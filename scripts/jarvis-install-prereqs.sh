#!/usr/bin/env bash
# Install Homebrew + Tailscale on macOS (requires admin password once).
# Run from Terminal:  bash scripts/jarvis-install-prereqs.sh
set -euo pipefail

echo "==> Hermes WebUI prerequisites (Homebrew + Tailscale)"

# --- Homebrew ---
if command -v brew >/dev/null 2>&1; then
  echo "[ok] Homebrew already installed: $(brew --version | head -1)"
else
  echo "[..] Installing Homebrew (will prompt for admin password)..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  if [[ -x /opt/homebrew/bin/brew ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
    grep -qxF 'eval "$(/opt/homebrew/bin/brew shellenv)"' ~/.zprofile 2>/dev/null \
      || echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
  elif [[ -x /usr/local/bin/brew ]]; then
    eval "$(/usr/local/bin/brew shellenv)"
  fi
  echo "[ok] Homebrew installed"
fi

# Ensure brew on PATH for this script
if [[ -x /opt/homebrew/bin/brew ]]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# --- Tailscale ---
if command -v tailscale >/dev/null 2>&1 || [[ -d /Applications/Tailscale.app ]]; then
  echo "[ok] Tailscale already present"
else
  echo "[..] Installing Tailscale via Homebrew cask..."
  brew install --cask tailscale
  echo "[ok] Tailscale installed"
fi

echo ""
echo "Next steps:"
echo "  1. Open Tailscale from Applications (or menu bar) and sign in"
echo "  2. Or run:  tailscale up"
echo "  3. Get your IP:  tailscale ip -4"
echo "  4. Browse WebUI at http://<tailscale-ip>:8787  (password in ~/.hermes/webui-access.txt)"
