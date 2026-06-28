# Author: Tom Sapletta · https://tom.sapletta.com
# Part of the ifURI solution.
"""Route contracts for the twin connector (LLM-editable declaration).

twin is large and mostly LLM/stateful (plan/mock/flow/proof/browser/sandbox routes need a model, a
live Chrome, or a twin store). This declares the DETERMINISTIC, pure-probe subset — environment /
constraints / step-feasibility — which the gate verifies by REAL execution. The remaining routes are
surfaced by the coverage report (no silent gaps), to be contracted as they become testable.

Single scheme but declared via the shared connector; contract keys are FULL URIs joined via
``attach_contracts(None, CONTRACTS)``.
"""
from __future__ import annotations

from urirun_connectors_toolkit.contract_gate import Contract

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
}
