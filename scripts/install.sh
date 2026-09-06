#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
APP="audiolab-editor"
BINARY_NAME="AudioLabEditor"

INSTALL_PREFIX="${HOME}/.local"
DESKTOP_DIR="${HOME}/.local/share/applications"
ICON_DIR="${HOME}/.local/share/icons/hicolor/256x256/apps"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --system) INSTALL_PREFIX="/usr/local"; DESKTOP_DIR="/usr/local/share/applications"; ICON_DIR="/usr/local/share/icons/hicolor/256x256/apps"; shift ;;
    --prefix) INSTALL_PREFIX="$2"; DESKTOP_DIR="${INSTALL_PREFIX}/share/applications"; ICON_DIR="${INSTALL_PREFIX}/share/icons/hicolor/256x256/apps"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

BIN_DIR="${INSTALL_PREFIX}/bin"

echo "==> PyInstaller build (core)..."
cd "$ROOT"
rm -rf dist build
python3 -m PyInstaller "$HERE/AudioLabEditor.spec" --log-level WARN

if [ ! -f "dist/${BINARY_NAME}" ]; then
  echo "ERROR: Build failed — dist/${BINARY_NAME} not found."
  exit 1
fi

echo "==> Installing to ${BIN_DIR}..."
mkdir -p "$BIN_DIR"
cp "dist/${BINARY_NAME}" "${BIN_DIR}/${APP}"
chmod 755 "${BIN_DIR}/${APP}"

echo "==> Installing desktop entry..."
mkdir -p "$DESKTOP_DIR"
cat > "${DESKTOP_DIR}/${APP}.desktop" <<DESKTOP
[Desktop Entry]
Version=1.0
Type=Application
Name=AudioLab Editor
Comment=Capture, edit and separate audio stems
Exec=${BIN_DIR}/${APP} %F
Icon=${APP}
Terminal=false
Categories=AudioVideo;Audio;Video;Utility;
StartupNotify=true
MimeType=audio/mpeg;audio/wav;audio/flac;audio/ogg;video/mp4;video/x-matroska;
DESKTOP

echo "==> Installing icon..."
mkdir -p "$ICON_DIR"
cp "${ROOT}/src/presentation/assets/logo.png" "${ICON_DIR}/${APP}.png"

if command -v update-desktop-database &>/dev/null; then
  update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi

echo ""
echo "==> Instalacao concluida!"
echo "    Executavel: ${BIN_DIR}/${APP}"
echo "    Desktop:    ${DESKTOP_DIR}/${APP}.desktop"
echo ""
echo "    Use '${APP}' no terminal ou procure por 'AudioLab Editor' no menu."
echo "    Para desinstalar: ${HERE}/uninstall.sh"
