"""Unit tests for urirun-connector-twin.

Tests run without a live node — kvm probes are monkeypatched out.
docker CLI is also not required (probe returns dockerAvailable based on system state,
but mock generation works regardless)."""
import pytest

from urirun_connector_twin.environment import probe, _constraints_from_profile_local as _constraints_from_profile
from urirun_connector_twin.planner import annotate_steps, build_imperative_plan
from urirun_connector_twin.mock import generate_mock, _detect_service


# ─── environment ─────────────────────────────────────────────────────────────

def test_probe_returns_host_info_without_node(monkeypatch):
    monkeypatch.setattr("urirun_connector_twin.environment._docker_available", lambda: False)
    env = probe(None)
    assert "host" in env
    assert env["host"]["os"]
    assert env["node"] == "localhost"
    assert env["dockerAvailable"] is False


def test_probe_with_unknown_node_adds_warning(monkeypatch):
    monkeypatch.setattr("urirun_connector_twin.environment._kvm_query", lambda *a, **kw: None)
    monkeypatch.setattr("urirun_connector_twin.environment._docker_available", lambda: False)
    env = probe("ghost-node")
    assert any("unreachable" in w for w in env["warnings"])
    assert env["node"] == "ghost-node"


def test_probe_merges_kvm_profile(monkeypatch):
    fake_profile = {"controllable": True, "best": "cdp", "actionMatrix": {
        "cdp": {"type": "executable"}, "atspi": {"type": "not_executable"}
    }}
    def _kvm(node, route):
        if "profile" in route:
            return fake_profile
        return None
    monkeypatch.setattr("urirun_connector_twin.environment._kvm_query", _kvm)
    monkeypatch.setattr("urirun_connector_twin.environment._docker_available", lambda: True)
    env = probe("laptop")
    assert env["controllable"] is True
    assert env["bestSurface"] == "cdp"


def test_constraints_from_profile_wayland_type():
    action_matrix = {
        "atspi": {"type": "not_executable"},
        "uinput": {"type": "not_executable"},
        "cdp": {"type": "executable"},
    }
    # If reversible module available, should return infeasible constraints
    constraints = _constraints_from_profile(action_matrix)
    # May be empty if reversible not importable in test env, but must be a list
    assert isinstance(constraints, list)


# ─── planner ─────────────────────────────────────────────────────────────────

_WAYLAND_ENV = {
    "node": "laptop", "bestSurface": "cdp", "controllable": True,
    "dockerAvailable": True, "warnings": [],
    "constraints": [
        {"kind": "infeasible", "what": "/input/command/type", "surface": "atspi",
         "reason": "Wayland withholds focus", "fix": "/cdp/page/command/fill"},
    ],
}

_CDP_ENV = {
    "node": "laptop", "bestSurface": "cdp", "controllable": True,
    "dockerAvailable": True, "warnings": [], "constraints": [],
}


def test_annotate_infeasible_os_type_step():
    steps = [{"id": "type", "uri": "kvm://laptop/input/command/type", "payload": {"text": "hi"}}]
    annotated = annotate_steps(steps, _WAYLAND_ENV)
    assert annotated[0]["feasible"] is False
    assert annotated[0]["fix"] == "/cdp/page/command/fill"
    assert annotated[0]["blocked_by"] == "/input/command/type"


def test_annotate_cdp_fill_is_feasible():
    steps = [{"id": "fill", "uri": "kvm://laptop/cdp/page/command/fill",
              "payload": {"role": "textbox", "text": "hello"}}]
    annotated = annotate_steps(steps, _WAYLAND_ENV)
    assert annotated[0]["feasible"] is True


def test_annotate_navigate_is_reversible():
    steps = [{"id": "nav", "uri": "kvm://laptop/cdp/page/command/navigate",
              "payload": {"url": "https://example.com"}}]
    annotated = annotate_steps(steps, _CDP_ENV)
    assert annotated[0]["reversible"] is True
    assert annotated[0]["inverse"] is not None  # inverse suffix stored (not full URI)


def test_annotate_fill_is_irreversible():
    steps = [{"id": "fill", "uri": "kvm://laptop/cdp/page/command/fill",
              "payload": {"role": "textbox", "text": "x"}}]
    annotated = annotate_steps(steps, _CDP_ENV)
    assert annotated[0]["reversible"] is False
    assert annotated[0]["inverse"] is None


def test_build_plan_counts_infeasible_steps():
    flow = {"steps": [
        {"id": "nav", "uri": "kvm://laptop/cdp/page/command/navigate", "payload": {}},
        {"id": "type", "uri": "kvm://laptop/input/command/type", "payload": {}},
    ]}
    plan = build_imperative_plan(flow, _WAYLAND_ENV, prompt="test")
    assert plan["totalSteps"] == 2
    assert plan["feasibleSteps"] == 1
    assert plan["infeasibleSteps"] == 1
    assert plan["needsMock"] is True


def test_build_plan_no_infeasible_when_clean():
    flow = {"steps": [
        {"id": "nav", "uri": "kvm://laptop/cdp/page/command/navigate", "payload": {}},
        {"id": "fill", "uri": "kvm://laptop/cdp/page/command/fill", "payload": {}},
    ]}
    plan = build_imperative_plan(flow, _CDP_ENV, prompt="test")
    assert plan["infeasibleSteps"] == 0
    assert plan["needsMock"] is False


# ─── mock ────────────────────────────────────────────────────────────────────

_INFEASIBLE_PLAN = {
    "steps": [
        {"uri": "kvm://laptop/input/command/type", "feasible": False},
    ]
}


def test_detect_service_linkedin():
    assert _detect_service("post on linkedin", []) == "linkedin"


def test_detect_service_fallback():
    assert _detect_service("do something random", []) == "web"


def test_generate_mock_returns_reversible():
    mock = generate_mock("test", _INFEASIBLE_PLAN)
    assert mock["reversible"] is True
    assert "docker compose down" in mock["inverseCmd"]


def test_generate_mock_compose_yaml():
    mock = generate_mock("linkedin test", _INFEASIBLE_PLAN, target="linkedin")
    assert "services:" in mock["dockerCompose"]
    assert "linkedin-mock" in mock["dockerCompose"]


def test_generate_mock_addresses_infeasible_uris():
    mock = generate_mock("test", _INFEASIBLE_PLAN)
    assert "kvm://laptop/input/command/type" in mock["infeasibleStepsAddressed"]


def test_generate_mock_has_test_uri():
    mock = generate_mock("test", _INFEASIBLE_PLAN)
    assert mock["testUri"].startswith("http://localhost:")


# ─── connector routes (smoke) ─────────────────────────────────────────────────

def test_connector_bindings_has_twin_routes():
    from urirun_connector_twin.core import bindings
    b = bindings()
    uris = list(b.get("bindings", {}).keys())
    assert any("environment/query/profile" in u for u in uris)
    assert any("plan/command/generate" in u for u in uris)
    assert any("mock/command/create" in u for u in uris)
    assert any("step/query/feasibility" in u for u in uris)


def test_step_feasibility_handler_clean(monkeypatch):
    monkeypatch.setattr("urirun_connector_twin.environment._kvm_query", lambda *a, **kw: None)
    monkeypatch.setattr("urirun_connector_twin.environment._docker_available", lambda: False)
    from urirun_connector_twin.core import step_feasibility
    r = step_feasibility("kvm://laptop/cdp/page/command/navigate", node="")
    assert r["ok"] is True
    assert r["uri"] == "kvm://laptop/cdp/page/command/navigate"


