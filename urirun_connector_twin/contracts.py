# Author: Tom Sapletta · https://tom.sapletta.com
# Part of the ifURI solution.
"""Route contracts for the twin connector (LLM-editable declaration).

Twin owns the autonomous planning / proof / flow-control surface. Some routes are live-stateful
(Chrome sessions, Docker sandbox, durable twin store), so their examples are contract golden
fixtures, not a promise that CI will execute every route against real external services. The stable
URI boundary is still declared here: input payload, query/command effect, and the additive output
core each caller can rely on before dispatching a natural-language task.

Single scheme but declared via the shared connector; contract keys are FULL URIs joined via
``attach_contracts(None, CONTRACTS)``.
"""
from __future__ import annotations

from urirun_connectors_toolkit.contract_gate import Contract


STATEFUL_ERRORS = ("degraded-backend", "precondition-unmet", "unreachable", "unknown")


def _ok(**extra) -> dict:
    return {"ok": True, **extra}


def _command(
    inp: dict,
    out: dict,
    *,
    payload: dict | None = None,
    result: dict | None = None,
    errors: tuple[str, ...] = STATEFUL_ERRORS,
) -> Contract:
    return Contract(
        version="v1",
        effect="command",
        inp=inp,
        out=out,
        errors=errors,
        examples=(
            {
                "payload": payload or {},
                "result": result or _ok(),
            },
        ),
    )


