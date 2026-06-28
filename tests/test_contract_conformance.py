# Author: Tom Sapletta · https://tom.sapletta.com
# Part of the ifURI solution.
"""Conformance gate for the twin connector's route contracts.

All live twin routes must have a route-level contract. Live-output conformance is still limited to
deterministic probe handlers, but coverage and dangling guards are now strict so the autonomous
planning surface cannot grow undocumented routes.
"""
from __future__ import annotations

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
    assert not uncovered, (
        f"twin contract coverage {len(contracted)}/{len(live)}; "
        f"{len(uncovered)} uncovered: {uncovered}"
    )


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
