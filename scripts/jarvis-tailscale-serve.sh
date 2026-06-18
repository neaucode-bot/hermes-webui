#!/usr/bin/env bash
# Expose Hermes WebUI over Tailscale HTTPS (MagicDNS URL, tailnet-only by default).
# Requires: Tailscale installed and logged in (tailscale up).
set -euo pipefail

PORT="${HERMES_WEBUI_PORT:-8787}"

if ! command -v tailscale >/dev/null 2>&1; then
  echo "Tailscale CLI not found. Install first:" >&2
  echo "  bash scripts/jarvis-install-prereqs.sh" >&2
  echo "  or open /Applications/Tailscale.app and sign in" >&2
  exit 1
fi

if ! tailscale status >/dev/null 2>&1; then
  echo "Tailscale not connected. Run:  tailscale up" >&2
  exit 1
fi

TS_IP="$(tailscale ip -4 2>/dev/null || true)"
echo "Tailscale IPv4: ${TS_IP:-unknown}"

# HTTPS reverse proxy on tailnet (no public funnel)
echo "Setting tailscale serve -> http://127.0.0.1:${PORT}"
tailscale serve --bg --https=443 "http://127.0.0.1:${PORT}"

echo ""
tailscale serve status 2>/dev/null || true
echo ""
echo "Open the HTTPS URL shown above from any device on your tailnet."
echo "Direct HTTP (also works): http://${TS_IP}:${PORT}"