CONTRACTS: dict[str, Contract] = {

    "twin://host/environment/query/profile": Contract(
        version="v1", effect="query",
        inp={"node": "?str", "prompt": "?str"},
        out={"ok": "const:true", "node": "str", "host": "obj", "constraints": "list", "actionMatrix": "obj"},
        examples=(
            {"payload": {},
             "result": {"ok": True, "node": "localhost",
                        "host": {"os": "linux", "release": "6.17.0", "machine": "x86_64",
                                 "python": "3.13.7", "wayland": True, "display": True},
                        "profile": {}, "surface": {}, "constraints": [], "actionMatrix": {}, "warnings": []}},
        )),
    "twin://host/environment/query/inventory": Contract(
        version="v1", effect="query",
        inp={"node": "?str"},
        out={"ok": "const:true", "node": "str", "displays": "list", "audioSinks": "list",
             "cameras": "list"},
        examples=(
            {"payload": {},
             "result": {"ok": True, "node": "localhost",
                        "displays": [], "audioSinks": [], "cameras": []}},
        )),

    "twin://host/constraints/query/from-profile": Contract(
        version="v1", effect="query",
        inp={"actionMatrix": "obj"},
        out={"ok": "const:true", "constraints": "list"},
        examples=(
            {"payload": {"actionMatrix": {}},
             "result": {"ok": True, "constraints": []}},
        )),

    "twin://host/step/query/feasibility": Contract(
        version="v1", effect="query",
        inp={"uri": "str", "node": "?str", "prompt": "?str"},
        out={"ok": "const:true", "uri": "str", "feasible": "bool", "surface": "str", "reversible": "bool"},
        examples=(
            {"payload": {"uri": "kvm://host/screen/query/capture"},
             "result": {"ok": True, "uri": "kvm://host/screen/query/capture", "node": "localhost",
                        "feasible": True, "surface": "unknown", "reversible": False,
                        "blocked_by": None, "fix": None, "constraints": [],
                        "sessionSelection": {"mode": "no-target", "port": None}}},
        )),

    # browser/query/* — czyste reads CDP (enumeracja/selekcja sesji Chrome), bez LLM/stanu twin
    "twin://host/browser/query/sessions": Contract(
        version="v1", effect="query",
        inp={"probe_cookies": "?bool"},
        out={"ok": "const:true", "sessions": "list", "count": "int", "reachable": "int"},
        examples=(
            {"payload": {},
             "result": {"ok": True, "sessions": [], "count": 0, "reachable": 0}},
        )),

    "twin://host/browser/query/profile": Contract(
        version="v1", effect="query",
        inp={"domain": "?str", "prompt": "?str", "probe_cookies": "?bool"},
        out={"ok": "const:true", "domain": "str", "selection": "?obj", "sessions": "int", "reachable": "int"},
        examples=(
            {"payload": {"domain": "example.com"},
             "result": {"ok": True, "domain": "example.com", "selection": None, "sessions": 0, "reachable": 0}},
        )),

    # proof/query/check — deterministyczny lookup w cache dowodów odwracalności (czyta twin store)
    "twin://host/proof/query/check": Contract(
        version="v1", effect="query",
        inp={"uri": "?str", "env_fingerprint": "?str"},
        out={"ok": "const:true", "hit": "bool", "proof_key": "str", "next": "obj",
             "verdict": "?str", "proven_at": "?any"},
        examples=(
            {"payload": {"uri": "kvm://host/screen/query/capture", "env_fingerprint": "deadbeef"},
             "result": {"ok": True, "hit": False,
                        "proof_key": "kvm://host/screen/query/capture::default::deadbeef",
                        "next": {"kind": "continue"}}},
        )),

    # proof/command/record — zapisuje POZYTYWNY dowód odwracalności w trwałym ledgerze (mutuje store)
    "twin://host/proof/command/record": Contract(
        version="v1", effect="command", reversible=False,
        inp={"uri": "?str", "env_fingerprint": "?str", "verdict": "?str", "scanned_after": "?any"},
        out={"ok": "const:true", "recorded": "bool", "proof_key": "str", "reason": "?str"},
        examples=(
            {"payload": {"uri": "fs://host/file/command/write", "env_fingerprint": "abc", "verdict": "reversible"},
             "result": {"ok": True, "recorded": True, "proof_key": "fs://host/file/command/write::default::abc"}},
        )),

    # proof/command/gate — brama odwracalności: skip (cache) | proven (probe+record) | block.
    # Koperta bez `ok` (jak preflight_step) — decision/reason/proof_key/next.
    "twin://host/proof/command/gate": Contract(
        version="v1", effect="command", reversible=False,
        inp={"uri": "?str", "env_fingerprint": "?str"},
        out={"decision": "enum:skip|proven|block", "reason": "str", "proof_key": "str", "next": "obj"},
        examples=(
            {"payload": {"uri": "kvm://host/screen/query/capture", "env_fingerprint": "deadbeef"},
             "result": {"decision": "skip", "reason": "proven-reversible (cached)",
                        "proof_key": "kvm://host/screen/query/capture::default::deadbeef",
                        "next": {"kind": "continue"}}},
        )),

    # plan/command/* — autonomous NL/flow planning boundaries. Plan internals stay additive.
    "twin://host/plan/command/from-prompt": _command(
        {"prompt": "str", "node": "?str", "include_mock": "?bool", "probe_browser": "?bool"},
        {"ok": "const:true", "prompt": "str", "taskType": "?str", "domain": "?str",
         "needsAuth": "bool", "plan": "obj", "environment": "obj", "mock": "?obj"},
        payload={"prompt": "otworz linkedin", "probe_browser": False},
        result=_ok(
            prompt="otworz linkedin",
            taskType="unknown",
            domain="linkedin.com",
            needsAuth=True,
            plan={"steps": [], "needsMock": False},
            environment={"node": "localhost", "constraints": [], "warnings": []},
        ),
    ),

    "twin://host/plan/command/annotate": _command(
        {"flow": "obj", "env": "obj", "prompt": "?str"},
        {"ok": "const:true", "plan": "obj"},
        payload={"flow": {"steps": []}, "env": {"node": "localhost", "constraints": []}},
        result=_ok(plan={"steps": [], "totalSteps": 0, "needsMock": False}),
    ),

    "twin://host/plan/command/generate": _command(
        {"flow": "obj", "prompt": "?str", "node": "?str", "include_mock": "?bool"},
        {"ok": "const:true", "plan": "obj", "environment": "obj", "mock": "?obj"},
        payload={"flow": {"steps": []}, "prompt": "test"},
        result=_ok(
            plan={"steps": [], "totalSteps": 0, "needsMock": False},
            environment={"node": "localhost", "constraints": [], "warnings": []},
        ),
    ),

    "twin://host/mock/command/create": _command(
        {"prompt": "?str", "flow": "?obj", "target": "?str"},
        {"ok": "const:true", "mock": "obj", "plan": "obj", "reversible": "const:true",
         "inverseCmd": "str", "notes": "list"},
        payload={"prompt": "test", "flow": {}, "target": "web"},
        result=_ok(
            mock={"service": "web", "testUri": "http://localhost:3000",
                  "inverseCmd": "docker compose down -v"},
            plan={"steps": [], "needsMock": False},
            reversible=True,
            inverseCmd="docker compose down -v",
            notes=["Generic static web server for testing web-navigation flows."],
        ),
    ),

    "twin://host/mock/command/start-probe-stop": _command(
        {"prompt": "?str", "flow": "?obj", "target": "?str", "health_timeout": "?num"},
        {"ok": "const:true", "mock": "obj", "reachable": "bool", "reversible": "const:true",
         "simulated": "bool", "testUri": "?str", "proof": "?str", "note": "?str"},
        payload={"prompt": "test", "flow": {}, "target": "web", "health_timeout": 1.0},
        result=_ok(
            mock={"service": "web", "testUri": "http://localhost:3000"},
            reachable=False,
            reversible=True,
            simulated=True,
            note="Docker not found - reversibility is structural (compose down -v removes all state)",
        ),
    ),

    "twin://host/sandbox/command/probe": _command(
        {"image": "?str", "scan_cmd": "?str", "forward_cmd": "?str", "inverse_cmd": "?str",
         "setup_cmd": "?str", "uri": "?str"},
        {"ok": "const:true", "connector": "const:twin", "scenario": "obj", "simulated": "bool",
         "exitCode": "int", "before": "str", "after": "str", "restored": "str",
         "changed": "bool", "reversible": "bool", "verdict": "str"},
        payload={"forward_cmd": "touch /data/x.txt", "inverse_cmd": "rm -f /data/x.txt"},
        result=_ok(
            connector="twin",
            scenario={"image": "alpine:3"},
            simulated=True,
            exitCode=0,
            before="",
            after="x.txt",
            restored="",
            changed=True,
            reversible=True,
            verdict="reversible",
        ),
    ),

    "twin://host/flow/command/preflight": _command(
        {"steps": "?list", "node": "?str"},
        {"ok": "const:true", "timeline": "list", "provisioned": "list", "targets": "list",
         "count": "int"},
        payload={"steps": []},
        result=_ok(timeline=[], provisioned=[], targets=[], count=0),
    ),

    "twin://host/flow/goal/query/verify": Contract(
        version="v1",
        effect="query",
        inp={"goal": "?obj", "results": "?obj"},
        out={"ok": "bool", "goalMet": "bool", "skipped": "?str", "error": "?str"},
        errors=STATEFUL_ERRORS,
        examples=(
            {"payload": {"goal": {}, "results": {}},
             "result": {"ok": True, "goalMet": True, "skipped": "no-goal-uri"}},
        ),
    ),

    "twin://host/flow/command/rollback-ledger": _command(
        {"ledger": "?list", "mesh": "?obj"},
        {"ok": "bool", "undone": "list", "note": "?str", "stuck": "?str", "reason": "?str",
         "error": "?str"},
        payload={"ledger": []},
        result=_ok(undone=[], note="empty ledger"),
    ),

    "twin://host/step/command/evaluate": _command(
        {"step": "obj", "entry": "obj", "routes": "?list", "execute": "?bool",
         "attempt": "?int", "max_retries": "?int", "healed": "?bool"},
        {"ok": "const:true", "next": "enum:retry|heal|rollback", "reason": "?str",
         "diagnosis": "?obj"},
        payload={"step": {"id": "s1", "uri": "kvm://host/screen/query/capture"},
                 "entry": {"error": {"category": "NETWORK"}}},
        result=_ok(next="rollback", reason="NETWORK"),
    ),

    "twin://host/flow/command/execute": _command(
        {"flow": "obj", "execute": "?bool", "max_retries": "?int",
         "max_remediations": "?int", "max_wall_clock": "?num"},
        {"ok": "bool", "timeline": "?list", "result": "?any", "error": "?any"},
        payload={"flow": {"steps": []}, "execute": False},
        result=_ok(timeline=[]),
    ),

    "twin://host/flow/query/recall": Contract(
        version="v1",
        effect="query",
        inp={"prompt": "?str", "env_fp": "?str", "episode_id": "?str", "node": "?str",
             "skip_drift_check": "?bool"},
        out={"ok": "const:true", "found": "bool", "steps": "list", "source": "?str",
             "episode_id": "?str", "goal": "?any", "flow_key": "?str",
             "driftDetected": "?bool", "driftUnchecked": "?bool", "reason": "?str"},
        errors=STATEFUL_ERRORS,
        examples=(
            {"payload": {"prompt": "not-found-test", "skip_drift_check": True},
             "result": {"ok": True, "found": False, "steps": []}},
        ),
    ),

    "twin://host/experience/query/retrieve": Contract(
        version="v1",
        effect="query",
        inp={"intent": "?str", "fingerprint": "?str", "env_fp": "?str", "k": "?int",
             "node": "?str", "routes": "?list"},
        out={"ok": "const:true", "kind": "const:experience-retrieval", "intent": "str",
             "fingerprint": "?str", "node": "str", "k": "int", "episodes": "list",
             "flows": "list", "routes": "list", "preferences": "list", "index": "obj",
             "note": "str"},
        errors=STATEFUL_ERRORS,
        examples=(
            {"payload": {"intent": "take screenshot", "fingerprint": "env-test", "k": 3},
             "result": {"ok": True, "kind": "experience-retrieval",
                        "intent": "take screenshot", "fingerprint": "env-test",
                        "node": "host", "k": 3, "episodes": [], "flows": [],
                        "routes": [], "preferences": [],
                        "index": {"kind": "derived", "fingerprint": "abc",
                                  "source": "TwinMemory+routes", "embedding": {}},
                        "note": "retrieval returns candidates only; router/contract/env gates decide admissibility"}},
        ),
    ),

    "twin://host/flow/episode/command/run": _command(
        {"episode_id": "str", "execute": "?bool", "max_retries": "?int",
         "max_remediations": "?int", "max_wall_clock": "?num"},
        {"ok": "bool", "found": "?bool", "error": "?obj", "timeline": "?list"},
        payload={"episode_id": "missing-episode", "execute": False},
        result={"ok": False, "found": False,
                "error": {"category": "NOT_FOUND", "message": "episode not found"}},
    ),

    "twin://host/flow/command/diagnose": _command(
        {"error": "obj", "step": "?obj", "routes": "?list", "environment": "?obj", "surface": "?obj"},
        {"ok": "const:true", "found": "bool", "rule": "?str", "cause": "?str",
         "confidence": "?num", "remediation": "?list", "autoApplicable": "?any"},
        payload={"error": {"message": "connection refused"},
                 "step": {"uri": "kvm://host/cdp/page/command/navigate"}},
        result=_ok(found=True, rule="service-stopped", cause="service unavailable",
                   confidence=0.8, remediation=[], autoApplicable=[]),
    ),

    "twin://host/monitor/event": _command(
        {"node": "?str", "stateSig": "?str", "narration": "?str"},
        {"ok": "const:true", "node": "str", "stateSig": "str", "narration": "str",
         "received": "const:true"},
        payload={"node": "host", "stateSig": "env-1", "narration": "ready"},
        result=_ok(node="host", stateSig="env-1", narration="ready", received=True),
        errors=(),
    ),
}