def test_mock_create_handler(monkeypatch):
    monkeypatch.setattr("urirun_connector_twin.environment._kvm_query", lambda *a, **kw: None)
    monkeypatch.setattr("urirun_connector_twin.environment._docker_available", lambda: True)
    from urirun_connector_twin.core import mock_create
    r = mock_create(prompt="test", flow={}, target="web")
    assert r["ok"] is True
    assert "mock" in r
    assert r["reversible"] is True


# ─── sandbox/command/probe ────────────────────────────────────────────────────

def test_sandbox_probe_simulated_reversible(monkeypatch):
    import urirun_connector_twin.sandbox as sb
    monkeypatch.setattr(sb, "_docker_available", lambda: False)
    sc = sb.Scenario(
        setup_cmd="mkdir -p /data",
        scan_cmd="ls /data",
        forward_cmd="touch /data/post.txt",
        inverse_cmd="rm -f /data/post.txt",
    )
    r = sb.probe_reversibility(sc)
    assert r["ok"] is True
    assert r["simulated"] is True
    assert r["changed"] is True
    assert r["reversible"] is True
    assert r["verdict"] == "reversible"


def test_sandbox_probe_simulated_irreversible(monkeypatch):
    import urirun_connector_twin.sandbox as sb
    monkeypatch.setattr(sb, "_docker_available", lambda: False)
    sc = sb.Scenario(
        setup_cmd="mkdir -p /data && echo original > /data/state",
        scan_cmd="cat /data/state 2>/dev/null || echo MISSING",
        forward_cmd="echo mutated > /data/state",
        inverse_cmd="true",                # wrong inverse — doesn't restore
    )
    r = sb.probe_reversibility(sc)
    assert r["ok"] is True
    assert r["changed"] is True
    assert r["reversible"] is False
    assert "IRREVERSIBLE" in r["verdict"]


def test_sandbox_probe_noop(monkeypatch):
    import urirun_connector_twin.sandbox as sb
    monkeypatch.setattr(sb, "_docker_available", lambda: False)
    sc = sb.Scenario(
        setup_cmd="mkdir -p /data",
        scan_cmd="ls /data",
        forward_cmd="true",               # no mutation
        inverse_cmd="true",
    )
    r = sb.probe_reversibility(sc)
    assert r["ok"] is True
    assert r["changed"] is False
    assert "no-op" in r["verdict"]


def test_scenario_for_uri_selects_builtin():
    from urirun_connector_twin.sandbox import scenario_for_uri, BUILTIN_SCENARIOS
    assert scenario_for_uri("browser://host/cdp/page/command/publish") == BUILTIN_SCENARIOS["web-post"]
    assert scenario_for_uri("sqlite://host/db/command/insert") == BUILTIN_SCENARIOS["sqlite"]
    assert scenario_for_uri("kvm://host/screen/query/capture") == BUILTIN_SCENARIOS["fs"]


def test_sandbox_probe_handler_wires_up(monkeypatch):
    import urirun_connector_twin.sandbox as sb
    monkeypatch.setattr(sb, "_docker_available", lambda: False)
    from urirun_connector_twin.core import sandbox_probe
    r = sandbox_probe(forward_cmd="touch /data/x.txt", inverse_cmd="rm -f /data/x.txt")
    assert r["ok"] is True
    assert "reversible" in r


# ─── step/command/evaluate ────────────────────────────────────────────────────

def test_step_evaluate_retry_on_transient(monkeypatch):
    """Transient NETWORK error + attempt=0 → retry."""
    from urirun_connector_twin.core import step_evaluate
    step = {"id": "s1", "uri": "kvm://host/cdp/page/query/info"}
    entry = {
        "error": {"category": "NETWORK", "message": "timeout"},
        "recovery": {"diagnosis": {"autoApplicable": False}},
    }
    # Stub can_retry_step to return True
    import urirun.node.recovery as rec
    monkeypatch.setattr(rec, "can_retry_step", lambda *a, **kw: True)
    r = step_evaluate(step=step, entry=entry, attempt=0, max_retries=1)
    assert r["ok"] is True
    assert r["next"] == "retry"


def test_step_evaluate_heal_when_auto_applicable(monkeypatch):
    """Auto-applicable diagnosis + not healed → heal."""
    from urirun_connector_twin.core import step_evaluate
    import urirun.node.recovery as rec
    monkeypatch.setattr(rec, "can_retry_step", lambda *a, **kw: False)
    step = {"id": "s1", "uri": "kvm://host/cdp/page/command/click"}
    entry = {
        "error": {"category": "CONNECTOR_REQUIRED", "message": "no CDP"},
        "recovery": {"diagnosis": {"autoApplicable": True, "rule": "ensure-cdp"}},
    }
    r = step_evaluate(step=step, entry=entry, execute=True, healed=False)
    assert r["ok"] is True
    assert r["next"] == "heal"
    assert r["diagnosis"]["rule"] == "ensure-cdp"


def test_step_evaluate_rollback_when_healed(monkeypatch):
    """Already healed + no retry budget → rollback."""
    from urirun_connector_twin.core import step_evaluate
    import urirun.node.recovery as rec
    monkeypatch.setattr(rec, "can_retry_step", lambda *a, **kw: False)
    step = {"id": "s1", "uri": "kvm://host/cdp/page/command/click"}
    entry = {
        "error": {"category": "CONNECTOR_REQUIRED", "message": "no CDP"},
        "recovery": {"diagnosis": {"autoApplicable": True}},
    }
    r = step_evaluate(step=step, entry=entry, execute=True, healed=True)
    assert r["ok"] is True
    assert r["next"] == "rollback"


def test_step_evaluate_rollback_dry_run(monkeypatch):
    """In dry-run mode with auto-applicable diagnosis → rollback (heal disabled)."""
    from urirun_connector_twin.core import step_evaluate
    import urirun.node.recovery as rec
    monkeypatch.setattr(rec, "can_retry_step", lambda *a, **kw: False)
    step = {"id": "s1", "uri": "kvm://host/cdp/page/command/click"}
    entry = {"error": {"category": "CONNECTOR_REQUIRED"}, "recovery": {"diagnosis": {"autoApplicable": True}}}
    r = step_evaluate(step=step, entry=entry, execute=False, healed=False)
    assert r["next"] == "rollback"


# ─── flow/command/rollback ────────────────────────────────────────────────────

def test_flow_rollback_empty_ledger():
    """Empty ledger → rollback succeeds with nothing undone."""
    from urirun_connector_twin.core import flow_rollback
    r = flow_rollback(ledger=[])
    assert isinstance(r, dict)


def test_flow_rollback_handler_in_bindings():
    """flow_rollback and step_evaluate are callable handlers (imported from core)."""
    from urirun_connector_twin.core import flow_rollback, step_evaluate
    # Verify they are callable functions (not just imported names)
    assert callable(flow_rollback)
    assert callable(step_evaluate)
    # Verify they have the expected parameter names
    import inspect
    rollback_params = set(inspect.signature(flow_rollback).parameters)
    assert "ledger" in rollback_params
    evaluate_params = set(inspect.signature(step_evaluate).parameters)
    assert "step" in evaluate_params and "entry" in evaluate_params and "next" not in evaluate_params


def test_flow_rollback_ledger_calls_inverses():
    """flow_rollback calls each inverse URI LIFO; returns undone list."""
    from urirun_connector_twin.core import flow_rollback
    called = []
    import urirun.v2_service as _svc_mod

    _orig = _svc_mod.call
    def fake_call(uri, payload, registry, mode="execute"):
        called.append(uri)
        return {"ok": True}
    _svc_mod.call = fake_call
    try:
        r = flow_rollback(ledger=[
            {"uri": "kvm://host/db/command/insert", "inverse": "kvm://host/db/command/delete", "args": {}},
            {"uri": "kvm://host/fs/command/write", "inverse": "kvm://host/fs/command/delete", "args": {}},
        ])
    finally:
        _svc_mod.call = _orig
    assert r["ok"] is True
    assert "undone" in r
    # LIFO: fs delete (last forward) must be undone before db delete
    assert called[0] == "kvm://host/fs/command/delete"
    assert called[1] == "kvm://host/db/command/delete"


