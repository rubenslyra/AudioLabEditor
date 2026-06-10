import importlib
import os

from infrastructure.startup_doctor import startup_error_message


def _detect_profile() -> str:
    env = os.environ.get("AUDIO_LAB_EDITOR_PROFILE", "").lower()
    if env in ("ai", "full"):
        return env
    # Auto-detect: use "ai" only if demucs is actually available
    if importlib.util.find_spec("demucs") is not None:
        return "ai"
    return "base"


def validate_startup() -> str:
    profile = _detect_profile()
    return startup_error_message(profile)
