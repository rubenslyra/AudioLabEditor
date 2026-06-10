#!/usr/bin/env bash
# =============================================================================
# AudioLab Editor — Uninstaller
# =============================================================================
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
APP="audiolab-editor"

# Detect where it was installed
CANDIDATES=(
  "${HOME}/.local/bin/${APP}"
  "/usr/local/bin/${APP}"
)

INSTALLED=""
for path in "${CANDIDATES[@]}"; do
  if [ -x "$path" ]; then
    INSTALLED="$path"
    break
  fi
done

if [ -z "$INSTALLED" ]; then
  echo "AudioLab Editor nao encontrado no sistema."
  echo "Removendo apenas arquivos de desktop e icone..."

  rm -f "${HOME}/.local/share/applications/${APP}.desktop"
  rm -f "${HOME}/.local/share/icons/hicolor/256x256/apps/${APP}.png"
  rm -f /usr/local/share/applications/${APP}.desktop
  rm -f /usr/local/share/icons/hicolor/256x256/apps/${APP}.png

  echo "Diretorio de build (dist/ build/) nao foi removido."
  echo "Para limpar: cd ${ROOT} && rm -rf dist build"
  exit 0
fi

echo "Removendo ${INSTALLED}..."
rm -f "$INSTALLED"

BIN_DIR="$(dirname "$INSTALLED")"
DESKTOP_DIR="${HOME}/.local/share/applications"
ICON_DIR="${HOME}/.local/share/icons/hicolor/256x256/apps"
if [[ "$BIN_DIR" == "/usr/local/bin" ]]; then
  DESKTOP_DIR="/usr/local/share/applications"
  ICON_DIR="/usr/local/share/icons/hicolor/256x256/apps"
fi

rm -f "${DESKTOP_DIR}/${APP}.desktop"
rm -f "${ICON_DIR}/${APP}.png"

if command -v update-desktop-database &>/dev/null; then
  update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi

echo "AudioLab Editor desinstalado."
echo "Para limpar o diretorio de build: cd ${ROOT} && rm -rf dist build"
