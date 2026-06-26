# Author: Tom Sapletta · https://tom.sapletta.com
# Part of the ifURI solution.
#
# Tests for the connector-side proof cache (proof_cache.py).
# Four structural paths, route-handler contract, scenario.signature stability.
# No Docker, no live sandbox — probe_fn is always a stub.
from __future__ import annotations

import unittest

from urirun_connector_twin.proof_cache import (
    DictProofStore,
    preflight_step,
    proof_check,
    proof_key,
    proof_record,
)
from urirun_connector_twin.sandbox import Scenario, BUILTIN_SCENARIOS


# ──────────────────────────────────────── scenario.signature ──── #

class TestScenarioSignature(unittest.TestCase):

    def test_signature_is_stable(self):
        sc = BUILTIN_SCENARIOS["fs"]
        self.assertEqual(sc.signature(), sc.signature())

    def test_signature_changes_on_inverse_change(self):
        sc_a = BUILTIN_SCENARIOS["fs"]
        sc_b = Scenario(**{**BUILTIN_SCENARIOS["fs"].__dict__, "inverse_cmd": "rm -rf /data"})
        self.assertNotEqual(sc_a.signature(), sc_b.signature())

    def test_signature_changes_on_forward_change(self):
        sc_a = BUILTIN_SCENARIOS["fs"]
        sc_b = Scenario(**{**BUILTIN_SCENARIOS["fs"].__dict__, "forward_cmd": "touch /data/other.txt"})
        self.assertNotEqual(sc_a.signature(), sc_b.signature())


# ──────────────────────────────────────── proof_key ──── #

class TestProofKey(unittest.TestCase):

    def setUp(self):
        self.sc = BUILTIN_SCENARIOS["fs"]
        self.uri = "fs://host/file/command/write"
        self.env = "env-d6a3c67fdb"

    def test_proof_key_is_stable(self):
        k1 = proof_key(self.uri, self.sc, self.env)
        k2 = proof_key(self.uri, self.sc, self.env)
        self.assertEqual(k1, k2)

    def test_proof_key_starts_with_pf(self):
        self.assertTrue(proof_key(self.uri, self.sc, self.env).startswith("pf-"))

    def test_proof_key_changes_on_env_drift(self):
        k1 = proof_key(self.uri, self.sc, "env-AAAA")
        k2 = proof_key(self.uri, self.sc, "env-BBBB")
        self.assertNotEqual(k1, k2)

    def test_proof_key_changes_on_scenario_change(self):
        sc2 = Scenario(**{**self.sc.__dict__, "inverse_cmd": "echo different"})
        self.assertNotEqual(proof_key(self.uri, self.sc, self.env),
                            proof_key(self.uri, sc2, self.env))


# ──────────────────────────────────────── route handlers ──── #

class TestRouteHandlers(unittest.TestCase):

    def setUp(self):
        self.store = DictProofStore()
        self.sc = BUILTIN_SCENARIOS["fs"]
        self.uri = "fs://host/file/command/write"
        self.env = "env-d6a3c67fdb"
        self.key = proof_key(self.uri, self.sc, self.env)

    def test_proof_check_miss(self):
        r = proof_check({"proof_key": self.key}, self.store)
        self.assertTrue(r["ok"])
        self.assertFalse(r["hit"])

    def test_proof_check_hit_after_record(self):
        proof_record({"proof_key": self.key, "verdict": "reversible",
                      "uri": self.uri, "env_fingerprint": self.env,
                      "scenario_signature": self.sc.signature(), "ts": "2026-06-26T10:00:00Z"},
                     self.store)
        r = proof_check({"proof_key": self.key}, self.store)
        self.assertTrue(r["hit"])
        self.assertEqual(r["verdict"], "reversible")
        self.assertEqual(r["proven_at"], "2026-06-26T10:00:00Z")

    def test_proof_record_stores_positive_verdict(self):
        r = proof_record({"proof_key": self.key, "verdict": "reversible",
                          "uri": self.uri, "env_fingerprint": self.env,
                          "scenario_signature": self.sc.signature(), "ts": "t"}, self.store)
        self.assertTrue(r["ok"])
        self.assertTrue(r["recorded"])
        self.assertIn(self.key, self.store)

    def test_proof_record_does_not_store_negative_verdict(self):
        r = proof_record({"proof_key": self.key, "verdict": "irreversible"}, self.store)
        self.assertTrue(r["ok"])
        self.assertFalse(r["recorded"])
        self.assertNotIn(self.key, self.store)

    def test_proof_check_missing_key_returns_error(self):
        r = proof_check({}, self.store)
        self.assertFalse(r["ok"])


