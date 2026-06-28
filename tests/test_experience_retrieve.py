from __future__ import annotations

import os
import tempfile
import unittest

from urirun_connector_twin import core
from urirun_connector_twin.experience import retrieve_experience


def _episode(eid: str, goal: str, fp: str, steps: list[dict]) -> dict:
    from urirun.node.episode import intent_signature
    return {
        "episode_id": eid,
        "goal": goal,
        "intent_sig": intent_signature(goal),
        "plan": {"steps": steps},
        "reality": {"fingerprint": fp},
        "outcome": {"status": "ok"},
        "ts": "2026-01-01T00:00:00Z",
    }


def _memory():
    from urirun.node.twin_store import TwinMemory
    return TwinMemory()


def test_retrieve_exact_episode_is_filtered_by_fingerprint():
    mem = _memory()
    steps = [{"id": "capture", "uri": "kvm://host/screen/query/capture"}]
    mem.remember_episode(_episode("ep-good", "zrob zrzut ekranu", "env-a", steps))
    mem.remember_episode(_episode("ep-other-env", "zrob zrzut ekranu", "env-b", steps))

    result = retrieve_experience("zrob zrzut ekranu", "env-a", memory=mem)

    assert [item["episode_id"] for item in result["episodes"]] == ["ep-good"]
    assert result["episodes"][0]["score"] == 1.0
    assert result["episodes"][0]["provenance"] == [
        {"edge": "intent_sig", "kind": "exact"},
        {"edge": "environment_fingerprint", "kind": "exact"},
    ]
    assert result["index"]["embedding"]["configured"] is False
    assert "not configured" in result["index"]["embedding"]["degradedReason"]


def test_retrieve_does_not_fake_similarity_without_embedder():
    mem = _memory()
    mem.remember_episode(_episode(
        "ep-related",
        "open browser and capture linkedin",
        "env-a",
        [{"id": "capture", "uri": "kvm://host/screen/query/capture"}],
    ))

    result = retrieve_experience("zrob screenshot linkedin", "env-a", memory=mem)

    assert result["episodes"] == []
    assert result["routes"] == []
    assert result["note"].startswith("retrieval returns candidates only")


def test_retrieve_routes_are_similarity_candidates_when_embedder_is_explicit():
    def embedder(texts: list[str]) -> list[list[float]]:
        vectors = []
        for text in texts:
            vectors.append([1.0, 0.0] if "screen/query/capture" in text or "screenshot" in text else [0.0, 1.0])
        return vectors

    result = retrieve_experience(
        "screenshot",
        routes=[
            {"uri": "kvm://host/screen/query/capture", "kind": "query", "title": "Capture screen"},
            {"uri": "fs://host/dir/query/list", "kind": "query", "title": "List directory"},
        ],
        memory=_memory(),
        embedder=embedder,
    )

    assert result["routes"][0]["uri"] == "kvm://host/screen/query/capture"
    assert result["routes"][0]["provenance"][0]["kind"] == "similarity"
    assert result["index"]["embedding"]["configured"] is True


class TestExperienceRetrieveRoute(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="experience-retrieve-")
        self.path = os.path.join(self.tmp, "twin-memory.json")
        self._old = os.environ.get("URIRUN_TWIN_MEMORY")
        os.environ["URIRUN_TWIN_MEMORY"] = self.path

    def tearDown(self):
        if self._old is None:
            os.environ.pop("URIRUN_TWIN_MEMORY", None)
        else:
            os.environ["URIRUN_TWIN_MEMORY"] = self._old
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_route_returns_candidates_only_shape(self):
        from urirun.node.twin_store import durable_memory
        durable_memory().remember_episode(_episode(
            "ep-route",
            "capture screen",
            "env-route",
            [{"id": "capture", "uri": "kvm://host/screen/query/capture"}],
        ))

        result = core.experience_retrieve(intent="capture screen", fingerprint="env-route", k=2)

        assert result["ok"] is True
        assert result["kind"] == "experience-retrieval"
        assert result["episodes"][0]["episode_id"] == "ep-route"
        assert result["index"]["kind"] == "derived"
        assert "accepted" not in result
