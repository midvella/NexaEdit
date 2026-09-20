#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-python3}"
if ! "$PYTHON" -c "import tkinter" >/dev/null 2>&1; then
    if command -v apt-get >/dev/null 2>&1; then
        echo "Tkinter eksik; python3-tk kuruluyor..."
        sudo apt-get update
        sudo apt-get install -y python3-tk
    else
        echo "Tkinter eksik. Sistem paket yöneticinizle python3-tk kurun."
        exit 1
    fi
fi
if command -v apt-get >/dev/null 2>&1 && ! command -v zenity >/dev/null 2>&1 && ! command -v kdialog >/dev/null 2>&1; then
    echo "Modern dosya seçici kuruluyor..."
    sudo apt-get update
    sudo apt-get install -y zenity
fi
"$PYTHON" -m venv "$ROOT/.venv"
"$ROOT/.venv/bin/python" -m pip install --upgrade pip
"$ROOT/.venv/bin/python" -m pip install -r "$ROOT/requirements.txt"
mkdir -p "$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"
mkdir -p "$ICON_DIR"
cp "$ROOT/icon.png" "$ICON_DIR/nexaedit.png"
cat > "$HOME/.local/share/applications/nexaedit.desktop" <<EOF
[Desktop Entry]
Name=NexaEdit
Comment=Yerel arka plan kaldırma
Exec="$ROOT/.venv/bin/python" "$ROOT/main.py"
Icon=nexaedit
Terminal=false
Type=Application
Categories=Graphics;Utility;
EOF
chmod +x "$HOME/.local/share/applications/nexaedit.desktop"
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$HOME/.local/share/applications" >/dev/null 2>&1 || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" >/dev/null 2>&1 || true
fi
echo "NexaEdit kuruldu."
