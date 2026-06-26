"""Re-export shim — all live code has moved to browser.py and prompt_plan.py.

session.py is kept for backward compat (test_browser_session.py imports from here).
Canonical implementations:
  - _extract_chrome_info, select_best_session, _AUTH_COOKIES → browser.py
  - derive_task_target (simple domain/auth shape)              → prompt_plan.py
"""
from __future__ import annotations

from .browser import (
    _AUTH_COOKIES,
    _extract_chrome_info,
    discover_browser_sessions,
    select_best_session,
)
from .prompt_plan import derive_task_target as _full_derive
import re


# ─── simple derive_task_target (domain + needsAuth only) ─────────────────────
# The full version in prompt_plan.py returns taskType/url/content in addition.
# This simpler shape is used by test_browser_session.py and select_best_session.

_DOMAIN_PATTERNS: list[tuple[str, str | None, bool]] = [
    (r"\blinkedin\b",     "linkedin.com",  True),
    (r"\bgithub\b",       "github.com",    False),
    (r"\bgoogle\b",       "google.com",    False),
    (r"\bfacebook\b",     "facebook.com",  True),
    (r"\btwitter\b|twitter\.com|x\.com", "twitter.com", True),
]


def derive_task_target(prompt: str) -> dict:
    """Extract domain and auth requirement from a natural-language prompt.

    Simple shape: {domain, needsAuth}.  For the full classification (taskType, url,
    content) use prompt_plan.derive_task_target instead."""
    low = prompt.lower()
    for pattern, domain, needs_auth in _DOMAIN_PATTERNS:
        if re.search(pattern, low):
            return {"domain": domain, "needsAuth": needs_auth}
    return {"domain": None, "needsAuth": False}


__all__ = [
    "_AUTH_COOKIES",
    "_extract_chrome_info",
    "discover_browser_sessions",
    "select_best_session",
    "derive_task_target",
]
