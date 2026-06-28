"""Derived retrieval layer for Digital Twin experience memory.

Retrieval is a PROPOSE-stage helper: it returns candidates with provenance and
scores. It never accepts, rejects or executes a plan. Deterministic admission
stays in router/contract/env gates.
"""
from __future__ import annotations

import hashlib
import importlib
import json
import math
import os
from typing import Any, Callable


Embedder = Callable[[list[str]], list[list[float]]]


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, default=str)


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(_stable_json(value).encode("utf-8")).hexdigest()[:16]


def _intent_signature(intent: str) -> str:
    from urirun.node.episode import intent_signature  # noqa: PLC0415
    return intent_signature(intent or "")


def _episode_steps(ep: dict) -> list:
    return list((ep.get("plan") or {}).get("steps") or [])


def _episode_fingerprint(ep: dict) -> str:
    return str((ep.get("reality") or {}).get("fingerprint") or "")


def _episode_goal(ep: dict) -> str:
    return str(ep.get("goal") or "")


def _flow_prompt(record: dict) -> str:
    return str(record.get("prompt") or record.get("goal") or "")


def _route_text(route: dict) -> str:
    meta = route.get("meta") if isinstance(route.get("meta"), dict) else {}
    contract = meta.get("contract") if isinstance(meta.get("contract"), dict) else {}
    return _stable_json({
        "uri": route.get("uri"),
        "title": route.get("title") or route.get("label"),
        "kind": route.get("kind"),
        "inputSchema": route.get("inputSchema"),
        "contract": contract,
    })


def _load_embedder_from_env() -> tuple[Embedder | None, str | None, str | None]:
    spec = os.getenv("URIRUN_EXPERIENCE_EMBEDDER", "").strip()
    if not spec:
        return None, None, "URIRUN_EXPERIENCE_EMBEDDER is not configured"
    module_name, sep, attr = spec.partition(":")
    if not sep or not module_name or not attr:
        return None, spec, "URIRUN_EXPERIENCE_EMBEDDER must be module:function"
    try:
        module = importlib.import_module(module_name)
        fn = getattr(module, attr)
        return fn, spec, None
    except Exception as exc:  # noqa: BLE001
        return None, spec, f"{type(exc).__name__}: {exc}"


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if not na or not nb:
        return 0.0
    return dot / (na * nb)


def _rank_by_embedding(intent: str, docs: list[tuple[dict, str]], *,
                       embedder: Embedder | None = None) -> tuple[list[tuple[dict, float]], dict]:
    provider = "callable" if embedder is not None else None
    reason = None
    fn = embedder
    if fn is None:
        fn, provider, reason = _load_embedder_from_env()
    meta = {"configured": fn is not None, "provider": provider, "degradedReason": reason}
    if fn is None or not docs:
        return [], meta
    try:
        vectors = fn([intent, *[text for _item, text in docs]])
        if len(vectors) != len(docs) + 1:
            raise ValueError("embedder returned wrong vector count")
        query = vectors[0]
        ranked = [
            (item, _cosine(query, vec))
            for (item, _text), vec in zip(docs, vectors[1:])
        ]
        ranked.sort(key=lambda pair: pair[1], reverse=True)
        meta["degradedReason"] = None
        return ranked, meta
    except Exception as exc:  # noqa: BLE001
        meta["configured"] = False
        meta["degradedReason"] = f"{type(exc).__name__}: {exc}"
        return [], meta


def _eligible_episode(ep: dict, fingerprint: str) -> bool:
    if (ep.get("outcome") or {}).get("status") != "ok":
        return False
    if fingerprint and _episode_fingerprint(ep) != fingerprint:
        return False
    return bool(_episode_steps(ep))


def _episode_candidate(ep: dict, score: float | None, provenance: list[dict]) -> dict:
    return {
        "episode_id": ep.get("episode_id"),
        "goal": ep.get("goal"),
        "score": score,
        "fingerprint": _episode_fingerprint(ep),
        "steps": _episode_steps(ep),
        "ts": ep.get("ts"),
        "provenance": provenance,
    }


def _flow_candidate(key: str, rec: dict, score: float | None, provenance: list[dict]) -> dict:
    return {
        "flow_key": rec.get("flowKey") or key,
        "goal": _flow_prompt(rec),
        "score": score,
        "steps": list(rec.get("steps") or []),
        "ts": rec.get("ts"),
        "provenance": provenance,
    }


def _route_candidate(route: dict, score: float, provenance: list[dict]) -> dict:
    return {
        "uri": route.get("uri"),
        "title": route.get("title") or route.get("label") or route.get("uri"),
        "kind": route.get("kind"),
        "node": route.get("node"),
        "score": score,
        "inputSchema": route.get("inputSchema") or {"type": "object"},
        "contract": (route.get("meta") or {}).get("contract") or route.get("contract") or {},
        "provenance": provenance,
    }


