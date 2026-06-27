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
}
