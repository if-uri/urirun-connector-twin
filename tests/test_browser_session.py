"""Tests for browser.py, session.py, and prompt_plan.py — no live Chrome needed."""
from __future__ import annotations

import pytest
from urirun_connector_twin.session import (
    _extract_chrome_info,
    select_best_session,
    _AUTH_COOKIES,
)
from urirun_connector_twin.prompt_plan import (
    derive_task_target,
    steps_from_prompt,
    plan_from_prompt,
    _extract_url,
    _extract_domain,
    _extract_text_to_type,
)


# ─── derive_task_target (canonical: prompt_plan.py) ──────────────────────────

def test_derive_task_target_linkedin():
    t = derive_task_target("opublikuj post na linkedin")
    assert t["domain"] == "linkedin.com"
    assert t["needsAuth"] is True


def test_derive_task_target_google():
    t = derive_task_target("search something on google")
    assert t["domain"] == "google.com"
    assert t["needsAuth"] is False


def test_derive_task_target_unknown():
    t = derive_task_target("zrób coś losowego")
    assert t["domain"] is None
    assert t["needsAuth"] is False


def test_derive_task_target_twitter():
    t = derive_task_target("post a tweet on twitter")
    assert t["domain"] == "twitter.com"
    assert t["needsAuth"] is True


# ─── session._extract_chrome_info ────────────────────────────────────────────

def test_extract_chrome_info_with_port():
    argv = [b"/usr/bin/google-chrome", b"--remote-debugging-port=9222",
            b"--user-data-dir=/home/tom/.config/google-chrome"]
    info = _extract_chrome_info(argv)
    assert info is not None
    assert info["port"] == 9222
    assert "/google-chrome" in info["userDataDir"]


def test_extract_chrome_info_no_port():
    argv = [b"/usr/bin/google-chrome", b"--no-first-run"]
    assert _extract_chrome_info(argv) is None


def test_extract_chrome_info_not_chrome():
    argv = [b"/usr/bin/python3", b"--remote-debugging-port=9222"]
    assert _extract_chrome_info(argv) is None


def test_extract_chrome_info_tmp_profile():
    argv = [b"/usr/bin/chromium", b"--remote-debugging-port=9333",
            b"--user-data-dir=/tmp/urirun-kvm-cdp-9333"]
    info = _extract_chrome_info(argv)
    assert info["port"] == 9333
    assert info["userDataDir"].startswith("/tmp")


# ─── session.select_best_session ─────────────────────────────────────────────

def _make_session(port, user_data_dir="/tmp/x", reachable=True,
                  auth_confirmed=False, holds_target=False, auth_cookie=None):
    return {
        "port": port, "userDataDir": user_data_dir,
        "reachable": reachable, "tabs": [],
        "holdsTarget": holds_target,
        "authConfirmed": auth_confirmed,
        "authCookie": auth_cookie,
    }


def test_select_best_auth_confirmed():
    sessions = [
        _make_session(9222, auth_confirmed=True, auth_cookie="li_at",
                      user_data_dir="/home/tom/.config/google-chrome"),
        _make_session(9333, user_data_dir="/tmp/urirun-kvm-cdp-9333"),
    ]
    sel = select_best_session(sessions, {"domain": "linkedin.com", "needsAuth": True})
    assert sel["mode"] == "attach"
    assert sel["port"] == 9222
    assert sel["authCookie"] == "li_at"


def test_select_best_holds_target_fallback():
    sessions = [
        _make_session(9222, holds_target=True,
                      user_data_dir="/home/tom/.config/google-chrome"),
    ]
    sel = select_best_session(sessions, {"domain": "linkedin.com", "needsAuth": True})
    assert sel["mode"] == "attach"
    assert sel["port"] == 9222


def test_select_best_needs_login_when_no_auth():
    sessions = [_make_session(9222, user_data_dir="/tmp/blank")]
    sel = select_best_session(sessions, {"domain": "linkedin.com", "needsAuth": True})
    assert sel["mode"] == "needs-login"
    assert "login" in sel["reason"].lower() or "auth" in sel["reason"].lower()


def test_select_best_no_chrome():
    sel = select_best_session([], {"domain": "linkedin.com", "needsAuth": True})
    assert sel["mode"] == "no-chrome"


def test_select_best_no_auth_required():
    sessions = [_make_session(9222, user_data_dir="/tmp/x")]
    sel = select_best_session(sessions, {"domain": None, "needsAuth": False})
    assert sel["mode"] == "attach"
    assert sel["port"] == 9222


# ─── prompt_plan._extract helpers ────────────────────────────────────────────

def test_extract_url():
    assert _extract_url("open https://linkedin.com/feed now") == "https://linkedin.com/feed"
    assert _extract_url("no url here") is None


