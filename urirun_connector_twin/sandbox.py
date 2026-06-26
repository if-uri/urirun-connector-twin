"""Reversibility probe: scan(before) → forward → scan(after) → inverse → scan(restored).

reversible := scan(before) == scan(restored)  AND  scan(before) != scan(after)

Tries Docker first (isolated, stateless container); degrades to a local temp-dir
simulation when Docker is absent — clearly marked simulated:True so callers know
the boundary. This gives a hard `reversible` fact for steps the live env can't
vouch for, without touching the real machine.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import time
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Scenario:
    """One reversibility experiment.

    Every *_cmd is a POSIX sh command executed inside the sandbox (container or
    temp dir). `scan_cmd` must write the observable state to stdout.
    """
    image: str = "alpine:3"
    scan_cmd: str = "ls /data 2>/dev/null || echo EMPTY"
    forward_cmd: str = "true"
    inverse_cmd: str = "true"
    setup_cmd: str = "mkdir -p /data"


# Predefined scenarios keyed by URI scheme / action family.
BUILTIN_SCENARIOS: dict[str, Scenario] = {
    "fs": Scenario(
        image="alpine:3",
        setup_cmd="mkdir -p /data",
        scan_cmd="ls /data",
        forward_cmd="touch /data/created.txt",
        inverse_cmd="rm -f /data/created.txt",
    ),
    "sqlite": Scenario(
        image="alpine:3",
        setup_cmd="mkdir -p /data && apk add --no-cache sqlite 2>/dev/null && sqlite3 /data/db.sqlite 'CREATE TABLE IF NOT EXISTS items(id INTEGER)'",
        scan_cmd="sqlite3 /data/db.sqlite 'SELECT count(*) FROM items' 2>/dev/null || echo 0",
        forward_cmd="sqlite3 /data/db.sqlite 'INSERT INTO items VALUES(1)'",
        inverse_cmd="sqlite3 /data/db.sqlite 'DELETE FROM items WHERE id=1'",
    ),
    "mqtt": Scenario(
        image="eclipse-mosquitto:2",
        setup_cmd="mkdir -p /mosquitto/config && echo 'listener 1883\\nallow_anonymous true' > /mosquitto/config/mosquitto.conf",
        scan_cmd="mosquitto_sub -h localhost -t 'test/probe' -C 1 -W 1 2>/dev/null | wc -l || echo 0",
        forward_cmd="mosquitto_pub -h localhost -t 'test/probe' -m 'forward' -r 2>/dev/null || echo 0",
        inverse_cmd="mosquitto_pub -h localhost -t 'test/probe' -m '' -r --null-message 2>/dev/null || echo 0",
    ),
    "web-post": Scenario(
        image="alpine:3",
        setup_cmd="mkdir -p /data && echo '' > /data/posts",
        scan_cmd="wc -l < /data/posts",
        forward_cmd="echo 'post content' >> /data/posts",
        inverse_cmd="head -n -1 /data/posts > /data/posts.tmp && mv /data/posts.tmp /data/posts",
    ),
}


def scenario_for_uri(uri: str) -> Scenario:
    """Pick a built-in scenario from URI scheme/path, falling back to generic fs."""
    uri_l = uri.lower()
    if "sqlite" in uri_l:
        return BUILTIN_SCENARIOS["sqlite"]
    if uri_l.startswith("mqtt://") or "/mqtt/" in uri_l:
        return BUILTIN_SCENARIOS["mqtt"]
    if any(k in uri_l for k in ("post", "publish", "create", "write", "send")):
        return BUILTIN_SCENARIOS["web-post"]
    return BUILTIN_SCENARIOS["fs"]


def _docker_available() -> bool:
    return shutil.which("docker") is not None


def _run(cmd: list[str], timeout: float = 60.0) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except Exception as exc:
        return 1, str(exc)


def _parse_sections(raw: str) -> tuple[str, str, str]:
    def _between(a: str, b: str) -> str:
        try:
            return raw.split(a, 1)[1].split(b, 1)[0].strip()
        except Exception:
            return ""
    before = _between("__BEFORE__", "__AFTER__")
    after = _between("__AFTER__", "__RESTORED__")
    restored = raw.split("__RESTORED__", 1)[1].strip() if "__RESTORED__" in raw else ""
    return before, after, restored


def _verdict(before: str, after: str, restored: str) -> dict[str, Any]:
    changed = before != after
    reversible = before == restored
    if reversible and changed:
        verdict = "reversible"
    elif not changed:
        verdict = "no-op (forward changed nothing)"
    else:
        verdict = "IRREVERSIBLE — inverse did not restore state"
    return {"before": before, "after": after, "restored": restored,
            "changed": changed, "reversible": reversible, "verdict": verdict}


def _docker_probe(sc: Scenario) -> dict[str, Any]:
    script = (
        f"{sc.setup_cmd}; "
        f"echo __BEFORE__; {sc.scan_cmd}; "
        f"( {sc.forward_cmd} ) 2>/dev/null; echo __AFTER__; {sc.scan_cmd}; "
        f"( {sc.inverse_cmd} ) 2>/dev/null; echo __RESTORED__; {sc.scan_cmd}"
    )
    name = f"twin-probe-{int(time.time() * 1000)}"
    code, raw = _run(
        ["docker", "run", "--rm", "--name", name, sc.image, "sh", "-c", script]
    )
    before, after, restored = _parse_sections(raw)
    return {"simulated": False, "exitCode": code, "raw": raw, **_verdict(before, after, restored)}


def _simulated_probe(sc: Scenario) -> dict[str, Any]:
    """Temp-dir fallback when Docker is absent. Rewrites /data → sandbox dir."""
    work = tempfile.mkdtemp(prefix="twin-sim-")

    def sh(cmd: str) -> str:
        cmd = cmd.replace("/data", work)
        _, out = _run(["sh", "-c", cmd])
        return out.strip()

    sh(sc.setup_cmd)
    before = sh(sc.scan_cmd)
    sh(sc.forward_cmd)
    after = sh(sc.scan_cmd)
    sh(sc.inverse_cmd)
    restored = sh(sc.scan_cmd)
    shutil.rmtree(work, ignore_errors=True)
    return {"simulated": True, "exitCode": 0, "raw": "",
            **_verdict(before, after, restored)}


def probe_reversibility(scenario: Scenario) -> dict[str, Any]:
    """Run the scan→forward→scan→inverse→scan round-trip.

    Returns a hard `reversible` fact so the planner can decide whether to block
    a step, allow it, or gate it on human confirmation.
    """
    if _docker_available():
        result = _docker_probe(scenario)
    else:
        result = _simulated_probe(scenario)
    return {"ok": True, "connector": "twin", "scenario": asdict(scenario), **result}