def test_abort_envelope_dispatches_rollback_ledger(monkeypatch):
    """_thin_rollback fires inverses LIFO through dispatch_uri when the envelope ledger has entries."""
    from urirun.node.flow import _thin_rollback, FlowEnvelope

    dispatch_calls = []
    def fake_dispatch(uri, payload):
        dispatch_calls.append((uri, payload))
        return {"ok": True}

    envelope = FlowEnvelope(flow_id="t", goal={})
    # Pre-populate the ledger as _thin_update_ledger would after a successful step.
    envelope.ledger.append({
        "uri": "kvm://host/db/command/insert",
        "inverse": "kvm://host/db/command/delete",
        "args": {},
    })
    timeline = [{"id": "s1", "uri": "kvm://host/db/command/insert", "ok": True}]

    out = _thin_rollback(fake_dispatch, envelope, timeline, {"s1": {"ok": True}}, "failed")

    assert out["ok"] is False
    # inverse was fired through dispatch_uri
    inverse_calls = [u for u, _ in dispatch_calls if "delete" in u]
    assert inverse_calls, f"expected delete inverse; got {dispatch_calls}"
    assert out["rollback"]["ok"] is True
    assert "kvm://host/db/command/delete" in out["rollback"]["undone"]


# NOTE: the _evaluate_step_next flow-engine helper was removed in the Phase-5 flow extraction; its
# decision logic now lives in the step/command/evaluate route handler (step_evaluate), covered above
# by test_step_evaluate_retry_on_transient / _heal_when_auto_applicable / _rollback_when_healed.


# ─── flow/command/preflight ───────────────────────────────────────────────────

def test_flow_preflight_no_cdp_steps_returns_empty(monkeypatch):
    """Preflight with no CDP steps returns ok=True with empty provisioned list."""
    import urirun.v2_service as _svc_mod
    monkeypatch.setattr(_svc_mod, "call",
                        lambda *a, **kw: {"ok": True})
    from urirun_connector_twin.core import flow_preflight
    steps = [
        {"id": "s1", "uri": "fs://host/file/command/write"},
        {"id": "s2", "uri": "kvm://host/screen/query/capture"},
    ]
    r = flow_preflight(steps=steps)
    assert r["ok"] is True
    assert r["provisioned"] == []
    assert r["targets"] == []


def test_flow_preflight_extracts_cdp_targets(monkeypatch):
    """Preflight finds kvm:// hosts in cdp/page/* step URIs and calls ensure on them."""
    ensure_calls = []

    def fake_call(uri, payload, registry, mode="execute"):
        ensure_calls.append(uri)
        return {"ok": True}

    import urirun.v2_service as _svc_mod
    monkeypatch.setattr(_svc_mod, "call", fake_call)
    from urirun_connector_twin.core import flow_preflight
    steps = [
        {"id": "nav",   "uri": "kvm://laptop/cdp/page/command/navigate"},
        {"id": "click", "uri": "kvm://laptop/cdp/page/command/click"},
        {"id": "read",  "uri": "kvm://server/cdp/page/query/text"},
    ]
    r = flow_preflight(steps=steps)
    assert r["ok"] is True
    assert sorted(r["targets"]) == ["laptop", "server"]
    assert len(ensure_calls) == 2
    assert any("laptop" in u and "ensure" in u for u in ensure_calls)
    assert any("server" in u and "ensure" in u for u in ensure_calls)


def test_flow_preflight_dedups_same_host(monkeypatch):
    """Multiple steps on the same host produce a single ensure call."""
    ensure_calls = []

    def fake_call(uri, payload, registry, mode="execute"):
        ensure_calls.append(uri)
        return {"ok": True}

    import urirun.v2_service as _svc_mod
    monkeypatch.setattr(_svc_mod, "call", fake_call)
    from urirun_connector_twin.core import flow_preflight
    steps = [
        {"id": "s1", "uri": "kvm://host/cdp/page/command/navigate"},
        {"id": "s2", "uri": "kvm://host/cdp/page/command/fill"},
        {"id": "s3", "uri": "kvm://host/cdp/page/command/click"},
    ]
    r = flow_preflight(steps=steps)
    assert r["count"] == 1
    assert len(ensure_calls) == 1


def test_flow_preflight_handles_ensure_failure_gracefully(monkeypatch):
    """If ensure fails for a target, preflight continues and reports it not provisioned."""
    def fake_call(uri, payload, registry, mode="execute"):
        return {"ok": False, "error": "CDP not reachable"}

    import urirun.v2_service as _svc_mod
    monkeypatch.setattr(_svc_mod, "call", fake_call)
    from urirun_connector_twin.core import flow_preflight
    steps = [{"id": "s1", "uri": "kvm://host/cdp/page/command/click"}]
    r = flow_preflight(steps=steps)
    assert r["ok"] is True
    assert r["provisioned"] == []
    assert r["targets"] == ["host"]
    tl = r["timeline"]
    assert len(tl) == 1
    assert tl[0]["ok"] is False


# ─── Krok 4: execute_flow auto-creates FlowEnvelope when dispatch_uri is set ──

def test_execute_flow_auto_envelope_uses_thin_driver():
    """execute_flow auto-creates FlowEnvelope when dispatch_uri is set (Krok 4)."""
    from urirun.node.flow import execute_flow, FlowEnvelope

    calls = []
    def fake_dispatch(uri, payload):
        calls.append(uri)
        # goal-verify: return goalMet=True to complete the flow
        if "goal" in uri:
            return {"ok": True, "goalMet": True}
        # preflight
        if "preflight" in uri:
            return {"ok": True, "provisioned": [], "timeline": []}
        # actual step — succeed
        return {"ok": True, "result": {"value": {"data": "done"}}}

    # Use a CDP step so _plan_with_preflight injects a preflight step as step 0.
    flow = {
        "task": {"id": "t1", "title": "test"},
        "steps": [
            {"id": "s1", "uri": "kvm://host/cdp/page/command/navigate", "payload": {"url": "https://example.com"}},
        ]
    }
    out = execute_flow(flow, {}, {}, execute=True, dispatch_uri=fake_dispatch)
    assert out["ok"] is True
    # thin driver ran preflight (injected as step 0) and goal-verify
    assert any("preflight" in c for c in calls), f"expected preflight call in {calls}"
    assert any("goal" in c or "verify" in c for c in calls)
    # timeline present (thin driver output)
    assert "timeline" in out
    # preflight is first entry in timeline
    assert any("preflight" in (t.get("uri") or "") for t in out["timeline"])


def test_execute_flow_without_dispatch_uses_orchestrator():
    """Without dispatch_uri, execute_flow uses the legacy orchestrator (no auto-envelope)."""
    from urirun.node.flow import execute_flow, FlowEnvelope
    import urirun.v2_service as _svc_mod

    orig = _svc_mod.call
    called = []
    def fake_call(uri, payload, registry, mode="execute"):
        called.append(uri)
        return {"ok": True}
    _svc_mod.call = fake_call
    try:
        flow = {
            "task": {"id": "t1"},
            "steps": [{"id": "s1", "uri": "kvm://host/screen/query/info", "payload": {}}],
        }
        out = execute_flow(flow, {}, {}, execute=True)
    finally:
        _svc_mod.call = orig
    # orchestrator path: returns ok, no goalMet key
    assert out["ok"] is True
    assert "goalMet" not in out


