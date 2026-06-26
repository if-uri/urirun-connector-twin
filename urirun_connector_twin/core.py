"""twin:// connector — environment probe, imperative plan generation, Docker mock fallback.

Every external capability is a URI call (switchable via mesh):
  kvm://   → node environment + surface info
  twin://host/browser/query/sessions  → Chrome session list
  twin://host/browser/query/profile   → best session for a domain
  twin://host/constraints/query/from-profile → infeasible constraints from actionMatrix

Routes served:
  twin://host/environment/query/profile   — node capability snapshot (kvm + browser + OS)
  twin://host/constraints/query/from-profile — infeasible constraints from actionMatrix
  twin://host/browser/query/sessions      — list live Chrome sessions
  twin://host/browser/query/profile       — select best session for domain/task
  twin://host/plan/command/from-prompt    — NL prompt → annotated imperative plan
  twin://host/plan/command/generate       — flow + env → annotated imperative plan
  twin://host/mock/command/create         — Docker Compose mock for infeasible steps
  twin://host/step/query/feasibility      — per-step feasibility check
  twin://host/monitor/event               — SSE event marker
"""
from __future__ import annotations

import importlib.util
from typing import Any

import urirun

from .browser import discover_browser_sessions, select_session
from .dispatch import uri_call, value_of
from .environment import probe
from .mock import generate_mock
from .planner import annotate_steps, build_imperative_plan
from .prompt_plan import derive_task_target, plan_from_prompt
from .sandbox import Scenario, probe_reversibility, scenario_for_uri

CONNECTOR_ID = "twin"
conn = urirun.connector(CONNECTOR_ID, scheme="twin")


# ─── helpers ──────────────────────────────────────────────────────────────────

def _safe_import(module: str) -> Any:
    if importlib.util.find_spec(module) is None:
        return None
    try:
        return __import__(module, fromlist=[""])
    except Exception:
        return None


def _local_browser_profile(domain: str, needs_auth: bool) -> dict:
    sessions = discover_browser_sessions(probe_cookies=needs_auth)
    sel = select_session(sessions, domain, needs_auth)
    return {"ok": True, "selection": sel, "sessions": len(sessions)}


# ─── routes ───────────────────────────────────────────────────────────────────

@conn.handler("environment/query/profile", meta={"label": "Twin environment probe"})
def environment_profile(node: str = "", prompt: str = "") -> dict:
    """Collect a structured capability snapshot for the given node (or localhost)."""
    env = probe(node or None, prompt=prompt)
    return urirun.ok(**env)


@conn.handler("constraints/query/from-profile",
              meta={"label": "Infeasible constraints from actionMatrix"})
def constraints_from_profile(actionMatrix: dict) -> dict:
    """Derive per-action infeasibility constraints from a kvm actionMatrix.

    URI boundary between 'what surfaces exist' (kvm data) and 'which actions are
    blocked' (twin reasoning).  Switchable: replace this URI to swap constraint logic."""
    rev = _safe_import("urirun.node.reversible")
    if not rev:
        return urirun.ok(constraints=[])
    try:
        cs = rev._infeasible_constraints(actionMatrix or {})
    except Exception:
        cs = []
    return urirun.ok(constraints=cs)


@conn.handler("browser/query/sessions", meta={"label": "Enumerate live Chrome sessions"})
def browser_sessions(probe_cookies: bool = False) -> dict:
    """Enumerate debug-enabled Chrome/Chromium processes on this host.

    probe_cookies=True: reads Network.getAllCookies per session (slower, auth proof).
    probe_cookies=False: only checks /proc and /json (fast, no auth info)."""
    sessions = discover_browser_sessions(probe_cookies=probe_cookies)
    return urirun.ok(
        sessions=sessions,
        count=len(sessions),
        reachable=sum(1 for s in sessions if s.get("reachable")),
    )


