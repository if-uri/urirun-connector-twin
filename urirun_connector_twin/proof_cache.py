# Author: Tom Sapletta · https://tom.sapletta.com
# Part of the ifURI solution.
#
# Connector-side proof cache — two twin:// routes + preflight gate.
#
# Drop-in for two routes in the connector manifest:
#   twin://{node}/proof/query/check      → proof_check(payload, store)
#   twin://{node}/proof/command/record   → proof_record(payload, store)
#
# The gate (preflight_step) wires them together:
#   1. check(key) → hit  → skip sandbox, continue           (fast path)
#   2. check(key) → miss → probe_fn(scenario) → reversible  → record + proven
#   3. check(key) → miss → probe_fn(scenario) → irreversible → block (NOT cached)
#
# Content-addressing contract:
#   proof_key = sha(uri | scenario.signature() | env_fingerprint)
#
#   scenario.signature() hashes the commands that define the proof. Change the
#   inverse command and the signature changes → old cached proof auto-misses.
#
#   env_fingerprint is the same "env-..." that TwinMemory already tracks. Drift in
#   the environment changes the fingerprint → proof cache misses → sandbox re-runs.
#
#   Only POSITIVE verdicts are stored. A transient miss (docker busy) must not
#   freeze a step; negative is not durable proof, only a momentary observation.
#
# In production: probe_fn → sandbox.probe_reversibility; store → _NamespacedStore
# from twin_store ("_proofs" namespace in twin-memory.json).
from __future__ import annotations

import time
from typing import Any, Callable

from urirun.node.episode import proof_key as _proof_key

from .sandbox import Scenario, probe_reversibility


# ────────────────────────────────────────────────── public proof_key wrapper ──── #

def proof_key(uri: str, scenario: Scenario, env_fingerprint: str) -> str:
    """Stable content-address for a reversibility proof of (uri, scenario, env).

    Delegates to ``urirun.node.episode.proof_key`` so connector-twin and the
    core episode module share one formula — a single source of truth."""
    return _proof_key(uri, scenario.signature(), env_fingerprint)


# ─────────────────────────────────────────────────────── route handlers ──── #

def proof_check(payload: dict, store: Any) -> dict:
    """twin://{node}/proof/query/check — is this proof already cached?"""
    key = payload.get("proof_key") or ""
    if not key:
        return {"ok": False, "error": "proof_key required"}
    rec = store.get(key)
    if rec is not None:
        return {"ok": True, "hit": True, "proof_key": key,
                "verdict": rec.get("verdict"), "proven_at": rec.get("ts"),
                "next": {"kind": "continue"}}
    return {"ok": True, "hit": False, "proof_key": key, "next": {"kind": "continue"}}


def proof_record(payload: dict, store: Any) -> dict:
    """twin://{node}/proof/command/record — persist a POSITIVE verdict only.

    Negative verdicts are intentionally not cached: a transient sandbox failure
    must not prevent a retry from succeeding once the environment is ready."""
    key = payload.get("proof_key") or ""
    if not key:
        return {"ok": False, "error": "proof_key required"}
    if payload.get("verdict") != "reversible":
        return {"ok": True, "recorded": False, "proof_key": key,
                "reason": "only positive verdicts are cached — negative is not durable proof"}
    store[key] = {
        "proof_key": key,
        "verdict": "reversible",
        "uri": payload.get("uri") or "",
        "env_fingerprint": payload.get("env_fingerprint") or "",
        "scenario_signature": payload.get("scenario_signature") or "",
        "scanned_before": payload.get("scanned_before") or "",
        "scanned_after": payload.get("scanned_after") or "",
        "ts": payload.get("ts") or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    return {"ok": True, "recorded": True, "proof_key": key}


# ─────────────────────────────────────────────────── preflight gate ──── #

def preflight_step(
    uri: str,
    scenario: Scenario,
    env_fingerprint: str,
    store: Any,
    probe_fn: Callable[[Scenario], dict] | None = None,
    ts: str = "",
) -> dict:
    """Check → probe → record gate.

    ``probe_fn`` defaults to ``sandbox.probe_reversibility`` (Docker / simulated).
    Pass a stub in tests to control the verdict and observe whether sandbox runs.

    Returns a decision dict:
      {"decision": "skip"|"proven"|"block", "reason": str, "proof_key": str,
       "next": {"kind": "continue"|"rollback"}}
    """
    key = proof_key(uri, scenario, env_fingerprint)
    check = proof_check({"proof_key": key}, store)
    if check.get("hit"):
        return {"decision": "skip", "reason": "proven-reversible (cached)",
                "proof_key": key, "next": {"kind": "continue"}}

    fn = probe_fn if probe_fn is not None else probe_reversibility
    result = fn(scenario)
    if result.get("reversible"):
        proof_record({
            "proof_key": key, "verdict": "reversible",
            "uri": uri,
            "env_fingerprint": env_fingerprint,
            "scenario_signature": scenario.signature(),
            "scanned_before": result.get("before") or str(result.get("scanned_before") or ""),
            "scanned_after": result.get("after") or str(result.get("scanned_after") or ""),
            "ts": ts or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }, store)
        return {"decision": "proven", "reason": "sandbox proved reversible; cached",
                "proof_key": key, "next": {"kind": "continue"}}

    return {"decision": "block", "reason": "sandbox could not prove reversibility",
            "proof_key": key, "next": {"kind": "rollback"}}


# ──────────────────────────────────── in-memory store for tests / REPL ──── #

class DictProofStore(dict):
    """A plain dict that satisfies the store interface (get / __setitem__ / __contains__).

    Use this in unit tests. In production wire a ``_NamespacedStore("_proofs")``
    from ``twin_store.durable_memory()`` — same interface, JSON-backed atomic writes."""

    def get(self, key, default=None):  # type: ignore[override]
        return super().get(key, default)
