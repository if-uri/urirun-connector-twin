"""Prompt → imperative plan: derives concrete URI steps from a natural language prompt
without a pre-built flow.  No LLM required — uses keyword + intent pattern matching
to produce a best-effort ordered step list that the twin planner can then annotate
with feasibility and reversibility.

For each recognized intent category, a step template is expanded with values
extracted from the prompt (URL, text, query terms, etc.).  Unknown/unrecognized
prompts get a single `env://host/intent/query/describe` fallback step.

This is the "gather grounding data from the prompt" half of the twin loop.
The other half (`annotate_steps`) handles feasibility against the live environment."""
from __future__ import annotations

import re
from typing import Any


# ─── intent patterns ─────────────────────────────────────────────────────────

def _extract_url(text: str) -> str | None:
    m = re.search(r"https?://[^\s\"'>]+", text)
    return m.group(0) if m else None


def _extract_domain(text: str) -> str | None:
    url = _extract_url(text)
    if url:
        m = re.match(r"https?://([^/]+)", url)
        return m.group(1) if m else None
    # e.g. "post on linkedin" → linkedin.com
    for svc in ("linkedin", "github", "google", "facebook", "twitter", "youtube"):
        if svc in text.lower():
            return f"{svc}.com"
    return None


def _extract_text_to_type(text: str) -> str:
    m = re.search(r'"([^"]+)"', text)
    if m:
        return m.group(1)
    for kw in ("write", "type", "enter", "fill", "wpisz", "napisz"):
        idx = text.lower().find(kw)
        if idx >= 0:
            after = text[idx + len(kw):].strip()
            if after:
                return after.split(".")[0].strip()[:200]
    return ""


def _extract_query(text: str) -> str:
    for kw in ("search for", "find", "szukaj", "znajdź"):
        idx = text.lower().find(kw)
        if idx >= 0:
            return text[idx + len(kw):].strip()[:200]
    return text.strip()[:100]


# ─── step templates ──────────────────────────────────────────────────────────

def _browser_open_steps(url: str) -> list[dict]:
    return [
        {"id": "session_ensure", "uri": "kvm://{node}/cdp/session/command/ensure",
         "payload": {"url": url}},
        {"id": "navigate", "uri": "kvm://{node}/cdp/page/command/navigate",
         "payload": {"url": url}},
        {"id": "page_ready", "uri": "kvm://{node}/cdp/session/query/ready",
         "payload": {}},
    ]


def _browser_fill_and_submit_steps(url: str, field_text: str) -> list[dict]:
    steps = _browser_open_steps(url)
    steps += [
        {"id": "fill_field", "uri": "kvm://{node}/cdp/page/command/fill",
         "payload": {"role": "textbox", "text": field_text}},
        {"id": "submit", "uri": "kvm://{node}/cdp/page/command/click",
         "payload": {"role": "button", "text": "Submit"}},
    ]
    return steps


def _post_on_social_steps(domain: str, content: str) -> list[dict]:
    url = f"https://{domain}"
    return [
        {"id": "session_ensure", "uri": "kvm://{node}/cdp/session/command/ensure",
         "payload": {"url": url}},
        {"id": "navigate_home", "uri": "kvm://{node}/cdp/page/command/navigate",
         "payload": {"url": url}},
        {"id": "page_ready", "uri": "kvm://{node}/cdp/session/query/ready",
         "payload": {}},
        {"id": "click_compose", "uri": "kvm://{node}/ui/command/click",
         "payload": {"role": "button", "text": "Start a post"}},
        {"id": "fill_post", "uri": "kvm://{node}/ui/command/fill",
         "payload": {"role": "textbox", "value": content or "New post"}},
        {"id": "click_publish", "uri": "kvm://{node}/ui/command/click",
         "payload": {"role": "button", "text": "Post"}},
    ]


def _search_steps(query: str) -> list[dict]:
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    return [
        {"id": "session_ensure", "uri": "kvm://{node}/cdp/session/command/ensure",
         "payload": {"url": url}},
        {"id": "navigate_search", "uri": "kvm://{node}/cdp/page/command/navigate",
         "payload": {"url": url}},
        {"id": "page_ready", "uri": "kvm://{node}/cdp/session/query/ready",
         "payload": {}},
    ]


