"""Browser session discovery: enumerates live Chrome/Chromium processes from /proc,
extracts their --user-data-dir and --remote-debugging-port, probes each CDP endpoint
for open tabs, and checks session auth via cookie presence.

This is the missing primitive: instead of always starting a fresh --user-data-dir=/tmp/...
profile, the planner can ATTACH to an existing, already-logged-in Chrome.

Pure functions only — no subprocess side-effects from the probe path."""
from __future__ import annotations

import json
import os
import re
import socket
import urllib.request
from pathlib import Path
from typing import Any


_CHROME_BINARIES = frozenset({"chrome", "chromium", "google-chrome", "chromium-browser"})

# Known auth cookies per domain keyword
_AUTH_COOKIES: dict[str, str] = {
    "linkedin": "li_at",
    "google": "SID",
    "github": "user_session",
    "facebook": "c_user",
}


def _proc_cmdline(pid: int) -> list[str]:
    try:
        raw = Path(f"/proc/{pid}/cmdline").read_bytes()
        return raw.rstrip(b"\x00").split(b"\x00")
    except (OSError, PermissionError):
        return []


def _is_browser(args: list[bytes]) -> bool:
    if not args:
        return False
    exe = Path(os.fsdecode(args[0])).name.lower()
    return exe in _CHROME_BINARIES or "chrome" in exe


def _extract_flag(args: list[bytes], flag: str) -> str | None:
    prefix = f"--{flag}="
    for arg in args:
        decoded = arg.decode("utf-8", errors="replace")
        if decoded.startswith(prefix):
            return decoded[len(prefix):]
    return None


