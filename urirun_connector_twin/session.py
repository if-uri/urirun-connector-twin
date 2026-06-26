"""Re-export shim — all live code has moved to browser.py and prompt_plan.py.

session.py is kept for backward compat (external code may import from here).
Canonical implementations:
  - _extract_chrome_info, select_best_session, _AUTH_COOKIES → browser.py
  - derive_task_target                                        → prompt_plan.py
"""
from __future__ import annotations

from .browser import (
    _AUTH_COOKIES,
    _extract_chrome_info,
    discover_browser_sessions,
    select_best_session,
)
from .prompt_plan import derive_task_target

__all__ = [
    "_AUTH_COOKIES",
    "_extract_chrome_info",
    "discover_browser_sessions",
    "select_best_session",
    "derive_task_target",
]
