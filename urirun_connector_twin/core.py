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
  twin://host/experience/query/retrieve   — propose-stage memory/route candidates
  twin://host/plan/command/from-prompt    — NL prompt → annotated imperative plan
  twin://host/plan/command/annotate       — flow + env → annotated plan (switchable logic)
  twin://host/plan/command/generate       — flow + node → probe env then annotate
  twin://host/mock/command/create         — Docker Compose mock for infeasible steps
  twin://host/step/query/feasibility      — per-step feasibility check
  twin://host/proof/query/check           — proof cache hit? (uri, scenario, env proven reversible)
  twin://host/proof/command/record        — record a positive reversibility proof
  twin://host/proof/command/gate          — reversibility gate: skip / probe-then-record / block
  twin://host/monitor/event               — SSE event marker
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

import urirun

from .browser import discover_browser_sessions, select_session
from .dispatch import uri_call, value_of
from .environment import probe
from .mock import generate_mock
from .planner import annotate_steps, build_imperative_plan
from .prompt_plan import derive_task_target, plan_from_prompt
from .sandbox import Scenario, probe_reversibility, scenario_for_uri
from .proof_cache import preflight_step, proof_check, proof_key, proof_record

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


def _apply_browser_sel(plan: dict, browser_sel: dict) -> None:
    """Merge browser session selection into plan (mutates in place)."""
    plan["browserSelection"] = browser_sel
    if browser_sel.get("mode") in ("needs-login", "none"):
        plan["needsMock"] = True
        plan["humanGated"] = True
        plan["blockedBy"] = "auth-required"
        plan["guidance"] = browser_sel.get("rationale") or browser_sel.get("reason")


def _prompt_result(prompt: str, target: dict, plan: dict, env: dict,
                   include_mock: bool) -> dict:
    """Build the final result dict for plan_from_prompt_route."""
    result: dict = {
        "ok": True, "prompt": prompt,
        "taskType": target.get("taskType"),
        "domain": target.get("domain"),
        "needsAuth": target.get("needsAuth"),
        "plan": plan,
        "environment": {
            "node": env.get("node"), "bestSurface": env.get("bestSurface"),
            "controllable": env.get("controllable"),
            "constraints": env.get("constraints") or [],
            "warnings": env.get("warnings") or [],
        },
    }
    if include_mock and plan.get("needsMock"):
        result["mock"] = generate_mock(prompt, plan, target=target.get("domain"))
    return result


# ─── routes ───────────────────────────────────────────────────────────────────

@conn.handler("environment/query/profile", meta={"label": "Twin environment probe"})
def environment_profile(node: str = "", prompt: str = "") -> dict:
    """Collect a structured capability snapshot for the given node (or localhost)."""
    env = probe(node or None, prompt=prompt)
    return urirun.ok(**env)


def _inv_run(cmd: list[str], timeout: float = 4.0) -> str:
    import subprocess
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout if r.returncode == 0 else ""
    except Exception:  # noqa: BLE001 — a missing tool / denied probe is a normal empty inventory
        return ""


def _inventory_displays() -> list[dict]:
    import os, re, shutil  # noqa: E401
    if not (shutil.which("xrandr") and os.environ.get("DISPLAY")):
        return []  # Wayland / headless: no portable read-only enumerator → empty (degrade, not guess)
    out = []
    for line in _inv_run(["xrandr", "--query"]).splitlines():
        if " connected" in line:
            m = re.search(r"(\d+x\d+)\+\d+\+\d+", line)
            out.append({"id": line.split()[0], "label": line.split()[0], "kind": "display",
                        "resolution": m.group(1) if m else None,
                        "primary": " primary " in f" {line} "})
    return out


def _inventory_audio_sinks() -> list[dict]:
    import shutil
    if not shutil.which("pactl"):
        return []
    out = []
    for line in _inv_run(["pactl", "list", "short", "sinks"]).splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and parts[0].strip():
            out.append({"id": parts[0].strip(), "label": parts[1].strip(), "kind": "audio-sink"})
    return out