@conn.handler("browser/query/profile", meta={"label": "Select best Chrome session for domain"})
def browser_profile(domain: str = "", prompt: str = "", probe_cookies: bool = True) -> dict:
    """Select the best live Chrome session for a domain or natural language task.

    Priority: auth cookie confirmed > tab on domain > real profile > any reachable > needs-login.
    Returns selection.mode: 'attach' (use this port) or 'needs-login' (human-gated)."""
    if not domain and prompt:
        t = derive_task_target(prompt)
        domain = t.get("domain") or ""
        needs_auth = t.get("needsAuth", False)
    else:
        needs_auth = bool(domain)
    sessions = discover_browser_sessions(probe_cookies=probe_cookies and bool(domain))
    sel = select_session(sessions, domain, needs_auth)
    return urirun.ok(
        domain=domain,
        selection=sel,
        sessions=len(sessions),
        reachable=sum(1 for s in sessions if s.get("reachable")),
    )


@conn.handler("plan/command/from-prompt", external=True,
              meta={"label": "Derive imperative plan from NL prompt"})
def plan_from_prompt_route(
    prompt: str,
    node: str = "",
    include_mock: bool = False,
    probe_browser: bool = True,
) -> dict:
    """Full twin loop from a single NL prompt.

    Calls twin://host/browser/query/profile via the mesh (switchable URI) with
    fallback to local browser.py scan.  If no logged-in Chrome exists for the
    target domain, plan.humanGated=True — NOT a silent failure."""
    _node = node or "host"
    target = derive_task_target(prompt)
    raw_plan = plan_from_prompt(prompt, node=_node)

    # ① Environment — URI first (remote node or local mesh), then in-process probe
    env_r = uri_call(
        f"twin://{_node}/environment/query/profile",
        {"node": node, "prompt": prompt},
        fallback=lambda: probe(node or None, prompt=prompt),
    )
    env = value_of(env_r) or env_r or probe(node or None, prompt=prompt)

    # ② Browser session — URI first (allows remote session discovery)
    browser_sel: dict = {}
    if probe_browser and target.get("domain"):
        r = uri_call(
            f"twin://{_node}/browser/query/profile",
            {"domain": target["domain"], "probe_cookies": True},
            fallback=lambda: _local_browser_profile(target["domain"],
                                                    target.get("needsAuth", False)),
        )
        browser_sel = (r or {}).get("selection") or {}
    plan = build_imperative_plan(raw_plan, env, prompt=prompt)
    if browser_sel:
        plan["browserSelection"] = browser_sel
        if browser_sel.get("mode") in ("needs-login", "none"):
            plan["needsMock"] = True
            plan["humanGated"] = True
            plan["blockedBy"] = "auth-required"
            plan["guidance"] = browser_sel.get("rationale") or browser_sel.get("reason")
    result: dict = {
        "ok": True,
        "prompt": prompt,
        "taskType": target.get("taskType"),
        "domain": target.get("domain"),
        "needsAuth": target.get("needsAuth"),
        "plan": plan,
        "environment": {
            "node": env.get("node"),
            "bestSurface": env.get("bestSurface"),
            "controllable": env.get("controllable"),
            "constraints": env.get("constraints") or [],
            "warnings": env.get("warnings") or [],
        },
    }
    if include_mock and plan.get("needsMock"):
        result["mock"] = generate_mock(prompt, plan, target=target.get("domain"))
    return result


@conn.handler("plan/command/generate", external=True,
              meta={"label": "Generate imperative plan from flow + environment"})
def plan_generate(
    flow: dict,
    prompt: str = "",
    node: str = "",
    include_mock: bool = False,
) -> dict:
    """Annotate a pre-built urirun flow with feasibility, reversibility and surface."""
    env = probe(node or None, prompt=prompt)
    plan = build_imperative_plan(flow, env, prompt=prompt)
    result: dict = {"ok": True, "plan": plan, "environment": env}
    if include_mock and plan.get("needsMock"):
        result["mock"] = generate_mock(prompt, plan)
    return result


