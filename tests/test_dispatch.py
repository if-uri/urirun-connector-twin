"""Tests for dispatch.py — URI-as-internal-bus switching layer with transport injection."""
from __future__ import annotations

import pytest
import urirun_connector_twin.dispatch as _d


# ─── helpers ────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def clean_transport():
    _d._transport_fn = None
    yield
    _d._transport_fn = None


# ─── basic dispatch.py behaviour ────────────────────────────────────────────

def test_uri_call_fallback_triggers_on_no_mesh():
    """When no mesh/transport, falls through to in-process fallback."""
    result = _d.uri_call("twin://host/not-a-real-route", {}, fallback=lambda: {"ok": True, "x": 9})
    assert result == {"ok": True, "x": 9}


def test_uri_call_fallback_none_returns_none():
    assert _d.uri_call("twin://host/missing", {}) is None


def test_value_of_extracts_value_key():
    assert _d.value_of({"ok": True, "value": {"a": 1}}) == {"a": 1}


def test_value_of_extracts_nested_result_value():
    assert _d.value_of({"result": {"value": {"b": 2}}}) == {"b": 2}


def test_value_of_none_input():
    assert _d.value_of(None) is None


def test_value_of_no_value_key():
    assert _d.value_of({"ok": True, "data": 1}) is None


# ─── transport injection ─────────────────────────────────────────────────────

def test_transport_is_called_first():
    """set_transport() makes the injected fn the primary dispatch path."""
    called = []

    def fake(uri, payload):
        called.append(uri)
        return {"ok": True, "result": {"value": {"source": "transport"}}}

    _d.set_transport(fake)
    result = _d.uri_call("twin://host/environment/query/profile", {})
    assert called == ["twin://host/environment/query/profile"]
    assert result is not None


def test_transport_result_not_ok_falls_to_fallback():
    """If transport returns ok=False, dispatch continues to v2_service / fallback."""
    _d.set_transport(lambda u, p: {"ok": False, "error": "not found"})
    sentinel = {"ok": True, "sentinel": True}
    result = _d.uri_call("twin://host/x", {}, fallback=lambda: sentinel)
    assert result == sentinel


def test_transport_exception_falls_to_fallback():
    """Transport exceptions are swallowed and dispatch falls through."""
    _d.set_transport(lambda u, p: (_ for _ in ()).throw(RuntimeError("bang")))
    sentinel = {"fallback": True}
    result = _d.uri_call("twin://host/x", {}, fallback=lambda: sentinel)
    assert result == sentinel


def test_set_transport_none_clears():
    """Passing None clears the transport."""
    _d.set_transport(lambda u, p: {"ok": True})
    _d.set_transport(None)
    assert _d._transport_fn is None
    # Without transport, should return None (no v2_service, no fallback)
    assert _d.uri_call("twin://host/x") is None


# ─── plan_from_prompt_route routes through URI dispatch ──────────────────────

def test_plan_from_prompt_route_calls_environment_uri():
    """plan_from_prompt_route calls twin://host/environment/... via uri_call."""
    transport_calls = []

    def fake(uri, payload):
        transport_calls.append(uri)
        if "environment" in uri:
            return {"ok": True, "host": "laptop", "node": None,
                    "bestSurface": "cdp", "controllable": True,
                    "constraints": [], "warnings": [], "docker": True,
                    "sessionSelection": {}}
        if "browser" in uri:
            return {"ok": True, "selection": {"mode": "no-chrome"}}
        return {"ok": True}

    _d.set_transport(fake)
    from urirun_connector_twin.core import plan_from_prompt_route
    r = plan_from_prompt_route("take a screenshot", node="laptop", probe_browser=False)
    assert r["ok"] is True
    env_calls = [u for u in transport_calls if "environment" in u]
    assert len(env_calls) >= 1, f"environment URI not called; got: {transport_calls}"