def _inventory_cameras() -> list[dict]:
    import glob
    return [{"id": dev, "label": dev, "kind": "camera", "device": dev}
            for dev in sorted(glob.glob("/dev/video*"))]


def _local_inventory_node_names() -> set[str]:
    import socket
    names = {"", "host", "localhost", "127.0.0.1"}
    try:
        hostname = socket.gethostname()
        if hostname:
            names.add(hostname)
            names.add(hostname.split(".", 1)[0])
    except OSError:
        pass
    return names


@conn.handler("environment/query/inventory",
              meta={"label": "Twin environment inventory (displays / audio sinks / cameras)"})
def environment_inventory(node: str = "") -> dict:
    """Enumerate the CONTROLLABLE SURFACES of the environment — displays, audio sinks, cameras — so
    a planner can resolve needs-selection (1 surface → use it; N → pick from preference or ask the
    human). Read-only and best-effort: each probe degrades to [] when its tool/device/permission is
    absent. This is the inventory half of the twin — profile/drift answer REACHABILITY, inventory
    answers WHAT IS THERE (the input the autonomy thesis plans over, alongside action_space)."""
    requested = str(node or "").strip()
    if requested and requested not in _local_inventory_node_names():
        return urirun.ok(
            node="localhost",
            requestedNode=requested,
            displays=[],
            audioSinks=[],
            cameras=[],
            inventoryAvailable=False,
            warnings=[f"inventory is local-only in this connector; remote node {requested!r} was not probed"],
        )
    return urirun.ok(
        node=requested or "localhost",
        displays=_inventory_displays(),
        audioSinks=_inventory_audio_sinks(),
        cameras=_inventory_cameras(),
        inventoryAvailable=True,
    )


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
    # ③ Annotation — URI first (hot-swap annotator: different feasibility logic, remote node)
    plan_r = uri_call(
        f"twin://{_node}/plan/command/annotate",
        {"flow": raw_plan, "env": env, "prompt": prompt},
        fallback=lambda: {"ok": True, "plan": build_imperative_plan(raw_plan, env, prompt=prompt)},
    )
    plan = (plan_r or {}).get("plan") or build_imperative_plan(raw_plan, env, prompt=prompt)
    if browser_sel:
        _apply_browser_sel(plan, browser_sel)
    return _prompt_result(prompt, target, plan, env, include_mock)


@conn.handler("plan/command/annotate",
              meta={"label": "Annotate a flow with feasibility, reversibility and surface"})
def plan_annotate(flow: dict, env: dict, prompt: str = "") -> dict:
    """URI boundary for build_imperative_plan — switchable annotation logic.

    Deploying a different twin connector with a smarter annotator (e.g. LLM-augmented
    constraint reasoning) causes all callers to pick it up without code changes."""
    plan = build_imperative_plan(flow, env, prompt=prompt)
    return urirun.ok(plan=plan)


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


@conn.handler("mock/command/start-probe-stop", external=True,
              meta={"label": "Start mock → health-check → stop, prove reversibility"})
def mock_start_probe_stop(
    prompt: str = "",
    flow: dict | None = None,
    target: str = "",
    health_timeout: float = 15.0,
) -> dict:
    """Close the mock ↔ sandbox loop: generate → up → health-check → down -v.

    Proves that the generated Docker mock is:
      - reachable (HTTP 200 on testUri within health_timeout seconds)
      - reversible by contract (compose down -v removes all state — no re-scan needed)

    Without Docker: degrades gracefully, returning reachable=False, simulated=True,
    reversible=True (the guarantee is structural, not empirical).

    Typical caller: plan_from_prompt_route when include_mock=True and needsMock=True."""
    import shutil, subprocess, tempfile, time as _time  # noqa: E401
    env = probe(None, prompt=prompt)
    plan = build_imperative_plan(flow or {}, env, prompt=prompt)
    mock = generate_mock(prompt, plan, target=target or None)
    test_uri = mock.get("testUri") or ""

    if not shutil.which("docker"):
        return urirun.ok(
            mock=mock, reachable=False, reversible=True, simulated=True,
            note="Docker not found — reversibility is structural (compose down -v removes all state)",
        )

    work = tempfile.mkdtemp(prefix="twin-mock-")
    compose_path = f"{work}/docker-compose.yml"
    try:
        with open(compose_path, "w") as f:
            f.write(mock.get("dockerCompose") or "")
        _run_compose(["docker", "compose", "-f", compose_path, "up", "-d"])
        reachable = _wait_for_http(test_uri, timeout=health_timeout)
    finally:
        _run_compose(["docker", "compose", "-f", compose_path, "down", "-v"])
        import shutil as _sh
        _sh.rmtree(work, ignore_errors=True)

    return urirun.ok(
        mock=mock, reachable=reachable, reversible=True, simulated=False,
        testUri=test_uri,
        proof="compose-down-removes-all-state",
        note=None if reachable else f"service not reachable at {test_uri} within {health_timeout}s",
    )


