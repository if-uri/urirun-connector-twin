"""Environment probe: structured capability snapshot for the twin planner.

Every external capability is accessed as a URI call first.  Fallbacks to
in-process implementations exist only for the case where the connector is not
yet served by a running node.

External URIs used (switchable via the mesh):
  kvm://{node}/env/query/profile          — actionMatrix + bestSurface
  kvm://{node}/surface/query/current      — active surface info
  twin://host/constraints/query/from-profile  — infeasible constraints from actionMatrix
  twin://host/browser/query/sessions      — live Chrome session discovery
"""
from __future__ import annotations

import importlib.util
import os
import platform
import subprocess
import sys
from typing import Any

from .browser import discover_browser_sessions, select_session
from .dispatch import uri_call, value_of
from .prompt_plan import derive_task_target


# ─── local fallbacks (used when mesh URIs are not yet served) ─────────────────

def _safe_import(module: str) -> Any:
    if importlib.util.find_spec(module) is None:
        return None
    try:
        return __import__(module, fromlist=[""])
    except Exception:
        return None


def _kvm_query(node: str, route: str) -> dict | None:
    """Call kvm://node/route via the mesh; return the value dict or None."""
    r = uri_call(f"kvm://{node}/{route}", timeout=4.0)
    if r:
        return value_of(r) or (r if isinstance(r, dict) else None)
    return None


_LOCAL_NODES = {"", "host", "localhost", "local", "127.0.0.1"}


def _is_local_node(node: str | None) -> bool:
    """True when ``node`` denotes the local host rather than a remote mesh node."""
    return not node or str(node).lower() in _LOCAL_NODES


def _kvm_profile_local() -> dict | None:
    """In-process kvm env profile, used when the connector is installed locally
    but its ``env/query/profile`` route is not reachable over the mesh yet.

    The preflight planner runs before the node is served, so the mesh call in
    ``_kvm_query`` returns nothing even though the very same flow will reach the
    kvm profile in-process at execution time (via ``v2_service``). Without this
    fallback the plan reports ``/screen/query/capture`` as infeasible ("kvm
    connector not installed") while routing + execution succeed — contradictory
    operator evidence. Reusing the connector's own ``profile()`` keeps the plan's
    feasibility aligned with what the flow actually does. No hard dependency: a
    missing kvm connector simply leaves the infeasible constraint in place."""
    kvm = _safe_import("urirun_connector_kvm.environment")
    if kvm is None or not hasattr(kvm, "profile"):
        return None
    try:
        prof = kvm.profile()
        return prof if isinstance(prof, dict) else None
    except Exception:
        return None


def _constraints_from_profile_local(action_matrix: dict) -> list[dict]:
    """In-process fallback: call reversible._infeasible_constraints directly."""
    rev = _safe_import("urirun.node.reversible")
    if rev is None:
        return []
    try:
        return rev._infeasible_constraints(action_matrix)
    except Exception:
        return []


def _constraints_via_uri(action_matrix: dict) -> list[dict]:
    """Fetch infeasible constraints through twin://host/constraints/query/from-profile."""
    r = uri_call("twin://host/constraints/query/from-profile",
                 {"actionMatrix": action_matrix},
                 fallback=lambda: None)
    cs = (r or {}).get("constraints")
    if isinstance(cs, list):
        return cs
    return _constraints_from_profile_local(action_matrix)


def _host_os_info() -> dict:
    uname = platform.uname()
    return {
        "os": uname.system.lower(),
        "release": uname.release,
        "machine": uname.machine,
        "python": sys.version.split()[0],
        "wayland": bool(os.environ.get("WAYLAND_DISPLAY")),
        "display": bool(os.environ.get("DISPLAY")),
    }


def _docker_available() -> bool:
    try:
        r = subprocess.run(["docker", "info"], capture_output=True, timeout=5)
        return r.returncode == 0
    except Exception:
        return False


def _probe_browser(task: dict) -> dict:
    """Discover and select a browser session for the task target.

    Tries twin://host/browser/query/sessions via the mesh first (so a remote
    node can serve its own browser list), falls back to local /proc scan."""
    r = uri_call(
        "twin://host/browser/query/sessions",
        {"probe_cookies": True},
        fallback=lambda: {"ok": True, "sessions": discover_browser_sessions(probe_cookies=True)},
    )
    sessions = (r or {}).get("sessions") or []
    domain = task.get("domain") or ""
    needs_auth = task.get("needsAuth", False)
    selection = select_session(sessions, domain, needs_auth) if domain else {
        "mode": "no-target", "port": None, "userDataDir": None, "rationale": "no domain in task"
    }
    return {"sessions": sessions, "selection": selection, "task": task}


