#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
rm -f "$HOME/.local/share/applications/nexaedit.desktop"
rm -f "$HOME/.local/share/icons/hicolor/256x256/apps/nexaedit.png"
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" >/dev/null 2>&1 || true
fi
rm -rf "$ROOT/.venv"
echo "NexaEdit kaldırıldı. Kaynak dosyalar korunmuştur."