def _run_compose(cmd: list) -> tuple[int, str]:
    import subprocess
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except Exception as exc:
        return 1, str(exc)


def _wait_for_http(url: str, *, timeout: float) -> bool:
    import time as _t
    import urllib.request
    if not url:
        return False
    deadline = _t.monotonic() + timeout
    while _t.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                if resp.status < 400:
                    return True
        except Exception:
            pass
        _t.sleep(1)
    return False


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


def _proof_store():
    """The durable ``_proofs`` ledger (a ``_NamespacedStore`` from twin_store) — the node
    HOLDS the proof state; this connector is the swappable URI capability over it."""
    from urirun.node.twin_store import durable_memory  # noqa: PLC0415
    return durable_memory().proof_store


@conn.handler("proof/query/check",
              meta={"label": "Proof cache hit? — is (uri, scenario, env) already proven reversible"})
def proof_check_route(uri: str = "", env_fingerprint: str = "") -> dict:
    """Cache hit ⇒ the sandbox can be skipped for this exact (uri, scenario, env)."""
    key = proof_key(uri, scenario_for_uri(uri), env_fingerprint)
    return proof_check({"proof_key": key}, _proof_store())


@conn.handler("proof/command/record",
              meta={"label": "Record a POSITIVE reversibility proof in the durable ledger"})
def proof_record_route(uri: str = "", env_fingerprint: str = "", verdict: str = "",
                       scanned_before: str = "", scanned_after: str = "") -> dict:
    """Persist only ``verdict == "reversible"`` — a negative is not durable proof."""
    sc = scenario_for_uri(uri)
    key = proof_key(uri, sc, env_fingerprint)
    return proof_record({"proof_key": key, "verdict": verdict, "uri": uri,
                         "env_fingerprint": env_fingerprint,
                         "scenario_signature": sc.signature(),
                         "scanned_before": scanned_before,
                         "scanned_after": scanned_after}, _proof_store())


@conn.handler("proof/command/gate",
              meta={"label": "Reversibility gate: skip on cache hit, else probe-then-record or block"})
def proof_gate_route(uri: str = "", env_fingerprint: str = "") -> dict:
    """check → probe → record. Drift is automatic: a changed env fingerprint is a new key,
    so it misses the cache and re-probes. Returns {decision: skip|proven|block, ...}."""
    return preflight_step(uri, scenario_for_uri(uri), env_fingerprint, _proof_store())


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


@conn.handler("flow/goal/query/verify",
              meta={"label": "Verify flow goal state after execution"})
def flow_goal_verify(goal: dict | None = None, results: dict | None = None) -> dict:
    """Check goal end-state after a flow.

    Calls goal.uri via the mesh and asserts the goal condition (contains/equals/present).
    Returns {ok:True, goalMet:True} on pass, {ok:False, goalMet:False} on fail so
    _thin_driver can trigger SAGA rollback when the goal state wasn't reached.
    A missing goal.uri is a no-op pass — query-only flows have no goal assertion."""
    from urirun_flow.flow_verify import _run_goal_check
    goal = goal or {}
    if not goal.get("uri"):
        return urirun.ok(goalMet=True, skipped="no-goal-uri")
    import urirun.v2_service as _svc
    dispatch = lambda uri, payload=None: _svc.call(uri, payload or {}, {}, mode="execute")
    try:
        passed, detail = _run_goal_check(goal, dispatch)
    except Exception as exc:
        return {"ok": False, "error": str(exc), "goalMet": False}
    return {**urirun.ok(), "ok": passed, "goalMet": passed, **detail}