def _host_has_kvm_binding() -> bool:
    """Return True when the kvm connector is installed in this Python environment."""
    try:
        import importlib.metadata as _meta
        return any(
            "kvm" in str(ep).lower()
            for ep in _meta.entry_points(group="urirun.bindings")
        )
    except Exception:
        return False


def probe(node: str | None = None, prompt: str = "") -> dict:
    """Return a unified environment snapshot for the given node (or localhost).

    Priority for each capability: URI mesh → local fallback.
    When prompt is provided, derives task target and probes browser sessions
    with auth cookie verification."""
    warnings: list[str] = []
    host_info = _host_os_info()
    profile: dict = {}
    surface: dict = {}

    node_kvm_unreachable = False
    if node:
        p = _kvm_query(node, "env/query/profile")
        if not p and _is_local_node(node):
            # Mesh route not served during preflight — reuse the in-process kvm
            # profile so feasibility matches the execution path (no false negative).
            p = _kvm_profile_local()
        if p:
            profile = p
        else:
            node_kvm_unreachable = True
            warnings.append(f"kvm://{node}/env/query/profile unreachable — host-only snapshot")
        s = _kvm_query(node, "surface/query/current")
        if s:
            surface = s
        elif not _is_local_node(node):
            warnings.append(f"kvm://{node}/surface/query/current unreachable")

    # When no remote node is selected, check if the host itself can capture the screen.
    host_kvm_missing = not node and not _host_has_kvm_binding()

    action_matrix = profile.get("actionMatrix") or {}
    constraints = _constraints_via_uri(action_matrix)

    if node_kvm_unreachable:
        # kvm screen-capture steps are infeasible when the selected node's env is unreachable.
        # kvm routes use "kvm://host/..." as authority regardless of which node runs them
        # (serviceMap routes transparently), so we match the ROUTE PATH, not the URI prefix.
        # _is_infeasible checks `what in uri` as a substring match.
        if _is_local_node(node):
            # Reached only when the in-process fallback also found no kvm profile,
            # i.e. the connector really is absent on this host.
            reason = "kvm connector not installed on this host — cannot capture local screen"
            fix = "pip install urirun-connector-kvm  # or select a node that has kvm"
        else:
            reason = (f"Node '{node}' environment unreachable — kvm connector not installed "
                      "or node offline")
            fix = f"urirun host ensure {node} kvm"
        constraints.append({
            "kind": "infeasible",
            "what": "/screen/query/capture",
            "surface": "unknown",
            "reason": reason,
            "fix": fix,
        })

    if host_kvm_missing:
        # No remote node selected AND host doesn't have kvm installed locally.
        # Screen capture cannot run — tell the user how to fix it.
        constraints.append({
            "kind": "infeasible",
            "what": "/screen/query/capture",
            "surface": "unknown",
            "reason": "kvm connector not installed on this host — cannot capture local screen",
            "fix": "pip install urirun-connector-kvm  # or: select a node that has kvm",
        })

    task = derive_task_target(prompt) if prompt else {"domain": None, "needsAuth": False}
    session_probe = _probe_browser(task)
    selection = session_probe["selection"]

    if task.get("needsAuth") and selection.get("mode") in ("needs-login", "no-chrome", "none"):
        constraints.append({
            "kind": "infeasible",
            "what": "web-auth",
            "surface": "cdp",
            "reason": selection.get("rationale") or selection.get("reason") or "no authenticated session",
            "fix": "one-time login (human-gated)",
            "authRequired": True,
        })

    return {
        "node": node or "localhost",
        "host": host_info,
        "profile": profile,
        "surface": surface,
        "constraints": constraints,
        "controllable": profile.get("controllable"),
        "bestSurface": profile.get("best"),
        "actionMatrix": action_matrix,
        "dockerAvailable": _docker_available(),
        "warnings": warnings,
        "sessionProbe": session_probe,
        "sessionSelection": selection,
        "task": task,
    }
