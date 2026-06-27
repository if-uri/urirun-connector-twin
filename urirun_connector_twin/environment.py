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
        if p:
            profile = p
        else:
            node_kvm_unreachable = True
            warnings.append(f"kvm://{node}/env/query/profile unreachable — host-only snapshot")
        s = _kvm_query(node, "surface/query/current")
        if s:
            surface = s
        else:
            warnings.append(f"kvm://{node}/surface/query/current unreachable")

    action_matrix = profile.get("actionMatrix") or {}
    constraints = _constraints_via_uri(action_matrix)

    if node_kvm_unreachable:
        # kvm://{node}/... steps are infeasible when the node is unreachable.
        # _is_infeasible matches any URI containing the "what" string as a substring.
        constraints.append({
            "kind": "infeasible",
            "what": f"kvm://{node}/",
            "surface": "unknown",
            "reason": (f"Node '{node}' environment unreachable — kvm connector not installed "
                       "or node offline"),
            "fix": f"urirun host ensure {node} kvm",
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