@conn.handler("flow/command/rollback-ledger",
              meta={"label": "Roll back reversible mutations from ledger"})
def flow_rollback(ledger: list | None = None, mesh: dict | None = None) -> dict:
    """Undo reversible mutations from a pre-built thin-driver ledger (LIFO).

    Each entry: {uri, inverse, args, before, after}.  Applies inverses in reverse
    order via v2_service.  Named rollback-ledger to avoid shadowing
    urirun.node.reversible's handler at twin://…/flow/command/rollback, which takes
    {execution, mesh} and does full proof-by-re-scan.

    ``mesh`` is forwarded as the registry so mesh-routed inverses (kvm://, cdp://, etc.)
    resolve correctly — without it, only in-process connectors are reachable.  The thin
    driver passes mesh routes when it delegates rollback via this URI."""
    import urirun.v2_service as _svc
    from urirun.node.routing import registry_from_routes  # noqa: PLC0415
    routes = (mesh or {}).get("routes") or []
    registry = registry_from_routes(routes)
    ledger = ledger or []
    if not ledger:
        return urirun.ok(undone=[], note="empty ledger")
    undone: list[str] = []
    for entry in reversed(ledger):
        inv_uri = entry.get("inverse")
        if not inv_uri:
            continue
        try:
            rb = _svc.call(inv_uri, entry.get("args") or {}, registry, mode="execute")
        except Exception as exc:
            return {"ok": False, "undone": undone, "stuck": inv_uri, "error": str(exc)}
        if not rb.get("ok", True):
            return {"ok": False, "undone": undone, "stuck": inv_uri,
                    "reason": rb.get("error", "inverse failed")}
        undone.append(inv_uri)
    return urirun.ok(undone=undone)


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


@conn.handler("flow/command/execute",
              meta={"label": "Execute a URI flow plan via the thin-driver"})
def flow_execute(
    flow: dict,
    execute: bool = True,
    max_retries: int = 1,
    max_remediations: int = 6,
    max_wall_clock: float = 180.0,
) -> dict:
    """Run a flow plan through the thin-driver path via URI dispatch.

    Exposes execute_flow() as a URI boundary so callers can point to a different
    twin connector (remote node, heavier executor, sandboxed runner) without changing
    call sites.  Each step in the flow is dispatched through v2_service — the same
    mesh routing the dashboard uses — so remote kvm:// and browser:// steps work
    identically to in-process calls."""
    import urirun.v2_service as _svc
    from urirun.node.flow import execute_flow

    mode = "execute" if execute else "dry-run"
    dispatch = lambda uri, payload=None: _svc.call(uri, payload or {}, {}, mode=mode)
    return execute_flow(
        flow, {}, {}, execute=execute,
        dispatch_uri=dispatch,
        max_retries=max_retries,
        max_remediations=max_remediations,
        max_wall_clock=max_wall_clock,
    )


def _env_drift_ok(mem: object, node: str, skip: bool) -> bool:
    """True when the node's live env matches its known-good fingerprint (no drift).

    Fails OPEN when the live profile is unavailable/empty — indeterminate drift must not
    permanently disable the env-matched recall path.  Fails CLOSED only on a genuine probe
    exception (offline node), where we cannot trust the live env and should re-plan."""
    if skip:
        return True
    try:
        import urirun.v2_service as _svc  # noqa: PLC0415
        prof_r = _svc.call(f"kvm://{node}/env/query/profile", {}, {}, mode="execute")
        val = prof_r.get("result") or {}
        if isinstance(val, dict) and "value" in val:
            val = val["value"]
        profile = val if isinstance(val, dict) else {}
        if not profile:
            return True  # indeterminate → allow (preflight re-validates)
        verdict = mem.drift(node, profile)  # type: ignore[union-attr]
        if not verdict.get("known"):
            return True  # no baseline yet → allow
        return not verdict.get("drifted")
    except Exception:  # noqa: BLE001 — offline node → re-plan, don't replay
        return False


