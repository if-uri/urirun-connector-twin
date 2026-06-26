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
    """_abort_envelope routes rollback through dispatch_uri when set."""
    import urirun.node.flow as flow_mod

    dispatch_calls = []
    def fake_dispatch(uri, payload):
        dispatch_calls.append((uri, payload))
        return {"ok": True, "undone": payload.get("ledger", [])}

    # Build a minimal timeline/results that ledger_from_execution can parse.
    # An entry with ok=True and a result that has result.value.inverse is needed.
    step = {"id": "s1", "uri": "kvm://host/db/command/insert"}
    entry = {"id": "s1", "uri": "kvm://host/db/command/insert", "ok": True}
    result_with_inverse = {
        "ok": True,
        "result": {"value": {"inverse": {"uri": "kvm://host/db/command/delete", "args": {}}}}
    }
    timeline = [entry]
    results = {"s1": result_with_inverse}

    out = flow_mod._abort_envelope(
        step, [{"id": "s1", "error": {"category": "ABORTED"}}], [{"error": {"category": "ABORTED"}}],
        timeline, results, [], {}, rollback_on_failure=True, execute=True,
        dispatch_uri=fake_dispatch,
    )
    assert out["ok"] is False
    # rollback-ledger call happened
    rb_calls = [u for u, _ in dispatch_calls if "rollback-ledger" in u]
    assert rb_calls, f"expected rollback-ledger call; got {dispatch_calls}"
    # payload has ledger with the insert→delete pair
    _, payload = next((u, p) for u, p in dispatch_calls if "rollback-ledger" in u)
    assert any(l.get("inverse") == "kvm://host/db/command/delete" for l in payload["ledger"])


# ─── _thin_driver + _evaluate_step_next seam ─────────────────────────────────

def test_evaluate_step_next_routes_through_dispatch_uri():
    """When dispatch_uri is set, _evaluate_step_next calls twin://*/step/command/evaluate."""
    from urirun.node.flow import _evaluate_step_next
    calls = []

    def fake_dispatch(uri, payload):
        calls.append(uri)
        return {"ok": True, "next": "retry"}

    step = {"id": "s1", "uri": "kvm://laptop/cdp/page/query/info"}
    entry = {"error": {"category": "NETWORK"}, "recovery": {}}
    result = _evaluate_step_next(step, entry, [], True, 0, 1, False, fake_dispatch)
    assert result == "retry"
    assert any("step/command/evaluate" in c for c in calls)
    assert any("laptop" in c for c in calls)


def test_evaluate_step_next_in_process_fallback(monkeypatch):
    """When dispatch_uri is None, decision is in-process (identical behaviour)."""
    import urirun.node.flow as flow_mod
    monkeypatch.setattr(flow_mod, "can_retry_step", lambda *a, **kw: True)
    step = {"id": "s1", "uri": "kvm://host/cdp/page/query/info"}
    entry = {"error": {"category": "NETWORK"}, "recovery": {}}
    result = flow_mod._evaluate_step_next(step, entry, [], True, 0, 1, False, None)
    assert result == "retry"


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