@conn.handler("mock/command/create", external=True,
              meta={"label": "Generate Docker mock for unavailable target"})
def mock_create(prompt: str = "", flow: dict | None = None, target: str = "") -> dict:
    """Generate a reversible Docker Compose environment for testing infeasible steps."""
    env = probe(None, prompt=prompt)
    plan = build_imperative_plan(flow or {}, env, prompt=prompt)
    mock = generate_mock(prompt, plan, target=target or None)
    return urirun.ok(
        mock=mock, plan=plan, reversible=True,
        inverseCmd=mock.get("inverseCmd"), notes=mock.get("notes"),
    )


@conn.handler("step/query/feasibility", meta={"label": "Check URI step feasibility"})
def step_feasibility(uri: str, node: str = "", prompt: str = "") -> dict:
    """Check whether a single URI step is feasible on the current node."""
    env = probe(node or None, prompt=prompt)
    steps = annotate_steps([{"id": "check", "uri": uri, "payload": {}}], env)
    s = steps[0] if steps else {}
    return urirun.ok(
        uri=uri, node=env.get("node"),
        feasible=s.get("feasible", True), surface=s.get("surface"),
        reversible=s.get("reversible", False),
        blocked_by=s.get("blocked_by"), fix=s.get("fix"),
        constraints=env.get("constraints") or [],
        sessionSelection=env.get("sessionSelection"),
    )


@conn.handler("sandbox/command/probe", isolated=True,
              meta={"label": "Prove reversibility in a disposable Docker sandbox"})
def sandbox_probe(
    image: str = "alpine:3",
    scan_cmd: str = "ls /data 2>/dev/null || echo EMPTY",
    forward_cmd: str = "true",
    inverse_cmd: str = "true",
    setup_cmd: str = "mkdir -p /data",
    uri: str = "",
) -> dict:
    """Run scan(before) → forward → scan(after) → inverse → scan(restored).

    reversible := before == restored  AND  before != after.

    When `uri` is given and no explicit cmds are set, auto-selects a built-in scenario
    for that URI's scheme (fs / sqlite / web-post family).  Falls back to temp-dir
    simulation when Docker is absent — clearly marked simulated:True.

    Returns a hard `reversible` datum the imperative planner was missing for
    `reversible='unknown'` steps — so the plan can block, allow, or gate on it
    without touching the real machine first."""
    if uri and forward_cmd == "true":
        sc = scenario_for_uri(uri)
    else:
        sc = Scenario(image=image, scan_cmd=scan_cmd, forward_cmd=forward_cmd,
                      inverse_cmd=inverse_cmd, setup_cmd=setup_cmd)
    return probe_reversibility(sc)


@conn.handler("flow/command/preflight",
              meta={"label": "Provision required surfaces before flow execution"})
def flow_preflight(steps: list | None = None, node: str = "") -> dict:
    """Identify which surfaces the flow steps need and provision them up-front.

    For CDP-dependent steps: if CDP is feasible but not reachable on the target
    node, bring it up now so the first `cdp/page/*` step doesn't hit a
    fail-then-self-heal roundtrip.  Idempotent — `ensure` reuses an existing session.

    Returns {ok, timeline: [{id, uri, ok, action, target}], provisioned: [target…]}."""
    import urirun.v2_service as _svc
    steps = steps or []
    timeline: list[dict] = []
    provisioned: list[str] = []
    cdp_targets: list[str] = sorted({
        _target_of(str(s.get("uri") or ""))
        for s in steps
        if "/cdp/page/" in str(s.get("uri") or "")
    } - {""})
    for target in cdp_targets:
        ensure_uri = f"kvm://{target}/cdp/session/command/ensure"
        try:
            env = _svc.call(ensure_uri, {}, {}, mode="execute")
            ok = bool(env.get("ok"))
        except Exception:
            ok = False
        timeline.append({"id": f"preflight:cdp:{target}", "uri": ensure_uri,
                         "target": target, "ok": ok, "action": "provision-surface",
                         "type": "preflight"})
        if ok:
            provisioned.append(target)
    return urirun.ok(timeline=timeline, provisioned=provisioned,
                     targets=cdp_targets, count=len(cdp_targets))