@conn.handler("flow/query/recall",
              meta={"label": "Return a cached flow plan by intent × env — the pre-LLM recall gate as URI"})
def flow_recall(
    prompt: str = "",
    env_fp: str = "",
    episode_id: str = "",
    node: str = "host",
    skip_drift_check: bool = False,
) -> dict:
    """URI boundary for the recall gate: check episode_store then flow_store before the LLM.

    Priority:
      1. episode_id — direct lookup (content-addressed, always wins if provided)
      2. intent_sig × env_fp — recall_episode (env-conditioned, strongest match)
      3. intent_sig alone — recall_flow_by_intent (env-agnostic fallback, no drift guard)

    Tiers 1 and 2 consult the drift gate: if the env drifted from the known-good fingerprint,
    recall is suppressed (found=False, driftDetected=True) so the caller re-plans fresh.
    Tier 3 (flow_store, intent-only) skips the drift check — offered as a hint, not a guarantee.

    Returns {found: True, steps, source, episode_id?} or {found: False, steps: []}."""
    from urirun.node.twin_store import durable_memory  # noqa: PLC0415
    mem = durable_memory()

    # 1. Direct episode lookup (content-addressed; drift gate guards replay)
    if episode_id:
        ep = mem.episode_store.get(episode_id)
        if ep and (ep.get("outcome") or {}).get("status") == "ok":
            steps = (ep.get("plan") or {}).get("steps") or []
            if steps:
                if not _env_drift_ok(mem, node, skip_drift_check):
                    return urirun.ok(found=False, steps=[], driftDetected=True,
                                     reason="env drifted from known-good — re-plan required")
                return urirun.ok(found=True, steps=steps, source="episode",
                                 episode_id=episode_id, goal=ep.get("goal"))

    # 2. Intent × env fingerprint (episode_store; strongest env-conditioned match)
    if prompt and env_fp:
        from urirun.node.episode import intent_signature  # noqa: PLC0415
        sig = intent_signature(prompt)
        ep = mem.recall_episode(sig, env_fp)
        if ep:
            steps = (ep.get("plan") or {}).get("steps") or []
            if steps:
                if not _env_drift_ok(mem, node, skip_drift_check):
                    return urirun.ok(found=False, steps=[], driftDetected=True,
                                     reason="env drifted from known-good — re-plan required")
                return urirun.ok(found=True, steps=steps, source="episode",
                                 episode_id=ep.get("episode_id"), goal=ep.get("goal"))

    # 3. Intent-only fallback (flow_store — no env constraint; no drift guard)
    if prompt:
        rec = mem.recall_flow_by_intent(prompt)
        if rec:
            steps = rec.get("steps") or []
            if steps:
                return urirun.ok(found=True, steps=steps, source="flow_store",
                                 flow_key=rec.get("flowKey"), goal=rec.get("prompt"),
                                 driftUnchecked=True)

    return urirun.ok(found=False, steps=[])


@conn.handler("experience/query/retrieve",
              meta={"label": "Retrieve candidate episodes, routes and preferences for propose-stage planning"})
def experience_retrieve(
    intent: str = "",
    fingerprint: str = "",
    env_fp: str = "",
    k: int = 5,
    node: str = "host",
    routes: list | None = None,
) -> dict:
    """Retrieve propose-stage candidates from derived Twin memory/index state.

    Similarity/exact recall here is advisory only. The returned candidates are not
    accepted plans; every proposed flow still goes through router/contract/env gates.
    """
    from .experience import retrieve_experience
    from urirun.node.twin_store import durable_memory  # noqa: PLC0415

    data = retrieve_experience(
        intent=intent,
        fingerprint=fingerprint or env_fp,
        k=k,
        node=node or "host",
        routes=routes or [],
        memory=durable_memory(),
    )
    return urirun.ok(**data)


