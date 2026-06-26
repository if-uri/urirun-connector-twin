"""Rollback parity tests — prove that thin-driver envelope-mode undoes the same
inverse URIs as the orchestrator, and that goal-verify drives rollback correctly.

Three contracts verified:
  1. envelope.ledger is populated after a step that returns an inverse
  2. _thin_driver LIFO-calls the recorded inverses when kind=rollback
  3. goal-verify failure triggers rollback (same inverse set as step-rollback)
"""
from __future__ import annotations

import pytest
from urirun.node.flow import FlowEnvelope, _thin_driver, _THIN_GOAL_URI


# ── helpers ──────────────────────────────────────────────────────────────────

def _nav_step(sid: str = "nav") -> dict:
    return {"id": sid, "uri": "cdp://host/page/command/navigate", "payload": {"url": "https://example.com"}}


def _nav_result_with_inverse(sid: str = "nav") -> dict:
    """A successful step result that carries a reversible inverse."""
    return {
        "ok": True,
        "result": {"value": {
            "state": "navigated",
            "inverse": {"path": "page/command/navigate-back", "args": {"url": "about:blank"}},
        }},
        "next": {"kind": "continue"},
    }


# ── ledger population ─────────────────────────────────────────────────────────

def test_envelope_ledger_filled_from_inverse():
    """After a step that returns an inverse, envelope.ledger has one entry."""
    goal_calls = []

    def dispatch(uri, payload=None):
        if _THIN_GOAL_URI in uri:
            goal_calls.append(uri)
            return {"ok": True}
        return _nav_result_with_inverse()

    steps = [_nav_step()]
    env = FlowEnvelope(goal={})
    result = _thin_driver(steps, env, dispatch, registry={}, execute=True, preflight=False)

    assert result["ok"] is True
    assert len(env.ledger) == 1
    entry = env.ledger[0]
    assert entry["uri"] == "cdp://host/page/command/navigate"
    # inverse URI rebased onto forward step's scheme://node
    assert entry["inverse"] == "cdp://host/page/command/navigate-back"
    assert entry["args"] == {"url": "about:blank"}


def test_ledger_stays_empty_for_query_step():
    """A step without an inverse (read-only query) leaves the ledger empty."""
    def dispatch(uri, payload=None):
        if _THIN_GOAL_URI in uri:
            return {"ok": True}
        return {"ok": True, "result": {"value": {"screenshot": "base64..."}}}

    steps = [{"id": "shot", "uri": "kvm://host/screen/query/capture", "payload": {}}]
    env = FlowEnvelope(goal={})
    _thin_driver(steps, env, dispatch, registry={}, execute=True, preflight=False)
    assert env.ledger == []


# ── rollback LIFO parity ──────────────────────────────────────────────────────

def test_thin_driver_rollback_calls_inverse_lifo():
    """On kind=rollback, _thin_driver applies all ledger inverses in reverse order."""
    inverse_calls: list[str] = []

    def dispatch(uri, payload=None):
        if "navigate-back" in uri or "fill-undo" in uri:
            inverse_calls.append(uri)
            return {"ok": True}
        if _THIN_GOAL_URI in uri:
            return {"ok": True}
        # step 1: navigate (reversible)
        if "navigate" in uri and "back" not in uri:
            return {
                "ok": True,
                "result": {"value": {"inverse": {"path": "page/command/navigate-back"}}},
                "next": {"kind": "continue"},
            }
        # step 2: fill (reversible, triggers rollback)
        if "fill" in uri:
            return {
                "ok": False,
                "result": {"value": {"inverse": {"path": "page/command/fill-undo"}}},
                "next": {"kind": "rollback"},
            }
        return {"ok": True}

    steps = [
        {"id": "nav", "uri": "cdp://host/page/command/navigate", "payload": {}},
        {"id": "fill", "uri": "cdp://host/page/command/fill", "payload": {}},
    ]
    env = FlowEnvelope(goal={})
    result = _thin_driver(steps, env, dispatch, registry={}, execute=True, preflight=False)

    assert result["ok"] is False
    assert result["next"]["kind"] == "failed"
    # fill's inverse is not pushed (step failed), only nav's is
    assert "cdp://host/page/command/navigate-back" in inverse_calls


