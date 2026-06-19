"""Regression checks for unlimited session pinning."""

import json
import pathlib
import urllib.error
import urllib.request

from tests._pytest_port import BASE

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG_PY = (ROOT / "api" / "config.py").read_text(encoding="utf-8")
INDEX_HTML = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
PANELS_JS = (ROOT / "static" / "panels.js").read_text(encoding="utf-8")
BOOT_JS = (ROOT / "static" / "boot.js").read_text(encoding="utf-8")
SESSIONS_JS = (ROOT / "static" / "sessions.js").read_text(encoding="utf-8")


def post(path, body=None):
    data = json.dumps(body or {}).encode()
    req = urllib.request.Request(
        BASE + path,
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read()), r.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read()), e.code


def make_session(created, title):
    payload = {
        "title": title,
        "messages": [{"role": "user", "content": "keep this conversation handy"}],
        "model": "test/pin-limit-setting",
    }
    d, status = post("/api/session/import", payload)
    assert status == 200
    sid = d["session"]["session_id"]
    created.append(sid)
    return sid


def test_pin_limit_setting_is_removed_from_ui_and_config():
    assert '"pinned_sessions_limit"' not in CONFIG_PY
    assert 'id="settingsPinnedSessionsLimit"' not in INDEX_HTML
    assert "pinned_sessions_limit" not in PANELS_JS
    assert "_pinnedSessionsLimit" not in BOOT_JS
    assert "function _getPinnedSessionsLimit()" not in SESSIONS_JS
    assert "function _pinnedSessionsLimit()" not in SESSIONS_JS
    assert "_pinnedSessionCount()>=_getPinnedSessionsLimit()" not in SESSIONS_JS
    assert "await api('/api/session/pin'" in SESSIONS_JS


def test_session_pin_endpoint_allows_unlimited_pins():
    created = []
    try:
        pinned = [make_session(created, f"Unlimited pin {i}") for i in range(5)]
        for sid in pinned:
            d, status = post("/api/session/pin", {"session_id": sid, "pinned": True})
            assert status == 200
            assert d["session"]["pinned"] is True
    finally:
        for sid in created:
            post("/api/session/delete", {"session_id": sid})
