import shutil
import sys
from os import environ
from pathlib import Path

IS_FROZEN = bool(getattr(sys, "frozen", False))
EXECUTABLE_DIR = Path(sys.executable).resolve().parent if IS_FROZEN else Path.cwd()
BUNDLE_DIR = Path(getattr(sys, "_MEIPASS", EXECUTABLE_DIR)).resolve()
APP_NAME = "AudioLabEditor"


def user_data_dir() -> Path:
    if sys.platform.startswith("win"):
        base = Path(environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
        return base / APP_NAME
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / APP_NAME
    base = Path(environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    return base / APP_NAME.lower()


def app_data_dir() -> Path:
    return user_data_dir()


def app_cache_dir() -> Path:
    if sys.platform.startswith("win"):
        base = Path(environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
        return base / APP_NAME / "Cache"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Caches" / APP_NAME
    base = Path(environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
    return base / APP_NAME.lower()


def runtime_dir() -> Path:
    return app_data_dir() / "runtime"


def tools_dir() -> Path:
    return runtime_dir() / "tools"


def models_dir() -> Path:
    return app_data_dir() / "models"


def candidate_dirs() -> list[Path]:
    anchors = [EXECUTABLE_DIR, BUNDLE_DIR, runtime_dir()]
    dirs: list[Path] = []
    for anchor in anchors:
        dirs.extend(
            [
                anchor,
                anchor / "_internal",
                anchor / "_internal" / "bin",
                anchor / "bin",
                anchor / "lib",
                anchor / "tools" / "bin",
                anchor / "ffmpeg" / "bin",
            ]
        )
    dirs.extend(
        [
            tools_dir(),
            tools_dir() / "bin",
            tools_dir() / "ffmpeg",
            tools_dir() / "ffmpeg" / "bin",
        ]
    )
    seen = set()
    unique = []
    for item in dirs:
        key = str(item)
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique


def platform_executable_names(name: str) -> list[str]:
    if sys.platform.startswith("win") and not name.lower().endswith(".exe"):
        return [f"{name}.exe", name]
    return [name]


def find_bundled_executable(name: str) -> Path | None:
    for directory in candidate_dirs():
        for executable_name in platform_executable_names(name):
            candidate = directory / executable_name
            if candidate.exists() and candidate.is_file():
                return candidate
    return None


def find_executable(name: str, *, allow_system_path: bool | None = None) -> Path | None:
    bundled = find_bundled_executable(name)
    if bundled:
        return bundled
    if allow_system_path is None:
        allow_system_path = not IS_FROZEN
    if allow_system_path:
        resolved = shutil.which(name)
        return Path(resolved) if resolved else None
    return None