def _target_of(uri: str) -> str:
    """Extract node/host from a URI string (the authority component)."""
    try:
        rest = uri.split("://", 1)[1]
        return rest.split("/")[0]
    except (IndexError, AttributeError):
        return ""


@conn.handler("flow/command/rollback-ledger",
              meta={"label": "Roll back reversible mutations from ledger"})
def flow_rollback(ledger: list | None = None) -> dict:
    """Undo reversible mutations recorded in the ledger.

    Named rollback-ledger (not rollback) to avoid shadowing the
    urirun.node.reversible handler at the same path — that one takes
    {execution} while this simplified form takes {ledger: [...]}.
    Returns {ok, undone, skipped}."""
    import urirun.v2_service as _svc
    from urirun.node.reversible import CallableTransport, rollback_partial_flow
    ledger = ledger or []
    # Build a minimal timeline/results stub so rollback_partial_flow can find inverses.
    # Each ledger entry is {uri, inverse, before, after}.
    timeline = [
        {"id": f"step:{i}", "uri": e["uri"], "ok": True,
         "inverse": e.get("inverse"), "before": e.get("before"), "after": e.get("after")}
        for i, e in enumerate(ledger)
    ]
    results: dict = {}
    try:
        transport = CallableTransport(
            lambda uri, payload: _svc.call(uri, payload, {}, mode="execute")
        )
        rb = rollback_partial_flow(timeline, results, transport)
    except Exception as exc:
        return {"ok": False, "error": str(exc), "undone": [], "skipped": len(ledger)}
    return rb or {"ok": True, "undone": [], "skipped": len(ledger)}


@conn.handler("step/command/evaluate",
              meta={"label": "Decide next action after a failed step: retry | heal | rollback"})
def step_evaluate(
    step: dict,
    entry: dict,
    routes: list | None = None,
    execute: bool = True,
    attempt: int = 0,
    max_retries: int = 1,
    healed: bool = False,
) -> dict:
    """Retry/heal/rollback decision for a single failed flow step.

    Makes the decision observable and switchable: callers replace this URI
    to inject different retry policies without touching flow.py.

    Priority order:
      1. retry  — transient error + within budget + query-kind route
      2. heal   — auto-applicable diagnosis + execute mode + not yet healed
      3. rollback — give up, let caller undo reversible mutations
    """
    from urirun.node.recovery import can_retry_step

    routes = routes or []
    error = entry.get("error") or {}

    if can_retry_step(error, step=step, routes=routes, execute=execute,
                      attempt=attempt, max_retries=max_retries):
        return urirun.ok(next="retry", reason=error.get("category"))

    if execute and not healed:
        diagnosis = (entry.get("recovery") or {}).get("diagnosis") or {}
        if diagnosis.get("autoApplicable"):
            return urirun.ok(next="heal", diagnosis=diagnosis)

    return urirun.ok(next="rollback", reason=error.get("category"))


@conn.handler("monitor/event", meta={"label": "Twin monitor SSE event marker"})
def monitor_event(node: str = "", stateSig: str = "", narration: str = "") -> dict:
    """Receive a twin state-transition event (distributed to /events?scheme=twin SSE)."""
    return urirun.ok(node=node, stateSig=stateSig, narration=narration, received=True)


def bindings() -> dict:
    return conn.bindings()


def manifest() -> dict:
    return conn.manifest(urirun.load_manifest(__package__))


def main(argv: list[str] | None = None) -> int:
    return conn.cli(argv, manifest_prose=urirun.load_manifest(__package__))


if __name__ == "__main__":
    import sys
    sys.exit(main())