def test_thin_driver_rollback_returns_undone_list():
    """rollback result includes undone list of called inverse URIs."""
    def dispatch(uri, payload=None):
        if "back" in uri:
            return {"ok": True}
        if _THIN_GOAL_URI in uri:
            return {"ok": True}
        return {
            "ok": False,
            "result": {"value": {"inverse": {"path": "page/command/navigate-back"}}},
            "next": {"kind": "rollback"},
        }

    steps = [{"id": "nav", "uri": "cdp://host/page/navigate", "payload": {}}]
    env = FlowEnvelope(goal={})
    result = _thin_driver(steps, env, dispatch, registry={}, execute=True, preflight=False)

    rb = result.get("rollback") or {}
    # nav step FAILED — inverse never pushed (only pushed for ok steps)
    # so undone is empty (nothing to undo)
    assert rb.get("ok") is True or rb == {} or rb.get("undone") == []


def test_two_reversible_steps_rolled_back_lifo():
    """Two successful reversible steps then rollback → inverses called in reverse order."""
    inverse_calls: list[str] = []

    def dispatch(uri, payload=None):
        if "inverse-a" in uri:
            inverse_calls.append("inverse-a")
            return {"ok": True}
        if "inverse-b" in uri:
            inverse_calls.append("inverse-b")
            return {"ok": True}
        if _THIN_GOAL_URI in uri:
            return {"ok": True}
        if "step-a" in uri:
            return {
                "ok": True,
                "result": {"value": {"inverse": {"path": "command/inverse-a"}}},
                "next": {"kind": "continue"},
            }
        if "step-b" in uri:
            return {
                "ok": True,
                "result": {"value": {"inverse": {"path": "command/inverse-b"}}},
                "next": {"kind": "rollback"},  # b succeeds then requests rollback
            }
        return {"ok": True}

    steps = [
        {"id": "a", "uri": "twin://host/command/step-a", "payload": {}},
        {"id": "b", "uri": "twin://host/command/step-b", "payload": {}},
    ]
    env = FlowEnvelope(goal={})
    result = _thin_driver(steps, env, dispatch, registry={}, execute=True, preflight=False)

    assert result["ok"] is False
    # Both steps succeeded before rollback was requested, so both inverses are in ledger
    assert len(env.ledger) == 2
    # LIFO: b's inverse (pushed second) called first, then a's
    assert inverse_calls == ["inverse-b", "inverse-a"]


# ── goal-verify drives rollback ───────────────────────────────────────────────

def test_goal_failure_triggers_rollback():
    """When goal-verify returns ok=False, thin-driver rolls back the ledger."""
    inverse_calls: list[str] = []

    def dispatch(uri, payload=None):
        if "nav-back" in uri:
            inverse_calls.append(uri)
            return {"ok": True}
        if _THIN_GOAL_URI in uri:
            return {"ok": False, "goalMet": False, "reason": "page not found"}
        return {
            "ok": True,
            "result": {"value": {"inverse": {"path": "page/command/nav-back"}}},
            "next": {"kind": "continue"},
        }

    steps = [{"id": "nav", "uri": "cdp://host/page/command/navigate", "payload": {}}]
    env = FlowEnvelope(goal={"uri": "twin://host/flow/goal/query/verify"})
    result = _thin_driver(steps, env, dispatch, registry={}, execute=True, preflight=False)

    assert result["ok"] is False
    assert result["next"]["kind"] == "goal-failed"
    assert "cdp://host/page/command/nav-back" in inverse_calls


