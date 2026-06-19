"""iOS Safari Return/Enter sends instead of inserting a newline.

Two related fixes are pinned here:

1. The chat composer's IME guard (`_isImeEnter`) must NOT treat a genuine
   Return press as composition just because iOS Safari reports
   `keyCode === 229` for it while predictive text / autocorrect is pending.
   Previously the blanket `keyCode === 229` check swallowed the Enter and the
   textarea inserted a newline instead of sending. The refined guard only
   trusts the stateless 229 signal when the event is not itself the Enter key,
   so real CJK composition (caught by `isComposing` / the `_imeComposing`
   flag) is still ignored while a real Return on iOS now goes through.

2. A new `send_key` mode, `enter_always`, lets touch users opt out of the
   mobile Enter=newline fallback so Return sends on the soft keyboard too
   (Shift+Enter still inserts a newline). The mobile fallback (`_mobileDefault`)
   must remain gated on the default `enter` mode so `enter_always` routes to the
   plain Enter-to-send branch on every device.
"""

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BOOT_JS = (REPO / "static" / "boot.js").read_text(encoding="utf-8")
INDEX_HTML = (REPO / "static" / "index.html").read_text(encoding="utf-8")
CONFIG_PY = (REPO / "api" / "config.py").read_text(encoding="utf-8")


# ── Fix 1: iOS keyCode 229 must not swallow a real Enter ─────────────────────


def test_ime_guard_excludes_real_enter_from_keycode_229():
    """`_isImeEnter` must qualify the stateless keyCode===229 signal with
    `key!=='Enter'` so a genuine Return on iOS Safari is not mistaken for IME
    composition."""
    assert "e.keyCode===229&&e.key!=='Enter'" in BOOT_JS, (
        "iOS Safari reports keyCode===229 for a real Return when predictive "
        "text is pending; the IME guard must not treat that Enter as composition."
    )


def test_ime_guard_still_covers_genuine_composition():
    """The composer composition signals (isComposing + _imeComposing flag) must
    remain in the guard so real CJK input is still ignored."""
    assert "e.isComposing" in BOOT_JS
    assert "_imeComposing" in BOOT_JS
    # Composer send handler still routes through the shared guard.
    assert "if(_isImeEnter(e)){return;}" in BOOT_JS


# ── Fix 2: enter_always opts out of the mobile newline fallback ──────────────


def test_send_key_dropdown_offers_enter_always():
    assert 'value="enter_always"' in INDEX_HTML, (
        "Send Key settings must offer an 'enter_always' option so mobile users "
        "can make Return send on the soft keyboard."
    )


def test_config_allows_enter_always_send_key():
    assert '"enter_always"' in CONFIG_PY, (
        "api/config.py must accept 'enter_always' as a valid send_key value or "
        "the preference will be rejected by enum validation."
    )


def test_mobile_newline_fallback_only_applies_to_default_enter_mode():
    """`_mobileDefault` must gate on `_sendKey==='enter'` so enter_always (and
    ctrl+enter) bypass the mobile Enter=newline fallback."""
    assert "window._sendKey==='enter'" in BOOT_JS
    # The branch that suppresses Enter-to-send only fires for ctrl+enter or the
    # gated mobile default; enter_always matches neither and falls to the
    # plain `if(!e.shiftKey){...send();}` branch.
    assert "if(window._sendKey==='ctrl+enter'||_mobileDefault){" in BOOT_JS
    assert "if(!e.shiftKey){e.preventDefault();send();" in BOOT_JS
