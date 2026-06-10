#!/usr/bin/env bash
# =============================================================================
# AudioLab Editor — Installer
# =============================================================================
# Builds the PyInstaller binary and installs it system-wide or per-user.
#
# Uso:
#   ./scripts/install.sh              # instala em ~/.local
#   ./scripts/install.sh --system     # instala em /usr/local (requer sudo)
#   ./scripts/install.sh --prefix /opt # instala em diretorio customizado
# =============================================================================
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
APP="audiolab-editor"
BINARY_NAME="AudioLabEditor"
PROFILE="${AUDIO_LAB_EDITOR_PROFILE:-base}"

# --- Parse arguments ---
INSTALL_PREFIX="${HOME}/.local"
DESKTOP_DIR="${HOME}/.local/share/applications"
ICON_DIR="${HOME}/.local/share/icons/hicolor/256x256/apps"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --system) INSTALL_PREFIX="/usr/local"; DESKTOP_DIR="/usr/local/share/applications"; ICON_DIR="/usr/local/share/icons/hicolor/256x256/apps"; shift ;;
    --prefix) INSTALL_PREFIX="$2"; DESKTOP_DIR="${INSTALL_PREFIX}/share/applications"; ICON_DIR="${INSTALL_PREFIX}/share/icons/hicolor/256x256/apps"; shift 2 ;;
    --profile) PROFILE="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

BIN_DIR="${INSTALL_PREFIX}/bin"

# --- Step 1: Build ---
echo "==> PyInstaller build (profile=${PROFILE})..."
cd "$ROOT"
rm -rf dist build
AUDIO_LAB_EDITOR_PROFILE="$PROFILE" python3 -m PyInstaller "$HERE/AudioLabEditor.spec" --log-level WARN

if [ ! -f "dist/${BINARY_NAME}" ]; then
  echo "ERROR: Build failed — dist/${BINARY_NAME} not found."
  exit 1
fi

# --- Step 2: Install binary ---
echo "==> Installing to ${BIN_DIR}..."
mkdir -p "$BIN_DIR"
cp "dist/${BINARY_NAME}" "${BIN_DIR}/${APP}"
chmod 755 "${BIN_DIR}/${APP}"

# --- Step 3: Desktop entry ---
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
StartupWMClass=audiolabeditor
MimeType=audio/mpeg;audio/wav;audio/flac;audio/ogg;video/mp4;video/x-matroska;
DESKTOP

# --- Step 4: Icon ---
echo "==> Installing icon..."
mkdir -p "$ICON_DIR"
cp "${ROOT}/src/presentation/assets/logo.png" "${ICON_DIR}/${APP}.png"

# --- Step 5: Update desktop database ---
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
