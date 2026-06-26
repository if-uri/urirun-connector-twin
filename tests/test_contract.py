"""Contract test suite for urirun-connector-twin.

Uses ConnectorContractSuite to verify universal connector invariants.
These tests complement the unit tests in test_twin_connector.py — they
exercise the bindings/registry/dispatch pipeline rather than individual
handler logic."""
from __future__ import annotations

import urirun_connector_twin as pkg
from urirun.connectors.connector_contract import ConnectorContractSuite


class TestTwinConnectorContract(ConnectorContractSuite):
    bindings_doc = pkg.bindings()
    dry_run_routes = None  # all routes

    # Twin handlers that are safe to dry-run without real system state:
    execute_cases = [
        # flow/goal/query/verify with no goal is always ok=True
        (
            "twin://host/flow/goal/query/verify",
            {"goal": {}, "results": {}},
            lambda data: data is not None,
        ),
        # rollback with empty ledger is ok=True with undone=[]
        (
            "twin://host/flow/command/rollback-ledger",
            {"ledger": []},
            lambda data: data is not None,
        ),
    ]
    allow_glob = "twin://**"

    def test_twin_routes_present(self):
        import urirun
        uris = {r["uri"] for r in urirun.list_routes(self.compile())}
        assert "twin://host/flow/command/rollback-ledger" in uris
        assert "twin://host/flow/goal/query/verify" in uris
        assert "twin://host/environment/query/profile" in uris
