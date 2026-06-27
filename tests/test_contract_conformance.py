# Author: Tom Sapletta · https://tom.sapletta.com
# Part of the ifURI solution.
"""Conformance gate for the twin connector's route contracts (deterministic subset).

twin is mostly LLM/stateful; this covers the pure-probe routes with live-output conformance and
surfaces the still-uncovered routes via a warning (no silent gaps). The dangling guard hard-fails if
a contract points at a route that no longer exists.
"""
from __future__ import annotations

import warnings

import urirun_connector_twin.core as core
from urirun_connector_twin.contracts import CONTRACTS
from urirun_connectors_toolkit.contract_gate import conform, envelope_violation


def test_contracts_conform():
    conform(CONTRACTS)


def test_no_dangling_and_report_coverage():
    live = set(core.conn.bindings()["bindings"])
    contracted = set(CONTRACTS)
    dangling = contracted - live
    assert not dangling, f"contracts point at routes that no longer exist: {sorted(dangling)}"
    uncovered = sorted(live - contracted)
    if uncovered:
        warnings.warn(
            f"twin contract coverage {len(contracted)}/{len(live)}; {len(uncovered)} uncovered "
            f"(LLM/stateful routes pending): {uncovered}", stacklevel=2)


def test_live_output_conforms_to_contract():
    """Run the deterministic probe handlers and assert live output conforms."""
    cases = [
        ("twin://host/environment/query/profile", lambda: core.environment_profile()),
        ("twin://host/constraints/query/from-profile", lambda: core.constraints_from_profile(actionMatrix={})),
        ("twin://host/step/query/feasibility", lambda: core.step_feasibility(uri="kvm://host/screen/query/capture")),
    ]
    for uri, run in cases:
        env = run()
        bad = envelope_violation(CONTRACTS[uri], env)
        assert bad is None, f"{uri}: live output violates contract: {bad}\nenvelope={env}"