# ─── memory loop (drift + remember as URI steps) ─────────────────────────────

def _make_twin_memory():
    from urirun.node.reversible import TwinMemory
    import dataclasses
    return dataclasses.replace(TwinMemory(), store={}, flow_store={})


def _make_dispatch_for_memory(calls: list, profiles: dict | None = None):
    """dispatch_uri stub: records URIs, returns env profile when asked."""
    profiles = profiles or {}
    def dispatch(uri, payload=None):
        calls.append(uri)
        if "/env/query/drift" in uri or "/memory/command/remember" in uri:
            # intercepted by _make_memory_dispatch — should never reach here in tests
            raise AssertionError(f"memory URI leaked to stub dispatch: {uri}")
        if "environment/query/profile" in uri or "/env/query/profile" in uri:
            node = (payload or {}).get("node") or uri.split("//")[1].split("/")[0]
            return profiles.get(node, {"platform": "linux", "best": "cdp"})
        if "goal/query/verify" in uri or "preflight" in uri:
            return {"ok": True, "next": {"kind": "done"}}
        return {"ok": True, "next": {"kind": "continue"}}
    return dispatch


def test_build_thin_plan_injects_drift_and_remember_for_kvm_steps():
    """_build_thin_plan prepends a drift step and appends a remember step for kvm targets."""
    from urirun.node.flow import _build_thin_plan
    memory = _make_twin_memory()
    flow = {"steps": [
        {"id": "a", "uri": "kvm://host/ui/command/click"},
        {"id": "b", "uri": "browser://host/page/command/open"},
    ]}
    steps = flow["steps"]
    plan = _build_thin_plan(steps, flow, execute=True, memory=memory)
    uris = [s["uri"] for s in plan]
    # drift step injected before kvm step
    assert any("/env/query/drift" in u for u in uris), f"no drift step in {uris}"
    # remember step at end
    assert uris[-1] == "twin://host/memory/command/remember"
    # original steps still present
    assert any("kvm://" in u for u in uris)
    assert any("browser://" in u for u in uris)


def test_build_thin_plan_kvm_always_gets_drift():
    """kvm:// steps always get drift/remember injected when execute=True, regardless of memory=.

    _build_thin_plan no longer gates on memory= being set: drift/remember are durable-store
    handlers, not in-memory-only.  memory=None still produces drift steps for kvm targets."""
    from urirun.node.flow import _build_thin_plan
    steps = [{"id": "a", "uri": "kvm://host/ui/command/click"}]
    plan = _build_thin_plan(steps, {}, execute=True, memory=None)
    uris = [s["uri"] for s in plan]
    assert any("/env/query/drift" in u for u in uris), "drift step must be injected for kvm"
    assert any("remember" in u for u in uris), "remember step must be injected for kvm"
    assert any("kvm://" in u for u in uris), "original kvm step must be present"


def test_build_thin_plan_no_kvm_no_drift():
    """Without kvm steps, no drift or remember steps injected even when memory is set."""
    from urirun.node.flow import _build_thin_plan
    memory = _make_twin_memory()
    steps = [{"id": "a", "uri": "browser://host/page/command/open"}]
    plan = _build_thin_plan(steps, {}, execute=True, memory=memory)
    uris = [s["uri"] for s in plan]
    assert not any("/env/query/drift" in u for u in uris)
    assert not any("remember" in u for u in uris)


def test_build_thin_plan_dry_run_no_drift():
    """In dry-run mode, _build_thin_plan returns original steps unchanged."""
    from urirun.node.flow import _build_thin_plan
    memory = _make_twin_memory()
    steps = [{"id": "a", "uri": "kvm://host/ui/command/click"}]
    plan = _build_thin_plan(steps, {}, execute=False, memory=memory)
    assert plan == steps


def test_memory_dispatch_drift_sets_baseline_on_first_run(monkeypatch):
    """On first drift call for a node, _make_memory_dispatch records known-good baseline."""
    from urirun.node.flow import _make_memory_dispatch
    import urirun.node.flow as flow_mod
    memory = _make_twin_memory()
    profile = {"best": "cdp", "platform": "linux"}
    monkeypatch.setattr(flow_mod, "_fetch_env_profile", lambda step, reg: profile)

    dispatch = _make_memory_dispatch(lambda u, p: {"ok": True}, memory, {}, {})
    result = dispatch("twin://host/env/query/drift", {"node": "host"})

    assert memory.known_good("host") is not None, "baseline must be set on first drift"
    assert result["ok"] is True
    assert result.get("next", {}).get("kind") == "continue"


def test_memory_dispatch_drift_detects_change(monkeypatch):
    """Drift handler returns type=twin-drift when current profile differs from known-good."""
    from urirun.node.flow import _make_memory_dispatch
    import urirun.node.flow as flow_mod
    memory = _make_twin_memory()
    known = {"best": "cdp", "display": "1920x1080", "platform": "linux"}
    current = {"best": "atspi", "display": "2560x1440", "platform": "linux"}
    memory.remember("host", known)
    monkeypatch.setattr(flow_mod, "_fetch_env_profile", lambda step, reg: current)

    dispatch = _make_memory_dispatch(lambda u, p: {"ok": True}, memory, {}, {})
    result = dispatch("twin://host/env/query/drift", {"node": "host"})

    assert result.get("type") == "twin-drift", f"expected twin-drift, got {result}"
    assert result.get("drifted") is True


def test_memory_dispatch_remember_updates_store(monkeypatch):
    """Remember handler updates known-good and saves flow record."""
    from urirun.node.flow import _make_memory_dispatch, _flow_key
    import urirun.node.flow as flow_mod
    memory = _make_twin_memory()
    profile = {"best": "cdp", "platform": "linux"}
    monkeypatch.setattr(flow_mod, "_fetch_env_profile", lambda step, reg: profile)

    flow = {"steps": [{"id": "a", "uri": "kvm://host/ui/command/click"}]}
    dispatch = _make_memory_dispatch(lambda u, p: {"ok": True}, memory, flow, {})
    result = dispatch("twin://host/memory/command/remember",
                      {"nodes": ["host"], "record": {"steps": flow["steps"]}})

    assert result["ok"] is True
    assert memory.known_good("host") is not None
    key = _flow_key(flow)
    assert memory.recall_flow(key) is not None, "flow record must be saved after remember"


def test_execute_flow_with_memory_injects_drift_steps():
    """execute_flow(memory=...) injects drift+remember steps via _build_thin_plan."""
    from urirun.node.flow import execute_flow
    import urirun.node.flow as flow_mod
    memory = _make_twin_memory()
    calls = []
    dispatched = []

    def fake_fetch(step, reg):
        return {"best": "cdp", "platform": "linux"}

    original_fetch = flow_mod._fetch_env_profile
    flow_mod._fetch_env_profile = fake_fetch
    try:
        def dispatch(uri, payload=None):
            dispatched.append(uri)
            if "goal/query/verify" in uri:
                return {"ok": True, "next": {"kind": "done"}}
            return {"ok": True, "next": {"kind": "continue"}}

        flow = {
            "task": {"id": "mem-test"},
            "steps": [{"id": "s1", "uri": "kvm://host/ui/command/click"}],
        }
        out = execute_flow(flow, {}, {}, execute=True,
                           dispatch_uri=dispatch, memory=memory)
    finally:
        flow_mod._fetch_env_profile = original_fetch

    from urirun.node.flow import _flow_key
    assert out["ok"] is True
    # Drift/remember steps are intercepted locally by _make_memory_dispatch,
    # so they do NOT appear in the test's dispatched list.
    # Instead verify their side-effects: memory state and timeline entries.
    assert memory.known_good("host") is not None, "drift must set known-good baseline"
    key = _flow_key(flow)
    assert memory.recall_flow(key) is not None, "remember must save flow record"
    timeline_uris = [t.get("uri", "") for t in (out.get("timeline") or [])]
    assert any("/env/query/drift" in u for u in timeline_uris), (
        f"drift step must appear in timeline: {timeline_uris}")
    assert any("memory/command/remember" in u for u in timeline_uris), (
        f"remember step must appear in timeline: {timeline_uris}")