def _screenshot_capture_payload(prompt: str) -> dict:
    try:
        from urirun_flow.flow_planner import _screenshot_capture_payload as _flow_payload  # noqa: PLC0415
        return _flow_payload(prompt)
    except Exception:  # noqa: BLE001 - twin can run without urirun-flow in minimal installs.
        low = prompt.lower()
        if any(kw in low for kw in (
            "all monitors", "all screens", "whole desktop", "entire desktop",
            "wszystkie monitory", "wszystkich monitorow", "wszystkich monitorw",
            "wszystkie ekrany", "caly pulpit", "calego pulpitu",
        )):
            return {"scope": "all", "monitor": -1}
        m = re.search(r"\bmonitor(?:ze|a|ow)?\s*(\d+)\b", low)
        if m:
            return {"monitor": max(1, int(m.group(1)))}
        m = re.search(r"\bmonitor(?:ze|a|ow)?\s+numer\s+(\d+)\b", low)
        if m:
            return {"monitor": max(1, int(m.group(1)))}
        m = re.search(r"\b(\d+)\s+monitor(?:ze|a|ow)?\b", low)
        if m:
            return {"monitor": max(1, int(m.group(1)))}
        m = re.search(r"\bnumer\s+(\d+)\s+monitor(?:ze|a|ow)?\b", low)
        if m:
            return {"monitor": max(1, int(m.group(1)))}
        ordinals = {
            "pierwszy": 1, "pierwszego": 1, "first": 1,
            "drugi": 2, "drugiego": 2, "second": 2,
            "trzeci": 3, "trzeciego": 3, "third": 3,
            "czwarty": 4, "czwartego": 4, "fourth": 4,
        }
        for word, number in ordinals.items():
            if re.search(rf"\b{re.escape(word)}\s+monitor\b|\bmonitor\s+{re.escape(word)}\b", low):
                return {"monitor": number}
        return {}


def _screenshot_steps(prompt: str = "") -> list[dict]:
    # kvm routes always use "host" as the URI authority — serviceMap dispatch routes them to the
    # selected node transparently.  `kvm://host/screen/query/capture` sent to lenovo's mesh
    # endpoint runs lenovo's local kvm handler (which also registers as kvm://host/...).
    # Do NOT use {node} here: kvm://lenovo/... is not in lenovo's own registry.
    return [
        {"id": "capture_screen", "uri": "kvm://host/screen/query/capture",
         "payload": _screenshot_capture_payload(prompt)},
    ]


def _file_write_steps(path: str, content: str) -> list[dict]:
    return [
        {"id": "write_file", "uri": "kvm://{node}/file/command/write",
         "payload": {"path": path, "content": content}},
    ]


def _service_start_steps(service: str) -> list[dict]:
    return [
        {"id": f"start_{service}", "uri": f"dashboard://host/service/{service}/start",
         "payload": {}},
    ]


def _service_stop_steps(service: str) -> list[dict]:
    return [
        {"id": f"stop_{service}", "uri": f"dashboard://host/service/{service}/stop",
         "payload": {}},
    ]


def _fallback_describe_steps(prompt: str) -> list[dict]:
    return [
        {"id": "describe_intent", "uri": "env://{node}/intent/query/describe",
         "payload": {"prompt": prompt}},
    ]


# ─── intent detection ─────────────────────────────────────────────────────────

_SOCIAL_VERBS = ("post", "publish", "share", "opublikuj", "udostępnij")
_SEARCH_VERBS = ("search", "find", "look up", "szukaj", "znajdź")
_FILL_VERBS = ("fill", "type", "enter", "write", "wpisz", "napisz")
_SCREEN_VERBS = ("screenshot", "capture screen", "zrzut ekranu")
_OPEN_VERBS = ("open", "navigate", "go to", "otwórz", "przejdź")
_SERVICE_START = ("start", "uruchom", "włącz")
_SERVICE_STOP = ("stop", "restart", "zatrzymaj", "wyłącz")