def test_plan_from_prompt_route_calls_browser_uri_when_domain():
    """When prompt has a domain, plan_from_prompt_route calls browser/query/profile URI."""
    transport_calls = []

    def fake(uri, payload):
        transport_calls.append(uri)
        if "environment" in uri:
            return {"ok": True, "host": "laptop", "node": None,
                    "bestSurface": "cdp", "controllable": True,
                    "constraints": [], "warnings": [], "docker": True,
                    "sessionSelection": {}}
        if "browser" in uri:
            return {"ok": True, "selection": {"mode": "no-chrome"}}
        return {"ok": True}

    _d.set_transport(fake)
    from urirun_connector_twin.core import plan_from_prompt_route
    r = plan_from_prompt_route("post on linkedin", node="laptop", probe_browser=True)
    assert r["ok"] is True
    browser_calls = [u for u in transport_calls if "browser" in u]
    assert len(browser_calls) >= 1, f"browser URI not called; got: {transport_calls}"


def test_plan_from_prompt_route_fallback_when_no_transport():
    """Without transport, plan_from_prompt_route still works via in-process fallback."""
    from urirun_connector_twin.core import plan_from_prompt_route
    r = plan_from_prompt_route("take a screenshot", node="", probe_browser=False)
    assert r["ok"] is True
    assert "plan" in r


def test_plan_from_prompt_route_calls_annotate_uri():
    """plan_from_prompt_route calls twin://host/plan/command/annotate via uri_call (step ③)."""
    transport_calls = []

    def fake(uri, payload):
        transport_calls.append(uri)
        if "environment" in uri:
            return {"ok": True, "node": "laptop", "bestSurface": "cdp",
                    "controllable": True, "constraints": [], "warnings": [],
                    "dockerAvailable": True, "sessionSelection": {}}
        if "plan/command/annotate" in uri:
            flow = payload.get("flow") or {}
            env  = payload.get("env") or {}
            from urirun_connector_twin.planner import build_imperative_plan
            plan = build_imperative_plan(flow, env, prompt=payload.get("prompt", ""))
            return {"ok": True, "plan": plan}
        return {"ok": True}

    _d.set_transport(fake)
    from urirun_connector_twin.core import plan_from_prompt_route
    r = plan_from_prompt_route("take a screenshot", node="laptop", probe_browser=False)
    assert r["ok"] is True
    annotate_calls = [u for u in transport_calls if "plan/command/annotate" in u]
    assert len(annotate_calls) == 1, f"annotate URI not called; got: {transport_calls}"


def test_plan_annotate_handler_returns_plan():
    """plan_annotate handler wraps build_imperative_plan and returns {ok, plan}."""
    from urirun_connector_twin.core import plan_annotate
    env = {"node": "laptop", "bestSurface": "cdp", "controllable": True,
           "dockerAvailable": True, "constraints": [], "warnings": []}
    flow = {"steps": [
        {"id": "nav", "uri": "kvm://laptop/cdp/page/command/navigate", "payload": {}},
    ]}
    r = plan_annotate(flow=flow, env=env, prompt="test")
    assert r["ok"] is True
    assert "plan" in r
    plan = r["plan"]
    assert plan["totalSteps"] == 1
    assert plan["feasibleSteps"] == 1


def test_all_three_from_prompt_steps_use_uri():
    """Prove ①②③ are all switchable: replace all three transport responses.

    When a transport provides all three URIs, plan_from_prompt_route must return
    whatever the transport put in 'plan' — no in-process fallback is taken."""
    injected_plan = {"steps": [{"id": "stub", "uri": "test://host/x", "feasible": True}],
                     "totalSteps": 1, "feasibleSteps": 1, "infeasibleSteps": 0,
                     "irreversibleSteps": 0, "needsMock": False, "node": "remote",
                     "environment": {}, "prompt": "via-transport"}

    def fake(uri, payload):
        if "environment" in uri:
            return {"ok": True, "node": "remote", "bestSurface": "cdp",
                    "controllable": True, "constraints": [], "warnings": [],
                    "dockerAvailable": True, "sessionSelection": {}}
        if "plan/command/annotate" in uri:
            return {"ok": True, "plan": injected_plan}
        return {"ok": True}

    _d.set_transport(fake)
    from urirun_connector_twin.core import plan_from_prompt_route
    r = plan_from_prompt_route("test task", node="remote", probe_browser=False)
    assert r["ok"] is True
    assert r["plan"] is injected_plan, "plan must come from transport, not in-process fallback"