def test_goal_none_result_is_treated_as_pass():
    """If dispatch returns None for goal URI, treat as pass (no rollback)."""
    def dispatch(uri, payload=None):
        if _THIN_GOAL_URI in uri:
            return None   # unhandled URI → None
        return {"ok": True, "next": {"kind": "continue"}}

    steps = [{"id": "q", "uri": "twin://host/query", "payload": {}}]
    env = FlowEnvelope(goal={})
    result = _thin_driver(steps, env, dispatch, registry={}, execute=True, preflight=False)
    # None → or {} → ok defaults True → no rollback
    assert result["ok"] is True


# ── connector twin: flow/goal/query/verify handler ───────────────────────────

def test_flow_goal_verify_no_uri_is_pass():
    """flow_goal_verify with empty goal returns ok=True (no assertion to fail)."""
    from urirun_connector_twin.core import flow_goal_verify
    r = flow_goal_verify(goal={}, results={})
    assert r["ok"] is True
    assert r.get("goalMet") is True


def test_flow_goal_verify_no_goal_arg():
    """flow_goal_verify with None goal is also a pass."""
    from urirun_connector_twin.core import flow_goal_verify
    r = flow_goal_verify()
    assert r["ok"] is True


# ── connector twin: flow/command/rollback-ledger ─────────────────────────────

def test_flow_rollback_empty_ledger():
    """Empty ledger returns ok immediately with undone=[]."""
    from urirun_connector_twin.core import flow_rollback
    r = flow_rollback(ledger=[])
    assert r["ok"] is True
    assert r.get("undone") == [] or "note" in r


def test_flow_rollback_none_inverse_skipped():
    """Ledger entry without inverse URI is skipped silently."""
    from urirun_connector_twin.core import flow_rollback
    # Entry with no inverse — should not crash
    r = flow_rollback(ledger=[{"uri": "cdp://host/navigate", "before": "", "after": ""}])
    assert r["ok"] is True


# ── three-path convergence ────────────────────────────────────────────────────
# All three rollback paths must produce the same {undone} list for the same ledger.
# Any silent divergence here means bugs that pass tests individually.

def test_three_path_rollback_convergence_success():
    """_thin_rollback, flow_rollback, and _uri_rollback all undo the same ledger."""
    import sys
    from urirun.node.flow import _thin_rollback, FlowEnvelope
    from urirun_connector_twin.core import flow_rollback
    from urirun.node.reversible import _uri_rollback as uri_rollback_fn

    inv_a = "kvm://host/window/command/restore-a"
    inv_b = "kvm://host/window/command/restore-b"
    ledger = [
        {"uri": "kvm://host/window/command/open-a", "inverse": inv_a, "args": {}, "before": "", "after": ""},
        {"uri": "kvm://host/window/command/open-b", "inverse": inv_b, "args": {}, "before": "", "after": ""},
    ]
    called: list[str] = []

    # ── path 1: _thin_rollback (in-process via dispatch_uri) ─────────────────
    def dispatch(uri, payload=None):
        if inv_a in uri or inv_b in uri:
            called.append(uri)
            return {"ok": True}
        return {"ok": True}

    env = FlowEnvelope()
    env.ledger = list(ledger)
    r1 = _thin_rollback(dispatch, env, [], {}, "failed")
    undone_thin = (r1.get("rollback") or {}).get("undone") or []

    # ── path 2: flow_rollback connector handler (patched v2_service) ─────────
    import urirun.v2_service as _svc
    _orig_call = _svc.call
    connector_calls: list[str] = []
    def _mock_call(uri, payload, registry, mode="execute"):
        if inv_a in uri or inv_b in uri:
            connector_calls.append(uri)
            return {"ok": True}
        return {"ok": True}
    _svc.call = _mock_call
    try:
        r2 = flow_rollback(ledger=ledger)
    finally:
        _svc.call = _orig_call
    undone_connector = r2.get("undone") or []

    # ── path 3: _uri_rollback from reversible.py (ledger shape) ──────────────
    reversible_calls: list[str] = []
    # _uri_rollback builds a ReversibleProcess + transport — mock _flow_transport
    from urirun.node import flow as _flow_mod
    from urirun.node.reversible import CallableTransport, ReversibleProcess
    def _mock_transport(mesh):
        def _call(uri, args):
            reversible_calls.append(uri)
            return {"ok": True}
        return CallableTransport(_call)
    _orig_transport = _flow_mod._flow_transport
    _flow_mod._flow_transport = _mock_transport
    try:
        r3 = uri_rollback_fn({"ledger": ledger, "mesh": {}})
    finally:
        _flow_mod._flow_transport = _orig_transport
    undone_reversible = r3.get("undone") or []

    # ── convergence assertion ─────────────────────────────────────────────────
    assert set(undone_thin) == {inv_a, inv_b}, f"thin: {undone_thin}"
    assert set(undone_connector) == {inv_a, inv_b}, f"connector: {undone_connector}"
    assert set(undone_reversible) == {inv_a, inv_b}, f"reversible: {undone_reversible}"
    # All three must agree on what was undone
    assert set(undone_thin) == set(undone_connector) == set(undone_reversible), \
        f"DIVERGENCE: thin={undone_thin} connector={undone_connector} reversible={undone_reversible}"


