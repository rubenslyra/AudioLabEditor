#!/usr/bin/env bash
set -euo pipefail

APP="audiolab-editor"

if [ -f "${HOME}/.local/bin/${APP}" ]; then
  rm -f "${HOME}/.local/bin/${APP}"
  echo "Removed ${HOME}/.local/bin/${APP}"
fi

for dir in "${HOME}/.local/share/applications" "/usr/local/share/applications"; do
  desktop="${dir}/${APP}.desktop"
  if [ -f "$desktop" ]; then
    rm -f "$desktop"
    echo "Removed $desktop"
  fi
done

for dir in "${HOME}/.local/share/icons/hicolor/256x256/apps" "/usr/local/share/icons/hicolor/256x256/apps"; do
  icon="${dir}/${APP}.png"
  if [ -f "$icon" ]; then
    rm -f "$icon"
    echo "Removed $icon"
  fi
done

echo "AudioLab Editor desinstalado."
