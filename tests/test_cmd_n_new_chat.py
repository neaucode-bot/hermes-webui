"""Regression tests for Cmd/Ctrl+N starting a new chat instead of a new window."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BOOT_JS = (REPO_ROOT / "static" / "boot.js").read_text(encoding="utf-8")
PWA_STARTUP_JS = (REPO_ROOT / "static" / "pwa-startup.js").read_text(encoding="utf-8")


def _document_keydown_block() -> str:
    marker = "// B14: Cmd/Ctrl+K creates a new chat from anywhere"
    start = BOOT_JS.index(marker)
    listener = BOOT_JS.index("document.addEventListener('keydown',async e=>{", start)
    brace = BOOT_JS.index("{", listener)
    depth = 1
    idx = brace + 1
    while idx < len(BOOT_JS) and depth:
        if BOOT_JS[idx] == "{":
            depth += 1
        elif BOOT_JS[idx] == "}":
            depth -= 1
        idx += 1
    assert depth == 0, "document keydown handler must close"
    return BOOT_JS[brace + 1 : idx - 1]


def test_pwa_startup_blocks_native_new_window_shortcut():
    assert "blockNativeNewWindowShortcut" in PWA_STARTUP_JS
    assert "window.addEventListener('keydown',blockNativeNewWindowShortcut,true)" in PWA_STARTUP_JS
    assert "e.preventDefault();" in PWA_STARTUP_JS
    assert "e.key!=='n'" in PWA_STARTUP_JS or "e.key==='n'" in PWA_STARTUP_JS


def test_cmd_n_triggers_new_chat_button_and_uses_capture():
    assert "{capture:true}" in BOOT_JS, "global shortcut handler must run in capture phase"
    block = _document_keydown_block()

    n_idx = block.index("e.key==='n'")
    snippet = block[max(0, n_idx - 500) : n_idx + 500]
    assert "e.preventDefault();" in snippet, "Cmd/Ctrl+N must prevent browser new-window shortcut"
    assert "btnNewChat" in snippet, "Cmd/Ctrl+N must reuse the New Chat button handler"
    assert "tagName==='INPUT'" in snippet, "must skip when focus is in an input"
    assert "tagName==='TEXTAREA'" in snippet, "must skip when focus is in a textarea"
    assert "isContentEditable" in snippet, "must skip when focus is in contenteditable"
