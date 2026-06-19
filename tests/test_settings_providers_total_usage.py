"""Settings → Providers must keep the quota/total-usage card visible."""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
PANELS_JS = (REPO_ROOT / "static" / "panels.js").read_text(encoding="utf-8")


def test_providers_panel_keeps_quota_card_when_provider_list_empty():
    """Empty provider cards must not hide the active-provider usage card."""
    start = PANELS_JS.index("async function loadProvidersPanel()")
    end = PANELS_JS.index("async function _refreshProviderQuota(", start)
    block = PANELS_JS[start:end]
    assert "const quotaCard=_buildProviderQuotaCard(quota)" in block
    assert "if(providers.length===0)" in block
    assert "list.style.display=quotaCard?'':'none'" in block
    assert "list.style.display='none'" not in block.split("if(providers.length===0)")[1].split("return")[0]


def test_conversation_usage_panel_not_wired():
    """Per-session usage belongs in chat/status, not Settings → Conversation."""
    assert "hermesSessionUsage" not in (REPO_ROOT / "static" / "index.html").read_text(encoding="utf-8")
    assert "_renderHermesSessionUsage" not in PANELS_JS
    assert "_refreshConversationUsageFromApi" not in PANELS_JS


def test_providers_panel_fetches_cursor_quota_for_active_provider():
    """Providers panel must call the shared provider quota endpoint."""
    assert "'/api/provider/quota'" in PANELS_JS
    assert "_fetchProviderQuotaStatus" in PANELS_JS