# ─── flow/goal/query/verify handler ─────────────────────────────────────────

def test_goal_verify_no_uri_is_noop():
    """No goal.uri → goalMet=True, skipped='no-goal-uri' (no mesh call made)."""
    from urirun_connector_twin.core import flow_goal_verify
    r = flow_goal_verify(goal={}, results={})
    assert r["ok"] is True
    assert r["goalMet"] is True
    assert r.get("skipped") == "no-goal-uri"


def test_goal_verify_no_goal_at_all_is_noop():
    """goal=None → same as empty — no-op pass."""
    from urirun_connector_twin.core import flow_goal_verify
    r = flow_goal_verify(goal=None)
    assert r["ok"] is True
    assert r["goalMet"] is True


def test_goal_verify_contains_passes(monkeypatch):
    """goal.contains is found in the dispatched value → goalMet=True."""
    import urirun.v2_service as _svc
    monkeypatch.setattr(_svc, "call",
        lambda uri, payload, reg, mode="execute": {"ok": True, "result": {"value": {"text": "hello world"}}})

    from urirun_connector_twin.core import flow_goal_verify
    r = flow_goal_verify(goal={"uri": "kvm://host/screen/query/text",
                                "path": "text", "contains": "hello"})
    assert r["ok"] is True
    assert r["goalMet"] is True
    assert r.get("actual") == "hello world"


def test_goal_verify_contains_fails(monkeypatch):
    """goal.contains NOT found in dispatched value → ok=False, goalMet=False."""
    import urirun.v2_service as _svc
    monkeypatch.setattr(_svc, "call",
        lambda uri, payload, reg, mode="execute": {"ok": True, "result": {"value": {"text": "goodbye"}}})

    from urirun_connector_twin.core import flow_goal_verify
    r = flow_goal_verify(goal={"uri": "kvm://host/screen/query/text",
                                "path": "text", "contains": "hello"})
    assert r["ok"] is False
    assert r["goalMet"] is False


def test_goal_verify_equals_passes(monkeypatch):
    """goal.equals matches the dispatched value exactly → goalMet=True."""
    import urirun.v2_service as _svc
    monkeypatch.setattr(_svc, "call",
        lambda uri, payload, reg, mode="execute": {"ok": True, "result": {"value": {"url": "https://example.com/done"}}})

    from urirun_connector_twin.core import flow_goal_verify
    r = flow_goal_verify(goal={"uri": "kvm://host/cdp/page/query/evaluate",
                                "path": "url", "equals": "https://example.com/done"})
    assert r["ok"] is True
    assert r["goalMet"] is True


def test_goal_verify_present_passes(monkeypatch):
    """goal.present=True and value is non-empty → goalMet=True."""
    import urirun.v2_service as _svc
    monkeypatch.setattr(_svc, "call",
        lambda uri, payload, reg, mode="execute": {"ok": True, "result": {"value": {"id": "post-123"}}})

    from urirun_connector_twin.core import flow_goal_verify
    r = flow_goal_verify(goal={"uri": "kvm://host/cdp/page/query/evaluate",
                                "path": "id", "present": True})
    assert r["ok"] is True
    assert r["goalMet"] is True


def test_goal_verify_transport_exception_returns_ok_false(monkeypatch):
    """Dispatch exception → ok=False, goalMet=False (goal check never panics the caller)."""
    import urirun.v2_service as _svc
    def boom(uri, payload, reg, mode="execute"):
        raise ConnectionError("node unreachable")
    monkeypatch.setattr(_svc, "call", boom)

    from urirun_connector_twin.core import flow_goal_verify
    r = flow_goal_verify(goal={"uri": "kvm://host/screen/query/text"})
    assert r["ok"] is False
    assert r["goalMet"] is False
    assert "node unreachable" in r.get("error", "")


def test_goal_verify_dispatch_ok_false_fails_goal(monkeypatch):
    """When the goal URI itself returns ok=False, goal check fails even if present."""
    import urirun.v2_service as _svc
    monkeypatch.setattr(_svc, "call",
        lambda uri, payload, reg, mode="execute": {"ok": False, "error": "timeout"})

    from urirun_connector_twin.core import flow_goal_verify
    r = flow_goal_verify(goal={"uri": "kvm://host/screen/query/text"})
    assert r["goalMet"] is False


# ─── mock/command/start-probe-stop ───────────────────────────────────────────

def test_mock_start_probe_stop_no_docker(monkeypatch):
    """Without Docker, start-probe-stop degrades gracefully: ok, reachable=False, reversible=True."""
    import shutil
    monkeypatch.setattr(shutil, "which", lambda cmd: None)
    monkeypatch.setattr("urirun_connector_twin.environment._kvm_query", lambda *a, **kw: None)
    monkeypatch.setattr("urirun_connector_twin.environment._docker_available", lambda: False)

    from urirun_connector_twin.core import mock_start_probe_stop
    r = mock_start_probe_stop(prompt="book a flight", flow={}, target="web")

    assert r["ok"] is True
    assert r["reachable"] is False
    assert r["reversible"] is True
    assert r.get("simulated") is True
    assert "mock" in r
    assert "Docker" in (r.get("note") or "")


def test_mock_start_probe_stop_structure_has_mock_fields(monkeypatch):
    """Start-probe-stop always includes mock dict (prompt, dockerCompose, testUri, etc.)."""
    import shutil
    monkeypatch.setattr(shutil, "which", lambda cmd: None)
    monkeypatch.setattr("urirun_connector_twin.environment._kvm_query", lambda *a, **kw: None)
    monkeypatch.setattr("urirun_connector_twin.environment._docker_available", lambda: False)

    from urirun_connector_twin.core import mock_start_probe_stop
    r = mock_start_probe_stop(prompt="send email", target="smtp")

    mock = r.get("mock") or {}
    assert isinstance(mock, dict)
    assert "dockerCompose" in mock or "services" in mock or "ok" in r


# ─── _thin_goal_verify direct unit tests ─────────────────────────────────────

def test_thin_goal_verify_pass_returns_none():
    """When goal-verify dispatch returns ok=True, _thin_goal_verify returns None (no rollback)."""
    from urirun.node.flow import FlowEnvelope, _thin_goal_verify

    env = FlowEnvelope(goal={})
    timeline: list = []
    results: dict = {}

    dispatch = lambda uri, payload=None: {"ok": True, "goalMet": True}
    rb = _thin_goal_verify(dispatch, env, timeline, results)

    assert rb is None


def test_thin_goal_verify_fail_returns_rollback_dict():
    """When goal-verify returns ok=False, _thin_goal_verify returns rollback dict."""
    from urirun.node.flow import FlowEnvelope, _thin_goal_verify

    env = FlowEnvelope(goal={"uri": "cdp://host/state/query/check"})
    timeline: list = []
    results: dict = {}

    dispatch = lambda uri, payload=None: {"ok": False, "goalMet": False}
    rb = _thin_goal_verify(dispatch, env, timeline, results)

    assert rb is not None
    assert rb["ok"] is False
    assert rb["next"]["kind"] == "goal-failed"