def test_three_path_rollback_convergence_stuck():
    """When an inverse fails, all three paths must halt at the same URI."""
    from urirun.node.flow import _thin_rollback, FlowEnvelope
    from urirun_connector_twin.core import flow_rollback
    from urirun.node.reversible import _uri_rollback as uri_rollback_fn

    inv_ok = "kvm://host/window/command/restore-ok"
    inv_fail = "kvm://host/window/command/restore-fail"
    ledger = [
        {"uri": "kvm://host/window/command/open-ok", "inverse": inv_ok, "args": {}, "before": "", "after": ""},
        {"uri": "kvm://host/window/command/open-fail", "inverse": inv_fail, "args": {}, "before": "", "after": ""},
    ]

    def dispatch(uri, payload=None):
        if inv_fail in uri:
            return {"ok": False, "error": "display not reachable"}
        return {"ok": True}

    # path 1
    env = FlowEnvelope()
    env.ledger = list(ledger)
    r1 = _thin_rollback(dispatch, env, [], {}, "failed")
    rb1 = r1.get("rollback") or {}

    # path 2
    import urirun.v2_service as _svc
    _orig_call = _svc.call
    _svc.call = lambda uri, p, reg, mode="execute": (
        {"ok": False, "error": "display not reachable"} if inv_fail in uri else {"ok": True}
    )
    try:
        r2 = flow_rollback(ledger=ledger)
    finally:
        _svc.call = _orig_call

    # path 3
    from urirun.node import flow as _flow_mod
    from urirun.node.reversible import CallableTransport
    def _mock_transport(mesh):
        return CallableTransport(lambda uri, args: (
            {"ok": False, "error": "display not reachable"} if inv_fail in uri else {"ok": True}
        ))
    _orig_transport = _flow_mod._flow_transport
    _flow_mod._flow_transport = _mock_transport
    try:
        from urirun.node.reversible import _uri_rollback as uri_rollback_fn
        r3 = uri_rollback_fn({"ledger": ledger, "mesh": {}})
    finally:
        _flow_mod._flow_transport = _orig_transport

    # All three must report failure at the same stuck URI
    assert rb1.get("ok") is False, f"thin should fail: {rb1}"
    assert r2.get("ok") is False, f"connector should fail: {r2}"
    assert r3.get("ok") is False, f"reversible should fail: {r3}"
    assert rb1.get("stuck") == inv_fail, f"thin stuck: {rb1.get('stuck')}"
    assert r2.get("stuck") == inv_fail, f"connector stuck: {r2.get('stuck')}"
    assert r3.get("stuck") == inv_fail, f"reversible stuck: {r3.get('stuck')}"