def test_extract_domain_from_url():
    assert _extract_domain("go to https://github.com/if-uri") == "github.com"


def test_extract_domain_from_keyword():
    assert _extract_domain("post on linkedin") == "linkedin.com"


def test_extract_text_to_type_quoted():
    assert _extract_text_to_type('type "Hello World"') == "Hello World"


def test_extract_text_to_type_after_verb():
    result = _extract_text_to_type("write hello there in the field")
    assert "hello" in result.lower()


# ─── derive_task_target full shape ───────────────────────────────────────────

def test_prompt_derive_social_post():
    t = derive_task_target("opublikuj post na linkedin")
    assert t["taskType"] == "social-post"
    assert t["domain"] == "linkedin.com"
    assert t["needsAuth"] is True


def test_prompt_derive_search():
    t = derive_task_target("search for urirun framework")
    assert t["taskType"] == "web-search"


def test_prompt_derive_screenshot():
    t = derive_task_target("take a screenshot of the screen")
    assert t["taskType"] == "screenshot"


def test_prompt_derive_browser_open():
    t = derive_task_target("open https://github.com")
    assert t["taskType"] == "browser-open"
    assert t["url"] == "https://github.com"


def test_prompt_derive_unknown():
    t = derive_task_target("oblicz sumę wektora")
    assert t["taskType"] == "unknown"


# ─── prompt_plan.steps_from_prompt ───────────────────────────────────────────

def test_steps_from_prompt_social_post():
    steps = steps_from_prompt("opublikuj post na linkedin", node="laptop")
    uris = [s["uri"] for s in steps]
    # Must have session ensure + navigate + fill/post steps
    assert any("session" in u for u in uris)
    assert any("navigate" in u for u in uris)
    assert any("fill" in u or "click" in u for u in uris)
    # {node} must be substituted
    assert all("{node}" not in s["uri"] for s in steps)


def test_steps_from_prompt_screenshot():
    steps = steps_from_prompt("zrób zrzut ekranu")
    assert len(steps) >= 1
    assert "screenshot" in steps[0]["uri"] or "display" in steps[0]["uri"]


def test_steps_from_prompt_search():
    steps = steps_from_prompt("search for urirun")
    uris = [s["uri"] for s in steps]
    assert any("navigate" in u for u in uris)


def test_steps_from_prompt_unknown_fallback():
    steps = steps_from_prompt("some unknown intent xyz")
    assert len(steps) == 1
    assert "describe" in steps[0]["uri"] or "intent" in steps[0]["uri"]


# ─── prompt_plan.plan_from_prompt ────────────────────────────────────────────

def test_plan_from_prompt_structure():
    plan = plan_from_prompt("take a screenshot", node="laptop")
    assert plan["prompt"] == "take a screenshot"
    assert "steps" in plan
    assert plan["stepCount"] == len(plan["steps"])


def test_plan_from_prompt_social_post_metadata():
    plan = plan_from_prompt("post on linkedin", node="laptop")
    assert plan["taskType"] == "social-post"
    assert plan["needsAuth"] is True
    assert plan["domain"] == "linkedin.com"


# ─── core routes (smoke, no live Chrome) ─────────────────────────────────────

def test_browser_sessions_route_no_chrome(monkeypatch):
    monkeypatch.setattr(
        "urirun_connector_twin.browser.os.listdir", lambda p: [],
    )
    from urirun_connector_twin.core import browser_sessions
    r = browser_sessions(probe_cookies=False)
    assert r["ok"] is True
    assert r["count"] == 0


def test_browser_profile_route_no_chrome(monkeypatch):
    monkeypatch.setattr(
        "urirun_connector_twin.browser.os.listdir", lambda p: []
    )
    from urirun_connector_twin.core import browser_profile
    r = browser_profile(domain="linkedin.com")
    assert r["ok"] is True
    assert r["selection"]["mode"] == "needs-login"


def test_plan_from_prompt_route(monkeypatch):
    monkeypatch.setattr(
        "urirun_connector_twin.environment._kvm_query", lambda *a, **kw: None
    )
    monkeypatch.setattr(
        "urirun_connector_twin.environment._docker_available", lambda: True
    )
    monkeypatch.setattr(
        "urirun_connector_twin.environment.uri_call", lambda *a, **kw: None
    )
    monkeypatch.setattr(
        "urirun_connector_twin.browser.os.listdir", lambda p: []
    )
    from urirun_connector_twin.core import plan_from_prompt_route
    r = plan_from_prompt_route("take a screenshot", node="", probe_browser=False)
    assert r["ok"] is True
    assert "plan" in r
    assert r["plan"]["totalSteps"] >= 1