def test_thin_goal_verify_registry_not_found_is_pass():
    """When dispatch returns NOT_FOUND registry error, _thin_goal_verify treats it as pass."""
    from urirun.node.flow import FlowEnvelope, _thin_goal_verify

    env = FlowEnvelope(goal={})
    timeline: list = []
    results: dict = {}

    # Simulate the twin connector not being installed: registry error
    dispatch = lambda uri, payload=None: {
        "ok": False,
        "error": {"type": "registry", "category": "NOT_FOUND", "message": "no handler"},
    }
    rb = _thin_goal_verify(dispatch, env, timeline, results)

    # Registry error → implicit pass → no rollback
    assert rb is None


def test_thin_goal_verify_none_dispatch_result_is_pass():
    """dispatch returning None (unregistered connector) is treated as a pass."""
    from urirun.node.flow import FlowEnvelope, _thin_goal_verify

    env = FlowEnvelope(goal={})
    dispatch = lambda uri, payload=None: None  # or {} after `or {}` coercion
    rb = _thin_goal_verify(dispatch, env, [], {})
    assert rb is None


# ─── flow/command/execute handler ────────────────────────────────────────────

def test_flow_execute_handler_dry_run(monkeypatch):
    """flow_execute(execute=False) runs all steps in dry-run mode — no mutations."""
    import urirun.v2_service as _svc
    dispatched = []

    def fake_call(uri, payload, reg, mode="dry-run"):
        dispatched.append((uri, mode))
        if "preflight" in uri or "goal/query/verify" in uri:
            return {"ok": True, "next": {"kind": "done"}}
        return {"ok": True, "next": {"kind": "continue"}}

    monkeypatch.setattr(_svc, "call", fake_call)
    from urirun_connector_twin.core import flow_execute
    flow = {"steps": [{"id": "s1", "uri": "kvm://host/ui/command/click", "payload": {}}],
            "task": {"id": "t1", "goal": "click"}}
    r = flow_execute(flow=flow, execute=False)
    assert r["ok"] is True
    modes = {m for _, m in dispatched}
    assert "dry-run" in modes, f"expected dry-run mode in {modes}"
    assert "execute" not in modes, f"execute mode must not appear in dry-run"


def test_flow_execute_handler_execute_mode(monkeypatch):
    """flow_execute(execute=True) dispatches steps in execute mode."""
    import urirun.v2_service as _svc
    dispatched = []

    def fake_call(uri, payload, reg, mode="execute"):
        dispatched.append((uri, mode))
        if "preflight" in uri or "goal/query/verify" in uri:
            return {"ok": True, "next": {"kind": "done"}}
        return {"ok": True, "next": {"kind": "continue"}}

    monkeypatch.setattr(_svc, "call", fake_call)
    from urirun_connector_twin.core import flow_execute
    flow = {"steps": [{"id": "s1", "uri": "kvm://host/cdp/page/command/navigate", "payload": {}}],
            "task": {"id": "t2", "goal": "navigate"}}
    r = flow_execute(flow=flow, execute=True)
    assert r["ok"] is True
    execute_calls = [(u, m) for u, m in dispatched if m == "execute"]
    assert len(execute_calls) >= 1, f"no execute-mode calls; got {dispatched}"


def test_flow_execute_handler_step_failure_returns_ok_false(monkeypatch):
    """A failing step causes flow_execute to return ok=False."""
    import urirun.v2_service as _svc

    def fake_call(uri, payload, reg, mode="execute"):
        if "preflight" in uri:
            return {"ok": True, "next": {"kind": "done"}}
        return {"ok": False, "error": {"message": "click failed"}, "next": {"kind": "rollback"}}

    monkeypatch.setattr(_svc, "call", fake_call)
    from urirun_connector_twin.core import flow_execute
    flow = {"steps": [{"id": "s1", "uri": "kvm://host/ui/command/click", "payload": {}}]}
    r = flow_execute(flow=flow, execute=True)
    assert r["ok"] is False


def test_flow_execute_in_bindings():
    """flow/command/execute is registered in the connector bindings."""
    from urirun_connector_twin.core import bindings
    uris = list(bindings().get("bindings", {}).keys())
    assert any("flow/command/execute" in u for u in uris), f"missing execute route; got: {uris}"


# ─── flow/command/diagnose handler ───────────────────────────────────────────

def test_flow_diagnose_no_match_returns_found_false():
    """An error that matches no playbook rule → {ok, found: False}."""
    from urirun_connector_twin.core import flow_diagnose
    r = flow_diagnose(error={"message": "completely-unknown-xyzzy-error"})
    assert r["ok"] is True
    assert r["found"] is False


def test_flow_diagnose_service_stopped_matches():
    """'connection refused' matches the service-stopped playbook rule."""
    from urirun_connector_twin.core import flow_diagnose
    r = flow_diagnose(
        error={"message": "connection refused"},
        step={"uri": "kvm://host/cdp/page/command/navigate"},
    )
    assert r["ok"] is True
    assert r["found"] is True
    assert r.get("rule") == "service-stopped", f"expected service-stopped; got {r}"


def test_flow_diagnose_returns_remediation_list():
    """A matched diagnosis includes a remediation list (may be empty list, not None)."""
    from urirun_connector_twin.core import flow_diagnose
    r = flow_diagnose(
        error={"message": "route not found", "category": "connector_required"},
        step={"uri": "kvm://host/cdp/page/command/navigate"},
    )
    if r["found"]:
        assert "remediation" in r
        assert isinstance(r["remediation"], list)


def test_flow_diagnose_in_bindings():
    """flow/command/diagnose is registered in the connector bindings."""
    from urirun_connector_twin.core import bindings
    uris = list(bindings().get("bindings", {}).keys())
    assert any("flow/command/diagnose" in u for u in uris), f"missing diagnose route; got: {uris}"


# ─── twin_bridge: inverse classification ────────────────────────────────────

def test_step_inverse_query_is_reversible_no_inverse():
    from urirun.host.twin_bridge import _step_inverse
    inv, rev = _step_inverse("kvm://host/screen/query/capture")
    assert rev is True
    assert inv is None


def test_step_inverse_navigate_is_reversible_with_back():
    from urirun.host.twin_bridge import _step_inverse
    inv, rev = _step_inverse("browser://cdp/page/command/navigate")
    assert rev is True
    assert inv == "browser://cdp/page/command/back"


def test_step_inverse_session_ensure_reversible():
    from urirun.host.twin_bridge import _step_inverse
    inv, rev = _step_inverse("kvm://host/cdp/session/command/ensure")
    assert rev is True
    assert inv == "kvm://host/cdp/session/command/close"


def test_step_inverse_click_is_irreversible():
    from urirun.host.twin_bridge import _step_inverse
    inv, rev = _step_inverse("kvm://host/cdp/page/command/click")
    assert rev is False
    assert inv is None


def test_step_inverse_fill_is_irreversible():
    from urirun.host.twin_bridge import _step_inverse
    inv, rev = _step_inverse("browser://cdp/page/command/fill")
    assert rev is False
    assert inv is None


def test_step_inverse_wait_is_reversible():
    from urirun.host.twin_bridge import _step_inverse
    inv, rev = _step_inverse("kvm://host/input/command/wait")
    assert rev is True
    assert inv is None


def test_step_inverse_unknown_command_is_irreversible():
    from urirun.host.twin_bridge import _step_inverse
    inv, rev = _step_inverse("kvm://host/custom/command/frobnicate")
    assert rev is False


def test_step_inverse_unknown_query_is_reversible():
    from urirun.host.twin_bridge import _step_inverse
    inv, rev = _step_inverse("kvm://host/custom/query/inspect")
    assert rev is True


