# Author: Tom Sapletta · https://tom.sapletta.com
# Part of the ifURI solution.
#
# Integration test for the twin://{node}/proof/* routes wired in core.py: they bind the
# proof_cache.py gate logic to the durable core "_proofs" store (durable_memory().proof_store).
# The sandbox probe is patched, so no Docker / served mesh is needed.
import os
import shutil
import tempfile
import unittest
from unittest import mock

from urirun_connector_twin import core


class TestProofRoutes(unittest.TestCase):

    URI = "fs://host/data/command/write"
    ENV = "env-aaa"

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="proof-routes-")
        self.path = os.path.join(self.tmp, "twin-memory.json")
        self._old = os.environ.get("URIRUN_TWIN_MEMORY")
        os.environ["URIRUN_TWIN_MEMORY"] = self.path

    def tearDown(self):
        if self._old is None:
            os.environ.pop("URIRUN_TWIN_MEMORY", None)
        else:
            os.environ["URIRUN_TWIN_MEMORY"] = self._old
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_check_miss_then_gate_probes_records_then_skip(self):
        # cold check → miss
        chk = core.proof_check_route(uri=self.URI, env_fingerprint=self.ENV)
        self.assertFalse(chk["hit"])
        # gate with a patched reversible probe → proven + recorded
        with mock.patch("urirun_connector_twin.proof_cache.probe_reversibility",
                        return_value={"reversible": True, "before": "x", "after": "y"}) as p:
            res = core.proof_gate_route(uri=self.URI, env_fingerprint=self.ENV)
        self.assertEqual(res["decision"], "proven")
        p.assert_called_once()
        # now durably cached → check hits, and the gate skips without probing
        self.assertTrue(core.proof_check_route(uri=self.URI, env_fingerprint=self.ENV)["hit"])
        with mock.patch("urirun_connector_twin.proof_cache.probe_reversibility") as p2:
            res2 = core.proof_gate_route(uri=self.URI, env_fingerprint=self.ENV)
        self.assertEqual(res2["decision"], "skip")
        p2.assert_not_called()

    def test_drift_reprobes(self):
        with mock.patch("urirun_connector_twin.proof_cache.probe_reversibility",
                        return_value={"reversible": True}):
            core.proof_gate_route(uri=self.URI, env_fingerprint=self.ENV)
        # a different env fingerprint → new key → cache miss → re-probe
        with mock.patch("urirun_connector_twin.proof_cache.probe_reversibility",
                        return_value={"reversible": True}) as p:
            core.proof_gate_route(uri=self.URI, env_fingerprint="env-bbb")
        p.assert_called_once()

    def test_irreversible_blocks_and_records_nothing(self):
        with mock.patch("urirun_connector_twin.proof_cache.probe_reversibility",
                        return_value={"reversible": False, "verdict": "IRREVERSIBLE"}):
            res = core.proof_gate_route(uri=self.URI, env_fingerprint=self.ENV)
        self.assertEqual(res["decision"], "block")
        self.assertFalse(core.proof_check_route(uri=self.URI, env_fingerprint=self.ENV)["hit"])

    def test_record_route_rejects_negative(self):
        rec = core.proof_record_route(uri=self.URI, env_fingerprint=self.ENV, verdict="irreversible")
        self.assertFalse(rec["recorded"])
        self.assertFalse(core.proof_check_route(uri=self.URI, env_fingerprint=self.ENV)["hit"])


if __name__ == "__main__":
    unittest.main()
