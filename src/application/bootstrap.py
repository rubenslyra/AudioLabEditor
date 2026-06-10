import importlib
import os

from infrastructure.startup_doctor import startup_error_message, startup_warning_message


def _detect_profile() -> str:
    env = os.environ.get("AUDIO_LAB_EDITOR_PROFILE", "").lower()
    if env in ("ai", "full"):
        return env
    # Auto-detect: use "ai" only if torch is actually available
    if importlib.util.find_spec("torch") is not None:
        return "ai"
    return "base"


def validate_startup() -> tuple[str, str]:
    profile = _detect_profile()
    return startup_error_message(profile), startup_warning_message(profile)
