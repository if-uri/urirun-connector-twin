"""Imperative plan generator: prompt + environment → ordered steps with reversibility.

Each step is a concrete URI operation annotated with:
  - feasible: bool  (passes infeasibility gate)
  - reversible: bool
  - inverse: URI or None
  - surface: which surface executes this step
  - blocked_by: constraint id if infeasible (else null)

When a step is infeasible on the available surfaces, the step is kept in the plan
but marked `feasible: false` and `blocked_by` carries the constraint that fired.
The mock module then decides whether to generate a Docker environment for testing."""
from __future__ import annotations

import re


_OS_TYPE_PATHS = frozenset({
    "/input/command/type", "/input/command/fill",
    "/screen/command/type", "/screen/command/fill",
    "/atspi/command/type", "/atspi/command/fill",
})

_CDP_ROUTES = frozenset({
    "/cdp/page/command/navigate", "/cdp/page/command/fill",
    "/cdp/page/command/click", "/cdp/page/query/evaluate",
    "/cdp/session/command/ensure", "/cdp/session/query/ready",
})

_REVERSIBLE_TABLE: dict[str, str | None] = {
    "/page/command/navigate": "/page/command/navigate",
    "/page/command/fill": None,
    "/page/command/click": None,
    "/session/command/ensure": "/session/command/close",
    "/session/command/close": "/session/command/ensure",
    "/input/command/type": None,
    "/input/command/click": None,
    "/file/command/write": "/file/command/delete",
    "/file/command/delete": None,
    "/service/command/start": "/service/command/stop",
    "/service/command/stop": "/service/command/start",
}


def _route_suffix(uri: str) -> str:
    """Extract the last 3 path segments as the route suffix."""
    parts = uri.rstrip("/").split("/")
    return "/" + "/".join(parts[-3:]) if len(parts) >= 3 else uri


def _is_infeasible(uri: str, constraints: list[dict]) -> dict | None:
    suffix = _route_suffix(uri)
    for c in constraints:
        if c.get("kind") == "infeasible" and (c.get("what") or "") in uri:
            return c
    return None


def _step_surface(uri: str, best_surface: str | None) -> str:
    s = _route_suffix(uri)
    if any(cdp in uri for cdp in ("/cdp/", "/browser/")):
        return "cdp"
    if any(p in s for p in _OS_TYPE_PATHS):
        return best_surface or "os"
    return best_surface or "unknown"


def _step_reversible(uri: str, route_contracts: dict | None = None) -> tuple[bool, str | None]:
    """Reversibility of a route. CONTRACT IS THE SINGLE SOURCE when available: if the live registry
    carries a contract for this URI (``route_contracts[uri]`` = a ``meta.contract`` dict with
    ``reversible``/``inverseRoute``), it wins. The static ``_REVERSIBLE_TABLE`` is the FALLBACK for
    routes whose connector has no contract yet (most of the fleet) — dropping it would regress those
    to unknown. Pass ``route_contracts`` (e.g. built from a compiled registry) to make the planner
    contract-driven for covered routes while staying correct for the rest."""
    if route_contracts:
        c = route_contracts.get(uri)
        if isinstance(c, dict) and "reversible" in c:
            rev = bool(c.get("reversible"))
            return rev, (c.get("inverseRoute") or None) if rev else None
    suffix = _route_suffix(uri)
    for pattern, inv in _REVERSIBLE_TABLE.items():
        if pattern in suffix:
            return (inv is not None), inv
    return False, None


def annotate_steps(steps: list[dict], env: dict, route_contracts: dict | None = None) -> list[dict]:
    """Annotate a list of {id, uri, payload} steps with feasibility + reversibility.

    ``route_contracts`` (optional URI→contract map from the live registry's ``meta.contract``) makes
    reversibility contract-driven for covered routes; absent, the static table is used (unchanged
    behaviour). Backward-compatible: callers that pass nothing get exactly the old annotation."""
    constraints = env.get("constraints") or []
    best = env.get("bestSurface")
    annotated = []
    for i, step in enumerate(steps, 1):
        uri = str(step.get("uri") or "")
        infeasible = _is_infeasible(uri, constraints)
        reversible, inverse = _step_reversible(uri, route_contracts)
        annotated.append({
            "step": i,
            "id": step.get("id") or f"step_{i}",
            "uri": uri,
            "payload": step.get("payload") or {},
            "surface": _step_surface(uri, best),
            "feasible": infeasible is None,
            "reversible": reversible,
            "inverse": inverse,
            "blocked_by": infeasible.get("what") if infeasible else None,
            "fix": infeasible.get("fix") if infeasible else None,
        })
    return annotated


def extract_steps_from_flow(flow: dict) -> list[dict]:
    """Pull raw steps from a urirun flow dict."""
    return [{"id": s.get("id"), "uri": s.get("uri"), "payload": s.get("payload") or {}}
            for s in (flow.get("steps") or [])]


def build_imperative_plan(flow: dict, env: dict, prompt: str = "",
                          route_contracts: dict | None = None) -> dict:
    """Generate an imperative plan from a flow + environment probe. ``route_contracts`` (optional
    URI→contract map from the live registry) makes reversibility contract-driven; absent, the
    static table is used (unchanged)."""
    raw_steps = extract_steps_from_flow(flow)
    steps = annotate_steps(raw_steps, env, route_contracts)
    infeasible_steps = [s for s in steps if not s["feasible"]]
    irreversible_steps = [s for s in steps if not s["reversible"]]
    return {
        "prompt": prompt,
        "node": env.get("node"),
        "steps": steps,
        "totalSteps": len(steps),
        "feasibleSteps": len(steps) - len(infeasible_steps),
        "infeasibleSteps": len(infeasible_steps),
        "irreversibleSteps": len(irreversible_steps),
        "needsMock": len(infeasible_steps) > 0 or not env.get("dockerAvailable"),
        "environment": {
            "bestSurface": env.get("bestSurface"),
            "controllable": env.get("controllable"),
            "constraints": env.get("constraints") or [],
            "warnings": env.get("warnings") or [],
        },
    }