def _cdp_pages(port: int, timeout: float = 1.5) -> list[dict]:
    """Fetch /json from a Chrome debug port. Returns [] on any error."""
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}/json",
                                     headers={"Host": "localhost"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception:
        return []


def _cdp_cookies(port: int, timeout: float = 1.5) -> list[dict]:
    """Fetch all cookies via CDP Network.getAllCookies (one-shot WS call)."""
    try:
        import socket as _socket
        import base64
        import struct
        import hashlib

        pages = _cdp_pages(port, timeout)
        if not pages:
            return []
        ws_url = pages[0].get("webSocketDebuggerUrl", "")
        if not ws_url:
            return []

        # Simple WS handshake (text frame only, no library dependency)
        m = re.match(r"ws://([^:/]+):(\d+)(/.+)", ws_url)
        if not m:
            return []
        host, ws_port, path = m.group(1), int(m.group(2)), m.group(3)
        key = base64.b64encode(os.urandom(16)).decode()
        sock = _socket.create_connection((host, ws_port), timeout=timeout)
        handshake = (
            f"GET {path} HTTP/1.1\r\nHost: {host}\r\n"
            f"Upgrade: websocket\r\nConnection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n"
        )
        sock.sendall(handshake.encode())
        resp = sock.recv(4096)
        if b"101" not in resp:
            return []

        # Send Network.getAllCookies
        payload = json.dumps({"id": 1, "method": "Network.getAllCookies"}).encode()
        length = len(payload)
        # WS frame: FIN=1, opcode=1 (text), masked
        mask = os.urandom(4)
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        frame = bytes([0x81, 0x80 | length]) + mask + masked
        sock.sendall(frame)

        # Receive response (may be fragmented)
        raw = b""
        sock.settimeout(timeout)
        try:
            while len(raw) < 2:
                raw += sock.recv(4096)
            body_start = 2
            length_byte = raw[1] & 0x7F
            if length_byte == 126:
                body_start = 4
            elif length_byte == 127:
                body_start = 10
            full = raw[body_start:]
            while len(full) < length_byte:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                full += chunk
        except Exception:
            full = raw[2:]
        sock.close()
        result = json.loads(full.decode("utf-8", errors="replace"))
        return result.get("result", {}).get("cookies", [])
    except Exception:
        return []


def _has_auth_cookie(cookies: list[dict], domain_key: str) -> bool:
    cookie_name = _AUTH_COOKIES.get(domain_key)
    if not cookie_name:
        # Unknown domain — check for any session-like cookie on that domain
        return any(domain_key in c.get("domain", "") for c in cookies)
    return any(c.get("name") == cookie_name for c in cookies)


def _port_open(port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=timeout):
            return True
    except Exception:
        return False


def discover_browser_sessions(probe_cookies: bool = False) -> list[dict]:
    """Enumerate live Chrome/Chromium processes and their debug sessions.

    Returns a list of session dicts sorted by port. Each entry:
      pid, port, userDataDir, pages (list of {url, title}), reachable (bool)

    When probe_cookies=True, also fetches cookies to populate
    authCookies={domain: bool} — more expensive but gives session proof."""
    sessions: list[dict] = []
    try:
        pids = [int(p) for p in os.listdir("/proc") if p.isdigit()]
    except OSError:
        return []

    for pid in pids:
        args = _proc_cmdline(pid)
        if not _is_browser(args):
            continue
        port_str = _extract_flag(args, "remote-debugging-port")
        if not port_str:
            continue
        try:
            port = int(port_str)
        except ValueError:
            continue
        user_data_dir = _extract_flag(args, "user-data-dir") or ""
        reachable = _port_open(port)
        pages: list[dict] = []
        auth_cookies: dict[str, bool] = {}
        if reachable:
            raw_pages = _cdp_pages(port)
            pages = [{"url": p.get("url", ""), "title": p.get("title", "")}
                     for p in raw_pages if p.get("type") == "page"]
            if probe_cookies:
                cookies = _cdp_cookies(port)
                for domain_key in _AUTH_COOKIES:
                    auth_cookies[domain_key] = _has_auth_cookie(cookies, domain_key)

        session: dict[str, Any] = {
            "pid": pid,
            "port": port,
            "userDataDir": user_data_dir,
            "reachable": reachable,
            "pages": pages,
        }
        if probe_cookies:
            session["authCookies"] = auth_cookies
        sessions.append(session)

    return sorted(sessions, key=lambda s: s["port"])


def select_session(sessions: list[dict], domain: str, needs_auth: bool = False) -> dict:
    """Choose the best session for a given domain/task.

    Selection priority:
      1. Session with an open tab on the target domain + auth cookie (if needs_auth)
      2. Session with a real (non-tmp) user-data-dir profile
      3. Any reachable session
      4. None → mode=needs-login

    Returns a selection dict: mode (attach|needs-login|none), port, userDataDir,
    profileType (real|temp|unknown), rationale."""
    domain_key = _domain_key(domain)
    reachable = [s for s in sessions if s["reachable"]]

    # 1. Has an open tab on the domain AND (if needs_auth) an auth cookie
    for s in reachable:
        on_domain = any(domain in p.get("url", "") for p in s.get("pages", []))
        if not on_domain:
            continue
        if needs_auth and s.get("authCookies"):
            if not s["authCookies"].get(domain_key, False):
                continue
        return _selection("attach", s, domain_key, "tab already open on domain")

    # 2. Non-temp profile (not /tmp/…)
    for s in reachable:
        udd = s.get("userDataDir") or ""
        if udd and not udd.startswith("/tmp"):
            rationale = "real profile — may already have saved session"
            if needs_auth:
                rationale += " (open target URL manually once to log in)"
            return _selection("attach", s, domain_key, rationale)

    # 3. Any reachable session
    if reachable:
        s = reachable[0]
        return _selection("attach", s, domain_key, "only reachable session — no profile guarantee")

    # 4. Nothing — requires human login
    return {
        "mode": "needs-login",
        "port": None,
        "userDataDir": None,
        "profileType": "none",
        "rationale": "no reachable Chrome found — start Chrome with --remote-debugging-port=9222 "
                     "and log in to the target site manually, then retry",
        "humanGated": True,
        "constraint": "auth-required",
    }


def _extract_chrome_info(argv: list[bytes]) -> "dict | None":
    """Compat shim: combine _is_browser + _extract_flag into the shape session.py exported.

    session.py is now a re-export shim; this function is the canonical implementation."""
    if not _is_browser(argv):
        return None
    port_str = _extract_flag(argv, "remote-debugging-port")
    if not port_str:
        return None
    try:
        port = int(port_str)
    except ValueError:
        return None
    data_dir = _extract_flag(argv, "user-data-dir") or ""
    return {"port": port, "userDataDir": data_dir}


def select_best_session(sessions: list[dict], task: dict) -> dict:
    """Compat shim for session.select_best_session(sessions, task_dict).

    Maps the task-dict shape (from session.py) onto select_session's explicit params.
    session.py is now a re-export shim; core.py uses select_session() directly."""
    domain = str(task.get("domain") or "")
    needs_auth = bool(task.get("needsAuth"))
    reachable = [s for s in sessions if s.get("reachable")]
    if not reachable:
        return {"mode": "no-chrome", "port": None, "reason": "no reachable Chrome processes found"}

    # Try session with authConfirmed + authCookie (session.py shape — old probe_session path)
    if needs_auth:
        for s in reachable:
            if s.get("authConfirmed") and s.get("authCookie"):
                return {"mode": "attach", "port": s["port"],
                        "userDataDir": s.get("userDataDir"),
                        "authCookie": s["authCookie"]}
        # holdsTarget: session holds a tab on the target domain
        for s in reachable:
            if s.get("holdsTarget"):
                return {"mode": "attach", "port": s["port"],
                        "userDataDir": s.get("userDataDir"),
                        "authCookie": s.get("authCookie")}
        return {"mode": "needs-login", "port": None,
                "reason": f"no authenticated session for {domain or 'requested site'} found"}

    # No auth needed: any reachable session is fine
    s = reachable[0]
    return {"mode": "attach", "port": s["port"], "userDataDir": s.get("userDataDir")}


def _domain_key(domain: str) -> str:
    """Map a domain/URL/service name to the _AUTH_COOKIES key."""
    d = domain.lower()
    for key in _AUTH_COOKIES:
        if key in d:
            return key
    return d.split(".")[0].split("/")[-1]


def _selection(mode: str, session: dict, domain_key: str, rationale: str) -> dict:
    udd = session.get("userDataDir") or ""
    auth_cookies = session.get("authCookies") or {}
    auth_confirmed = bool(auth_cookies.get(domain_key))
    cookie_name = _AUTH_COOKIES.get(domain_key) if auth_confirmed else None
    return {
        "mode": mode,
        "port": session["port"],
        "userDataDir": udd,
        "profileType": "temp" if udd.startswith("/tmp") else ("real" if udd else "unknown"),
        "rationale": rationale,
        "humanGated": False,
        "constraint": None,
        "pid": session.get("pid"),
        "authConfirmed": auth_confirmed,
        "authCookie": cookie_name,
    }
