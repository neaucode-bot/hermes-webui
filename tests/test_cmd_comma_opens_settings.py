"""Regression tests for Cmd/Ctrl+, opening Settings."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BOOT_JS = (REPO_ROOT / "static" / "boot.js").read_text(encoding="utf-8")


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


def test_cmd_comma_opens_settings_and_skips_text_inputs():
    block = _document_keydown_block()

    assert "e.key===','" in block, "handler must listen for comma"
    assert "switchPanel('settings')" in block, "handler must open settings panel"
    assert "e.preventDefault();" in block, "handler must prevent browser preferences shortcut"

    comma_idx = block.index("e.key===','")
    snippet = block[max(0, comma_idx - 400) : comma_idx + 400]
    assert "tagName==='INPUT'" in snippet, "must skip when focus is in an input"
    assert "tagName==='TEXTAREA'" in snippet, "must skip when focus is in a textarea"
    assert "isContentEditable" in snippet, "must skip when focus is in contenteditable"
