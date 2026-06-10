#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Prefer AppImage if available
APPIMAGE="${APP_ROOT}/dist/AudioLabEditor-x86_64.AppImage"
if [ -x "$APPIMAGE" ]; then
  exec "$APPIMAGE" "$@"
fi

# Fallback: PyInstaller executable
if [ -x "${SCRIPT_DIR}/AudioLabEditor" ]; then
  exec "${SCRIPT_DIR}/AudioLabEditor" "$@"
fi

if [ -x "${APP_ROOT}/AudioLabEditor" ]; then
  exec "${APP_ROOT}/AudioLabEditor" "$@"
fi

# Last resort: run from source
export PYTHONPATH="${APP_ROOT}/src${PYTHONPATH:+:${PYTHONPATH}}"
cd "${APP_ROOT}" && exec python3 -m presentation.main "$@"
