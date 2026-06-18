#!/usr/bin/env bash
# Install launchd LaunchAgent for Hermes WebUI (auto-start on login, restart on crash).
# IMPORTANT: Do not also run ./ctl.sh start — pick launchd OR ctl.sh, not both.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLIST_SRC="${REPO_ROOT}/deploy/com.jarvis.hermes-webui.plist"
PLIST_DST="${HOME}/Library/LaunchAgents/com.jarvis.hermes-webui.plist"
LABEL="com.jarvis.hermes-webui"

echo "==> Installing launchd LaunchAgent: ${LABEL}"

# Stop ctl.sh daemon if running (avoid port conflict)
if [[ -x "${REPO_ROOT}/ctl.sh" ]]; then
  "${REPO_ROOT}/ctl.sh" stop 2>/dev/null || true
fi

mkdir -p "${HOME}/Library/LaunchAgents"
cp "${PLIST_SRC}" "${PLIST_DST}"

# Unload if already loaded, then load fresh
launchctl bootout "gui/$(id -u)/${LABEL}" 2>/dev/null || \
  launchctl unload "${PLIST_DST}" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "${PLIST_DST}" 2>/dev/null || \
  launchctl load "${PLIST_DST}"

sleep 2
echo ""
echo "Status:"
launchctl print "gui/$(id -u)/${LABEL}" 2>/dev/null | head -20 || launchctl list | grep hermes || true
echo ""
echo "Logs: ~/.hermes/webui/launchd-{stdout,stderr}.log"
echo "Manage: launchctl kickstart -k gui/$(id -u)/${LABEL}   # restart"
echo "        launchctl bootout gui/$(id -u)/${LABEL}         # stop"
echo "Health: curl http://127.0.0.1:8787/health"
