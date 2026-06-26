"""Docker mock generator: when a target is unreachable or a step is infeasible,
generate a minimal Docker Compose environment for isolated testing.

The mock is designed to be:
  - reversible: `docker compose down -v` removes all state
  - self-contained: no credentials required for the container layer
  - probe-ready: the same twin connector can re-probe the mock environment

Each mock includes:
  - docker_compose: YAML string to write to docker-compose.yml
  - start_cmd / stop_cmd: shell commands (reversible pair)
  - test_uri: the local URI to use instead of the real target
  - notes: what the mock cannot simulate (auth, live data, etc.)
"""
from __future__ import annotations

import textwrap


_SERVICE_MOCKS: dict[str, dict] = {
    "linkedin": {
        "image": "httpd:2.4-alpine",
        "port": 3001,
        "test_uri": "http://localhost:3001",
        "notes": [
            "Static HTML only — no authentication, no real feed.",
            "Use for testing CDP DOM navigation + fill routes.",
            "Login flows require a real CDP session with a saved profile.",
        ],
        "env": {},
    },
    "browser": {
        "image": "selenium/standalone-chrome:latest",
        "port": 4444,
        "test_uri": "http://localhost:4444",
        "notes": [
            "Selenium grid with Chrome — CDP available on port 9222 inside the container.",
            "Use for testing CDP navigate/fill/click without a local Chrome install.",
        ],
        "env": {"SE_NODE_MAX_SESSIONS": "2"},
    },
    "web": {
        "image": "httpd:2.4-alpine",
        "port": 3000,
        "test_uri": "http://localhost:3000",
        "notes": ["Generic static web server for testing web-navigation flows."],
        "env": {},
    },
}

_DEFAULT_MOCK = {
    "image": "httpd:2.4-alpine",
    "port": 3000,
    "test_uri": "http://localhost:3000",
    "notes": ["Generic HTTP server — replace with a service-specific image."],
    "env": {},
}


def _detect_service(prompt: str, uris: list[str]) -> str:
    text = (prompt + " " + " ".join(uris)).lower()
    for svc in _SERVICE_MOCKS:
        if svc in text:
            return svc
    return "web"


def _resolve_service(target: str | None, prompt: str, uris: list[str]) -> str:
    """Resolve a service key from an optional target domain or prompt/URIs."""
    if target:
        # exact key match (e.g. "linkedin")
        if target in _SERVICE_MOCKS:
            return target
        # domain match (e.g. "linkedin.com" → "linkedin")
        for svc in _SERVICE_MOCKS:
            if svc in target.lower():
                return svc
    return _detect_service(prompt, uris)


def _compose_yaml(service: str, spec: dict) -> str:
    env_lines = "\n".join(f"      - {k}={v}" for k, v in spec["env"].items())
    env_block = f"\n    environment:\n{env_lines}" if env_lines else ""
    return textwrap.dedent(f"""\
        version: "3.9"
        services:
          {service}-mock:
            image: {spec['image']}
            ports:
              - "{spec['port']}:{spec['port']}"{env_block}
            restart: "no"
    """)


def generate_mock(prompt: str, plan: dict, target: str | None = None) -> dict:
    """Return a Docker mock spec for the given plan's infeasible/unreachable steps."""
    infeasible_uris = [s["uri"] for s in plan.get("steps", []) if not s.get("feasible")]
    all_uris = [s["uri"] for s in plan.get("steps", [])]
    svc = _resolve_service(target, prompt, infeasible_uris or all_uris)
    spec = _SERVICE_MOCKS.get(svc, _DEFAULT_MOCK)
    compose = _compose_yaml(svc, spec)
    return {
        "service": svc,
        "image": spec["image"],
        "port": spec["port"],
        "testUri": spec["test_uri"],
        "dockerCompose": compose,
        "startCmd": f"docker compose up -d  # starts {svc}-mock on port {spec['port']}",
        "stopCmd": "docker compose down -v  # reversible: removes all state",
        "reversible": True,
        "inverseCmd": "docker compose down -v",
        "notes": spec["notes"],
        "infeasibleStepsAddressed": infeasible_uris,
    }