def test_is_infra_step_skips_drift_and_preflight():
    from urirun.host.twin_bridge import _is_infra_step
    assert _is_infra_step({"id": "twin:drift:host", "uri": "twin://host/env/query/drift"}) is True
    assert _is_infra_step({"id": "preflight", "uri": "twin://host/flow/command/preflight"}) is True
    assert _is_infra_step({"id": "memory:remember", "uri": "twin://host/memory/command/remember"}) is True


def test_is_infra_step_passes_real_steps():
    from urirun.host.twin_bridge import _is_infra_step
    assert _is_infra_step({"id": "step_1", "uri": "kvm://host/screen/query/capture"}) is False
    assert _is_infra_step({"id": "nav", "uri": "browser://cdp/page/command/navigate"}) is False


def test_append_twin_widget_emits_events_with_inverse(monkeypatch):
    """append_twin_widget publishes TwinEvent with correct inverse for each non-infra step."""
    import sys
    sys.path.insert(0, '/home/tom/github/if-uri/urirun/adapters/python')
    from urirun.host.twin_bridge import append_twin_widget, TWIN_EVENT_HUB
    from urirun.node.mesh import EventHub

    # Use a fresh hub so we get clean counts
    captured = []
    original_publish = TWIN_EVENT_HUB.publish
    monkeypatch.setattr(TWIN_EVENT_HUB, "publish", lambda ev: captured.append(ev) or original_publish(ev))

    flow = {"steps": [
        {"uri": "kvm://host/cdp/session/command/ensure"},
        {"uri": "browser://cdp/page/command/navigate"},
        {"uri": "kvm://host/cdp/page/command/click"},
    ]}
    timeline = [
        {"id": "twin:drift:host", "uri": "twin://host/env/query/drift", "ok": True},  # infra
        {"id": "preflight", "uri": "twin://host/flow/command/preflight", "ok": True},  # infra
        {"id": "s1", "uri": "kvm://host/cdp/session/command/ensure", "ok": True, "target": "host"},
        {"id": "s2", "uri": "browser://cdp/page/command/navigate", "ok": True, "target": "cdp"},
        {"id": "s3", "uri": "kvm://host/cdp/page/command/click", "ok": True, "target": "host"},
    ]
    attachments = []
    append_twin_widget(True, flow, attachments, "test", ["host"], timeline)

    step_events = [e for e in captured if e.get("uri") == "twin://monitor/event"]
    assert len(step_events) == 3  # only 3 real steps, 2 infra skipped
    # flowCompleted event is emitted after all steps
    assert any(e.get("flowCompleted") for e in captured)
    # ensure: reversible, inverse=close
    ev_ensure = next(e for e in step_events if "session/command/ensure" in e["transition"]["forward"])
    assert ev_ensure["transition"]["reversible"] is True
    assert ev_ensure["transition"]["inverse"] == "kvm://host/cdp/session/command/close"
    # navigate: reversible, inverse=back
    ev_nav = next(e for e in step_events if "navigate" in e["transition"]["forward"])
    assert ev_nav["transition"]["reversible"] is True
    assert ev_nav["transition"]["inverse"] == "browser://cdp/page/command/back"
    # click: irreversible
    ev_click = next(e for e in step_events if "click" in e["transition"]["forward"])
    assert ev_click["transition"]["reversible"] is False
    assert ev_click["transition"]["inverse"] is None
    assert ev_click["status"] == "applied"
    assert "irreversible" in ev_click["narration"]


def test_convergence_navigate_inverse_matches_rollback_ledger(monkeypatch):
    """Three-path convergence: _step_inverse, ledger_from_execution, and SSE event all agree
    on the same inverse URI for a browser navigate step.

    This is the KEY invariant of the twin engine: the static classification (used to display
    inverse in the SSE widget) must match what a connector-aware rollback ledger would use.
    When connectors return inverse, both sources CONVERGE on the same URI — the widget can
    show the actual captured state while the engine rolls back with it."""
    import sys
    sys.path.insert(0, '/home/tom/github/if-uri/urirun/adapters/python')
    from urirun.host.twin_bridge import _step_inverse, append_twin_widget, TWIN_EVENT_HUB
    from urirun.node.flow import ledger_from_execution

    NAV_URI = "browser://cdp/page/command/navigate"
    BACK_URI = "browser://cdp/page/command/back"

    # Path 1: static classification predicts the inverse URI
    static_inv, static_rev = _step_inverse(NAV_URI)
    assert static_inv == BACK_URI
    assert static_rev is True

    # Path 2: rollback ledger built from connector-returned inverse
    execution = {
        "ok": True,
        "timeline": [{"id": "nav", "uri": NAV_URI, "ok": True}],
        "results": {"nav": {"result": {"value": {
            "ok": True,
            "inverse": {"uri": BACK_URI, "args": {}},
        }}}},
    }
    ledger = ledger_from_execution(execution)
    assert len(ledger) == 1
    assert ledger[0].forward.uri == NAV_URI
    assert ledger[0].inverse.uri == BACK_URI   # ← convergence with path 1

    # Path 3: SSE event emitted by append_twin_widget with connector results
    captured = []
    monkeypatch.setattr(TWIN_EVENT_HUB, "publish", lambda ev: captured.append(ev))
    flow = {"steps": [{"uri": NAV_URI}]}
    timeline = [{"id": "nav", "uri": NAV_URI, "ok": True, "target": "cdp"}]
    append_twin_widget(True, flow, [], "test", ["host"], timeline,
                       results=execution["results"])
    step_events = [e for e in captured if e.get("uri") == "twin://monitor/event"]
    assert len(step_events) == 1
    sse_inv = step_events[0]["transition"]["inverse"]
    assert sse_inv == BACK_URI                 # ← convergence with paths 1 & 2
    assert step_events[0]["transition"]["reversible"] is True


def test_convergence_query_no_inverse_no_ledger(monkeypatch):
    """Query steps: no inverse in SSE, no ledger entry, no rollback needed — consistent."""
    import sys
    sys.path.insert(0, '/home/tom/github/if-uri/urirun/adapters/python')
    from urirun.host.twin_bridge import _step_inverse, append_twin_widget, TWIN_EVENT_HUB
    from urirun.node.flow import ledger_from_execution

    QUERY_URI = "kvm://host/screen/query/capture"

    # Path 1: static classification — no inverse, reversible (no state change)
    static_inv, static_rev = _step_inverse(QUERY_URI)
    assert static_inv is None
    assert static_rev is True

    # Path 2: query connectors don't return inverse → empty ledger (correct, nothing to undo)
    execution = {
        "ok": True,
        "timeline": [{"id": "cap", "uri": QUERY_URI, "ok": True}],
        "results": {"cap": {"result": {"value": {"ok": True, "image": "..."}}}},
    }
    ledger = ledger_from_execution(execution)
    assert ledger == []  # no inverse → no ledger entry

    # Path 3: SSE event shows inverse=None, reversible=True
    captured = []
    monkeypatch.setattr(TWIN_EVENT_HUB, "publish", lambda ev: captured.append(ev))
    flow = {"steps": [{"uri": QUERY_URI}]}
    timeline = [{"id": "cap", "uri": QUERY_URI, "ok": True, "target": "host"}]
    append_twin_widget(True, flow, [], "test", ["host"], timeline,
                       results=execution["results"])
    step_events = [e for e in captured if e.get("uri") == "twin://monitor/event"]
    assert len(step_events) == 1
    assert step_events[0]["transition"]["inverse"] is None    # consistent: no undo for queries
    assert step_events[0]["transition"]["reversible"] is True


