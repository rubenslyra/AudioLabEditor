#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Prefer single-file executable
ONEFILE="${APP_ROOT}/dist/AudioLabEditor"
if [ -x "$ONEFILE" ]; then
  exec "$ONEFILE" "$@"
fi

# Fallback: AppImage
APPIMAGE="${APP_ROOT}/dist/AudioLabEditor-x86_64.AppImage"
if [ -x "$APPIMAGE" ]; then
  exec "$APPIMAGE" "$@"
fi

# Last resort: run from source
export PYTHONPATH="${APP_ROOT}/src${PYTHONPATH:+:${PYTHONPATH}}"
cd "${APP_ROOT}" && exec python3 -m presentation.main "$@"
