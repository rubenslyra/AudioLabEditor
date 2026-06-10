#!/usr/bin/env bash
set -euo pipefail

APP=AudioLabEditor
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
BUILD="$ROOT/dist"
APPDIR="$BUILD/$APP.AppDir"
PROFILE="${AUDIO_LAB_EDITOR_PROFILE:-base}"

echo "==> PyInstaller onefile build (profile=$PROFILE)..."
cd "$ROOT"
rm -rf dist build
AUDIO_LAB_EDITOR_PROFILE="$PROFILE" python3 -m PyInstaller "$HERE/AudioLabEditor.spec" --log-level WARN

echo "==> Creating AppDir..."
mkdir -p "$APPDIR"
cp "$BUILD/$APP" "$APPDIR/$APP"

cat > "$APPDIR/AppRun" <<'APPRUN'
#!/usr/bin/env bash
HERE="$(dirname "$(readlink -f "$0")")"
exec "$HERE/AudioLabEditor" "$@"
APPRUN
chmod +x "$APPDIR/AppRun"

# Extract icon from the internal assets (available after first run)
# Fallback: use source icon
cp "$ROOT/src/presentation/assets/logo.png" "$APPDIR/$APP.png"

cat > "$APPDIR/$APP.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Name=$APP
Comment=Capture, edit and separate audio stems
Exec=$APP
Icon=$APP
Categories=AudioVideo;Audio;Video;Utility;
Terminal=false
StartupNotify=true
StartupWMClass=audiolabeditor
DESKTOP

echo "==> Running appimagetool..."
rm -f "$BUILD/$APP-x86_64.AppImage"
/tmp/squashfs-root/AppRun "$APPDIR" "$BUILD/$APP-x86_64.AppImage"

echo "==> Done: $BUILD/$APP-x86_64.AppImage"