def _preference_candidates(memory: Any, node: str, fingerprint: str, k: int) -> list[dict]:
    store = getattr(memory, "preference_store", None)
    values = store.values() if hasattr(store, "values") else []
    out = []
    for rec in values:
        if not isinstance(rec, dict):
            continue
        if node and rec.get("node") != node:
            continue
        if fingerprint and rec.get("fingerprint") != fingerprint:
            continue
        out.append({
            "node": rec.get("node"),
            "name": rec.get("name"),
            "value": rec.get("value"),
            "fingerprint": rec.get("fingerprint"),
            "ts": rec.get("ts"),
            "provenance": [{"edge": "preference", "kind": "exact"}],
        })
    return sorted(out, key=lambda item: str(item.get("ts") or ""), reverse=True)[:k]


def retrieve_experience(intent: str, fingerprint: str = "", *, k: int = 5, node: str = "host",
                        routes: list[dict] | None = None, memory: Any = None,
                        embedder: Embedder | None = None) -> dict:
    """Return retrieval candidates; never an accepted plan."""
    if memory is None:
        from urirun.node.twin_store import durable_memory  # noqa: PLC0415
        memory = durable_memory()
    k = max(1, int(k or 5))
    sig = _intent_signature(intent)
    episodes: list[dict] = []
    seen_episodes: set[str] = set()

    raw_episodes = [
        ep for ep in (memory.known_good_episodes() if hasattr(memory, "known_good_episodes") else [])
        if isinstance(ep, dict) and _eligible_episode(ep, fingerprint)
    ]
    for ep in raw_episodes:
        ep_sig = ep.get("intent_sig") or _intent_signature(_episode_goal(ep))
        if ep_sig != sig:
            continue
        eid = str(ep.get("episode_id") or "")
        seen_episodes.add(eid)
        provenance = [{"edge": "intent_sig", "kind": "exact"}]
        if fingerprint:
            provenance.append({"edge": "environment_fingerprint", "kind": "exact"})
        episodes.append(_episode_candidate(ep, 1.0, provenance))

    ranked_eps, embedding_meta = _rank_by_embedding(
        intent,
        [(ep, _episode_goal(ep)) for ep in raw_episodes if str(ep.get("episode_id") or "") not in seen_episodes],
        embedder=embedder,
    )
    for ep, score in ranked_eps:
        if len(episodes) >= k:
            break
        episodes.append(_episode_candidate(
            ep,
            score,
            [{"edge": "intent_embedding", "kind": "similarity", "provider": embedding_meta.get("provider")}],
        ))

    flows: list[dict] = []
    flow_store = getattr(memory, "flow_store", None)
    flow_items = flow_store.items() if hasattr(flow_store, "items") else []
    for key, rec in flow_items:
        if not isinstance(rec, dict) or rec.get("degraded"):
            continue
        if rec.get("intent_sig") == sig:
            flows.append(_flow_candidate(str(key), rec, 1.0, [{"edge": "intent_sig", "kind": "exact"}]))
    flows = sorted(flows, key=lambda item: str(item.get("ts") or ""), reverse=True)[:k]

    ranked_routes, route_embedding_meta = _rank_by_embedding(
        intent,
        [(route, _route_text(route)) for route in (routes or []) if isinstance(route, dict) and route.get("uri")],
        embedder=embedder,
    )
    route_candidates = [
        _route_candidate(route, score, [{"edge": "route_embedding", "kind": "similarity",
                                        "provider": route_embedding_meta.get("provider")}])
        for route, score in ranked_routes[:k]
    ]

    source_shape = {
        "intent": intent,
        "fingerprint": fingerprint,
        "episodes": raw_episodes,
        "flows": [(str(k), v) for k, v in flow_items],
        "routes": routes or [],
    }
    degraded = []
    for meta in (embedding_meta, route_embedding_meta):
        if meta.get("degradedReason") and meta.get("degradedReason") not in degraded:
            degraded.append(meta["degradedReason"])

    return {
        "kind": "experience-retrieval",
        "intent": intent,
        "fingerprint": fingerprint,
        "node": node,
        "k": k,
        "episodes": episodes[:k],
        "flows": flows[:k],
        "routes": route_candidates,
        "preferences": _preference_candidates(memory, node, fingerprint, k),
        "index": {
            "kind": "derived",
            "fingerprint": _fingerprint(source_shape),
            "source": "TwinMemory+routes",
            "embedding": {
                "configured": bool(embedding_meta.get("configured") or route_embedding_meta.get("configured")),
                "provider": embedding_meta.get("provider") or route_embedding_meta.get("provider"),
                "degradedReason": "; ".join(degraded) if degraded else None,
            },
        },
        "note": "retrieval returns candidates only; router/contract/env gates decide admissibility",
    }


__all__ = ["retrieve_experience"]
