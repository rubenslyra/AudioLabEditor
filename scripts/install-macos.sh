#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
APP="audiolab-editor"
BINARY_NAME="AudioLabEditor"
BUNDLE_NAME="AudioLabEditor.app"
INSTALL_DIR="${HOME}/Applications"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --system) INSTALL_DIR="/Applications"; shift ;;
    --prefix) INSTALL_DIR="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

BINARY_PATH="${ROOT}/dist/${BINARY_NAME}"
if [ ! -f "$BINARY_PATH" ]; then
  echo "ERROR: Build not found at ${BINARY_PATH}. Run 'python3 -m PyInstaller scripts/AudioLabEditor.spec' first."
  exit 1
fi

echo "==> Creating .app bundle..."
BUNDLE_PATH="${INSTALL_DIR}/${BUNDLE_NAME}"
mkdir -p "${BUNDLE_PATH}/Contents/MacOS"
mkdir -p "${BUNDLE_PATH}/Contents/Resources"

cp "$BINARY_PATH" "${BUNDLE_PATH}/Contents/MacOS/${APP}"
chmod 755 "${BUNDLE_PATH}/Contents/MacOS/${APP}"

ICON_SRC="${ROOT}/src/presentation/assets/logo.png"
if [ -f "$ICON_SRC" ]; then
  ICON_DST="${BUNDLE_PATH}/Contents/Resources/${APP}.icns"
  if command -v iconutil &>/dev/null; then
    # Convert PNG to ICNS via iconset (macOS built-in)
    ICONSET=$(mktemp -d)
    sips -z 256 256 "$ICON_SRC" --out "${ICONSET}/icon_256x256.png" &>/dev/null || true
    cp "$ICON_SRC" "${ICONSET}/icon_256x256.png" 2>/dev/null || true
    iconutil -c icns "${ICONSET}" -o "$ICON_DST" 2>/dev/null || true
    rm -rf "$ICONSET"
  fi
  if [ ! -f "$ICON_DST" ]; then
    cp "$ICON_SRC" "${BUNDLE_PATH}/Contents/Resources/${APP}.png"
  fi
fi

cat > "${BUNDLE_PATH}/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleExecutable</key>
  <string>${APP}</string>
  <key>CFBundleIdentifier</key>
  <string>com.rubenslyra.audiolab-editor</string>
  <key>CFBundleName</key>
  <string>AudioLab Editor</string>
  <key>CFBundleDisplayName</key>
  <string>AudioLab Editor</string>
  <key>CFBundleVersion</key>
  <string>1.0</string>
  <key>CFBundleShortVersionString</key>
  <string>1.0</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>LSMinimumSystemVersion</key>
  <string>10.15</string>
  <key>NSHighResolutionCapable</key>
  <true/>
  <key>NSAppTransportSecurity</key>
  <dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
  </dict>
</dict>
</plist>
PLIST

echo "==> Creating symlink in /usr/local/bin..."
mkdir -p /usr/local/bin
ln -sf "${BUNDLE_PATH}/Contents/MacOS/${APP}" "/usr/local/bin/${APP}"

echo ""
echo "==> Instalacao concluida!"
echo "    App Bundle: ${BUNDLE_PATH}"
echo "    Executavel: /usr/local/bin/${APP}"
echo ""
echo "    Abra o 'AudioLab Editor' do Launchpad ou execute '${APP}' no terminal."
echo "    Para desinstalar: rm -rf '${BUNDLE_PATH}' '/usr/local/bin/${APP}'"
