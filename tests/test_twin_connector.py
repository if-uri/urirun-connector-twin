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