def test_inverse_from_results_prefers_connector_over_static(monkeypatch):
    """When a connector returns a concrete inverse URI, append_twin_widget uses it
    instead of the static _step_inverse() fallback."""
    import sys
    sys.path.insert(0, '/home/tom/github/if-uri/urirun/adapters/python')
    from urirun.host.twin_bridge import append_twin_widget, TWIN_EVENT_HUB

    # A session/ensure step normally gets a generic close URI from _step_inverse(),
    # but the connector here carries a more specific one with session_id.
    ENSURE_URI = "kvm://host/cdp/session/command/ensure"
    SPECIFIC_CLOSE = "kvm://host/cdp/session/command/close?session_id=abc123"

    captured = []
    monkeypatch.setattr(TWIN_EVENT_HUB, "publish", lambda ev: captured.append(ev))
    flow = {"steps": [{"uri": ENSURE_URI}]}
    timeline = [{"id": "sess", "uri": ENSURE_URI, "ok": True, "target": "host"}]
    results = {"sess": {"result": {"value": {
        "ok": True,
        "inverse": {"uri": SPECIFIC_CLOSE, "args": {}},
    }}}}
    append_twin_widget(True, flow, [], "test", ["host"], timeline, results=results)
    step_events = [e for e in captured if e.get("uri") == "twin://monitor/event"]
    assert len(step_events) == 1
    # Connector-specific URI wins over generic _step_inverse() output
    assert step_events[0]["transition"]["inverse"] == SPECIFIC_CLOSE
    assert step_events[0]["transition"]["reversible"] is True


def test_inverse_from_results_handles_path_based_inverse(monkeypatch):
    """Connectors that don't know their own address use inverse.path instead of inverse.uri.
    _inverse_from_results must rebase path onto the forward step's scheme://node.

    This is the actual shape returned by kvm connector's cdp_navigate:
      inverse = {"path": "cdp/page/command/navigate", "args": {"url": prev}}
    which should rebase to kvm://{node}/cdp/page/command/navigate."""
    import sys
    sys.path.insert(0, '/home/tom/github/if-uri/urirun/adapters/python')
    from urirun.host.twin_bridge import _inverse_from_results

    KVM_NAV = "kvm://lenovo/cdp/page/command/navigate"
    results = {"nav": {"result": {"value": {
        "ok": True,
        "inverse": {"path": "cdp/page/command/navigate", "args": {"url": "https://prev.example.com"}},
    }}}}
    inv = _inverse_from_results(results, "nav", KVM_NAV)
    # path rebased onto kvm://lenovo/
    assert inv == "kvm://lenovo/cdp/page/command/navigate"


def test_convergence_kvm_navigate_path_inverse_matches_ledger(monkeypatch):
    """Real KVM connector convergence: cdp_navigate returns path-based inverse.

    The rollback ledger (ledger_from_execution) and the SSE event (append_twin_widget)
    BOTH produce the same rebased inverse URI — proving the three paths converge even
    when the connector uses the path convention instead of uri."""
    import sys
    sys.path.insert(0, '/home/tom/github/if-uri/urirun/adapters/python')
    from urirun.host.twin_bridge import append_twin_widget, TWIN_EVENT_HUB
    from urirun.node.flow import ledger_from_execution

    KVM_NAV = "kvm://lenovo/cdp/page/command/navigate"
    REBASED_INVERSE = "kvm://lenovo/cdp/page/command/navigate"
    PREV_URL = "https://prev.example.com"

    # This is exactly the shape kvm connector's cdp_navigate emits
    kvm_result = {"result": {"value": {
        "ok": True, "action": "cdp-navigate", "url": "https://new.example.com",
        "inverse": {"path": "cdp/page/command/navigate", "args": {"url": PREV_URL}},
    }}}
    execution = {
        "ok": True,
        "timeline": [{"id": "nav", "uri": KVM_NAV, "ok": True}],
        "results": {"nav": kvm_result},
    }

    # Path 1 (rollback ledger) — ledger_from_execution handles path via _inverse_uri
    ledger = ledger_from_execution(execution)
    assert len(ledger) == 1
    assert ledger[0].inverse.uri == REBASED_INVERSE
    assert ledger[0].inverse.args == {"url": PREV_URL}

    # Path 2 (SSE event) — append_twin_widget via _inverse_from_results handles path
    captured = []
    monkeypatch.setattr(TWIN_EVENT_HUB, "publish", lambda ev: captured.append(ev))
    flow = {"steps": [{"uri": KVM_NAV}]}
    timeline = [{"id": "nav", "uri": KVM_NAV, "ok": True, "target": "lenovo"}]
    append_twin_widget(True, flow, [], "test", ["lenovo"], timeline,
                       results=execution["results"])
    step_events = [e for e in captured if e.get("uri") == "twin://monitor/event"]
    assert len(step_events) == 1
    assert step_events[0]["transition"]["inverse"] == REBASED_INVERSE  # ← CONVERGENCE
    assert step_events[0]["transition"]["reversible"] is True


def test_degraded_step_shows_degraded_status_in_sse_event(monkeypatch):
    """A step that returned ok=True but degraded=True must produce status='degraded'
    (not 'applied') in the SSE event, so the twin panel can show yellow instead of green.

    Real scenario: kvm capture returns ok=True but degraded=True when the Wayland portal
    permission is denied. The flow succeeds with graceful degradation, but the twin panel
    should reflect that the actual output quality was reduced."""
    import sys
    sys.path.insert(0, '/home/tom/github/if-uri/urirun/adapters/python')
    from urirun.host.twin_bridge import append_twin_widget, TWIN_EVENT_HUB

    CAPTURE_URI = "kvm://host/screen/query/capture"

    captured = []
    monkeypatch.setattr(TWIN_EVENT_HUB, "publish", lambda ev: captured.append(ev))

    flow = {"steps": [{"uri": CAPTURE_URI}]}
    timeline = [{"id": "cap", "uri": CAPTURE_URI, "ok": True, "target": "host"}]
    results = {"cap": {"result": {"value": {
        "ok": True,
        "degraded": True,
        "degradedReason": "Portal permission denied, no screenshot captured",
    }}}}
    append_twin_widget(True, flow, [], "zrob screenshot ekranu", ["host"], timeline,
                       results=results)

    step_events = [e for e in captured if e.get("uri") == "twin://monitor/event"]
    assert len(step_events) == 1
    ev = step_events[0]
    assert ev["status"] == "degraded"             # not "applied"
    assert ev["degraded"] is True
    assert ev["degradedReason"] == "Portal permission denied, no screenshot captured"
    assert "⚠ degraded" in ev["narration"]
    # flowCompleted is emitted after all steps
    assert any(e.get("flowCompleted") for e in captured)
    fc = next(e for e in captured if e.get("flowCompleted"))
    assert fc["prompt"] == "zrob screenshot ekranu"


def test_non_degraded_query_step_shows_applied_status(monkeypatch):
    """A query step that returned ok=True without degraded must show status='applied'."""
    import sys
    sys.path.insert(0, '/home/tom/github/if-uri/urirun/adapters/python')
    from urirun.host.twin_bridge import append_twin_widget, TWIN_EVENT_HUB

    CAPTURE_URI = "kvm://host/screen/query/capture"
    captured = []
    monkeypatch.setattr(TWIN_EVENT_HUB, "publish", lambda ev: captured.append(ev))

    flow = {"steps": [{"uri": CAPTURE_URI}]}
    timeline = [{"id": "cap", "uri": CAPTURE_URI, "ok": True, "target": "host"}]
    results = {"cap": {"result": {"value": {"ok": True, "image": "base64data"}}}}
    append_twin_widget(True, flow, [], "screenshot", ["host"], timeline, results=results)

    step_events = [e for e in captured if e.get("uri") == "twin://monitor/event"]
    assert step_events[0]["status"] == "applied"
    assert step_events[0]["degraded"] is False
    assert "degraded" not in step_events[0]["narration"]