# ──────────────────────────────────────── four preflight paths ──── #

class TestPreflightPaths(unittest.TestCase):
    """Structural proof of the four decision paths.

    probes_run counter is the observable: it only increments when the sandbox
    actually runs — so `probes_run unchanged` proves the sandbox was skipped."""

    def setUp(self):
        self.store = DictProofStore()
        self.sc = BUILTIN_SCENARIOS["fs"]
        self.uri = "fs://host/file/command/write"

    def _reversible_probe(self):
        self.probes_run += 1
        return {"reversible": True, "before": "[]", "after": "[x]"}

    def _irreversible_probe(self):
        self.probes_run += 1
        return {"reversible": False}

    def test_path1_new_env_miss_probe_proven_cached(self):
        """New env → miss → sandbox → proven + record."""
        self.probes_run = 0
        r = preflight_step(self.uri, self.sc, "env-d6a3c67fdb",
                           self.store, lambda s: self._reversible_probe())
        self.assertEqual(r["decision"], "proven")
        self.assertEqual(self.probes_run, 1)
        self.assertIn(r["proof_key"], self.store)
        self.assertEqual(r["next"]["kind"], "continue")

    def test_path2_same_env_hit_sandbox_skipped(self):
        """Same env after path 1 → hit → skip (sandbox NOT run)."""
        self.probes_run = 0
        preflight_step(self.uri, self.sc, "env-d6a3c67fdb",
                       self.store, lambda s: self._reversible_probe())
        before = self.probes_run
        r = preflight_step(self.uri, self.sc, "env-d6a3c67fdb",
                           self.store, lambda s: self._reversible_probe())
        self.assertEqual(r["decision"], "skip")
        self.assertEqual(self.probes_run, before)   # counter unchanged = sandbox not run

    def test_path3_env_drift_different_key_re_probed(self):
        """Env drift → new fingerprint → miss → sandbox re-runs."""
        self.probes_run = 0
        r1 = preflight_step(self.uri, self.sc, "env-d6a3c67fdb",
                             self.store, lambda s: self._reversible_probe())
        r3 = preflight_step(self.uri, self.sc, "env-99newenv99",
                             self.store, lambda s: self._reversible_probe())
        self.assertEqual(r3["decision"], "proven")
        self.assertEqual(self.probes_run, 2)                  # re-probed in new env
        self.assertNotEqual(r1["proof_key"], r3["proof_key"]) # drift → different key
        self.assertIn(r3["proof_key"], self.store)

    def test_path4_negative_block_not_cached(self):
        """Irreversible → block + NOT cached → retry can prove if env changes."""
        self.probes_run = 0
        sc_net = Scenario(scan_cmd="ss -tan", forward_cmd="true", inverse_cmd="true")
        uri = "net://host/socket/command/open"
        env = "env-d6a3c67fdb"

        b1 = preflight_step(uri, sc_net, env, self.store,
                             lambda s: self._irreversible_probe())
        self.assertEqual(b1["decision"], "block")
        self.assertEqual(b1["next"]["kind"], "rollback")
        self.assertNotIn(b1["proof_key"], self.store)   # negative NOT cached

        # A subsequent retry (same key) can still prove when sandbox is ready.
        self.probes_run = 0
        b2 = preflight_step(uri, sc_net, env, self.store,
                             lambda s: self._reversible_probe())
        self.assertEqual(b2["decision"], "proven")      # not stuck


# ──────────────────────────────────────── only positives in store ──── #

class TestStoreContainsOnlyPositives(unittest.TestCase):

    def test_store_shows_only_positive_entries(self):
        store = DictProofStore()
        sc_fs = BUILTIN_SCENARIOS["fs"]
        sc_net = Scenario(scan_cmd="ss -tan", forward_cmd="true", inverse_cmd="true")

        probes: dict[str, int] = {}

        def rev_probe(s):
            probes["n"] = probes.get("n", 0) + 1
            return {"reversible": True}

        def irr_probe(s):
            probes["n"] = probes.get("n", 0) + 1
            return {"reversible": False}

        # env-A: fs reversible → stored
        preflight_step("fs://h/f", sc_fs, "env-A", store, rev_probe)
        # env-B: fs reversible (drift) → stored
        preflight_step("fs://h/f", sc_fs, "env-B", store, rev_probe)
        # env-A: net irreversible → NOT stored
        preflight_step("net://h/s", sc_net, "env-A", store, irr_probe)

        self.assertEqual(len(store), 2)
        for rec in store.values():
            self.assertEqual(rec["verdict"], "reversible")