_TASK_RULES: list[tuple] = [
    # (verbs, location_check, task_type)
    # location_check: None=no check, "domain"=needs domain, "any"=needs url or domain
    (_SOCIAL_VERBS,  "domain", "social-post"),
    (_SEARCH_VERBS,  None,     "web-search"),
    (_FILL_VERBS,    "any",    "browser-fill"),
    (_OPEN_VERBS,    "any",    "browser-open"),
    (_SCREEN_VERBS,  None,     "screenshot"),
    (_SERVICE_START, None,     "service-start"),
    (_SERVICE_STOP,  None,     "service-stop"),
]


def _location_ok(check: str | None, domain: str | None, url: str | None) -> bool:
    if check is None:
        return True
    if check == "domain":
        return bool(domain)
    return bool(domain or url)


def _classify_task_type(low: str, domain: str | None, url: str | None) -> str:
    """Map a lowered prompt + extracted domain/url to a task-type string."""
    for verbs, loc, label in _TASK_RULES:
        if any(v in low for v in verbs) and _location_ok(loc, domain, url):
            return label
    return "browser-open" if url else "unknown"


def derive_task_target(prompt: str) -> dict:
    """Extract domain, content, and task type from a natural language prompt.

    Returns: {domain, url, content, needsAuth, taskType}"""
    low = prompt.lower()
    domain = _extract_domain(prompt)
    url = _extract_url(prompt)
    return {
        "domain": domain,
        "url": url,
        "content": _extract_text_to_type(prompt),
        "needsAuth": any(svc in low for svc in ("linkedin", "github", "facebook", "instagram", "twitter")),
        "taskType": _classify_task_type(low, domain, url),
    }


def _raw_steps_for_target(target: dict, prompt: str) -> list[dict]:
    """Return un-bound step list for a derive_task_target result."""
    task_type = target["taskType"]
    domain = target["domain"]
    url = target["url"]
    content = target["content"]
    nav_url = url or (f"https://{domain}" if domain else None)
    if task_type == "social-post" and domain:
        return _post_on_social_steps(domain, content)
    if task_type == "web-search":
        return _search_steps(_extract_query(prompt))
    if task_type == "browser-fill" and nav_url:
        return _browser_fill_and_submit_steps(nav_url, content)
    if task_type == "browser-open" and nav_url:
        return _browser_open_steps(nav_url)
    if task_type == "screenshot":
        return _screenshot_steps(prompt)
    if task_type == "service-start":
        return _service_start_steps(_guess_service_name(prompt))
    if task_type == "service-stop":
        return _service_stop_steps(_guess_service_name(prompt))
    return _fallback_describe_steps(prompt)


def steps_from_prompt(prompt: str, node: str = "host") -> list[dict]:
    """Derive concrete URI step list from a natural language prompt.

    Steps use `{node}` as a placeholder — caller substitutes the actual node name."""
    return [_bind_node(s, node) for s in _raw_steps_for_target(derive_task_target(prompt), prompt)]


def _guess_service_name(prompt: str) -> str:
    m = re.search(r"(?:start|stop|restart|uruchom|zatrzymaj)\s+(\w[\w-]*)", prompt, re.I)
    return m.group(1).lower() if m else "service"


def _bind_node(step: dict, node: str) -> dict:
    return {**step, "uri": step["uri"].replace("{node}", node)}


# ─── top-level plan builder ───────────────────────────────────────────────────

def plan_from_prompt(prompt: str, node: str = "host") -> dict:
    """Build a raw (unannotated) imperative plan dict from a prompt.

    This is the input to `planner.build_imperative_plan` — it produces the
    `flow`-shaped dict with steps, plus derived task metadata."""
    target = derive_task_target(prompt)
    steps = steps_from_prompt(prompt, node)
    return {
        "prompt": prompt,
        "taskType": target["taskType"],
        "domain": target["domain"],
        "needsAuth": target["needsAuth"],
        "steps": steps,
        "stepCount": len(steps),
    }
