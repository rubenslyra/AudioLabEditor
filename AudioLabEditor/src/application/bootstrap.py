import os

from infrastructure.startup_doctor import startup_error_message


def validate_startup() -> str:
    profile = os.environ.get("AUDIO_LAB_EDITOR_PROFILE", "ai")
    return startup_error_message(profile)