@conn.handler("flow/episode/command/run",
              meta={"label": "Run the flow plan stored in an episode (plan atom → execute)"})
def flow_episode_run(
    episode_id: str,
    execute: bool = True,
    max_retries: int = 1,
    max_remediations: int = 6,
    max_wall_clock: float = 180.0,
) -> dict:
    """Content-addressed flow execution: look up plan atom by episode_id, then run it.

    Makes any episodic plan a first-class dispatchable URI — the plan lives in the same
    address space as the facts and actions it operates on.  Idempotent: re-running with
    the same episode_id re-executes the same step sequence against current world state."""
    from urirun.node.twin_store import durable_memory  # noqa: PLC0415
    import urirun.v2_service as _svc
    from urirun.node.flow import execute_flow
    mem = durable_memory()
    ep = mem.episode_store.get(episode_id)
    if not ep:
        return urirun.ok(ok=False, found=False,
                         error={"category": "NOT_FOUND", "message": f"episode {episode_id!r} not found"})
    steps = (ep.get("plan") or {}).get("steps") or []
    if not steps:
        return urirun.ok(ok=False, found=False,
                         error={"category": "NOT_FOUND", "message": f"episode {episode_id!r} has no plan steps"})
    flow = {"steps": steps, "task": {"id": "recall", "source": "episode", "title": ep.get("goal") or ""}}
    mode = "execute" if execute else "dry-run"
    dispatch = lambda uri, payload=None: _svc.call(uri, payload or {}, {}, mode=mode)
    return execute_flow(
        flow, {}, {}, execute=execute,
        dispatch_uri=dispatch,
        max_retries=max_retries,
        max_remediations=max_remediations,
        max_wall_clock=max_wall_clock,
    )


@conn.handler("flow/command/diagnose",
              meta={"label": "Match a step error against the diagnostics playbook"})
def flow_diagnose(
    error: dict,
    step: dict | None = None,
    routes: list | None = None,
    environment: dict | None = None,
    surface: dict | None = None,
) -> dict:
    """URI boundary for the diagnostics playbook (diagnose()).

    Replace this route with a smarter connector (e.g. LLM-augmented root-cause
    analysis) without touching the flow engine.  Returns
    {ok, found, rule, cause, confidence, remediation, autoApplicable} or
    {ok, found: false} when no playbook rule matches."""
    from urirun.node.diagnostics import diagnose

    diagnosis = diagnose(error or {}, step=step, routes=routes or [],
                         environment=environment, surface=surface)
    if diagnosis is None:
        return urirun.ok(found=False)
    return urirun.ok(found=True, **diagnosis)


@conn.handler("monitor/event", meta={"label": "Twin monitor SSE event marker"})
def monitor_event(node: str = "", stateSig: str = "", narration: str = "") -> dict:
    """Receive a twin state-transition event (distributed to /events?scheme=twin SSE)."""
    return urirun.ok(node=node, stateSig=stateSig, narration=narration, received=True)


def bindings() -> dict:
    return conn.bindings()


def _manifest_prose() -> dict:
    """Load optional prose metadata without making bindings/CLI depend on it."""
    try:
        prose = urirun.load_manifest(__package__)
    except FileNotFoundError:
        prose_path = Path(__file__).resolve().parent.parent / "connector.manifest.json"
        if not prose_path.exists():
            return {}
        prose = json.loads(prose_path.read_text(encoding="utf-8"))
    # Older twin checkouts keep a bindings document here. It is useful for static
    # discovery, but not valid prose for conn.manifest(...).
    if isinstance(prose, dict) and prose.get("version") == "urirun.bindings.v2":
        return {}
    return prose if isinstance(prose, dict) else {}


def manifest() -> dict:
    return conn.manifest(_manifest_prose())


def main(argv: list[str] | None = None) -> int:
    return conn.cli(argv, manifest_prose=_manifest_prose())


if __name__ == "__main__":
    import sys
    sys.exit(main())
