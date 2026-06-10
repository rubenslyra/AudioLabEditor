from infrastructure.startup_doctor import (
    check_startup_dependencies,
    startup_error_message,
    startup_warning_message,
)


def test_system_tools_are_required():
    statuses = check_startup_dependencies("base")

    ffmpeg = next(s for s in statuses if s.name == "ffmpeg")
    ffprobe = next(s for s in statuses if s.name == "ffprobe")

    assert ffmpeg.required is True
    assert ffprobe.required is True


def test_demucs_is_optional_in_ai_profile():
    statuses = check_startup_dependencies("ai")

    demucs = next(s for s in statuses if s.name == "demucs")

    assert demucs.required is False


def test_faster_whisper_is_optional_in_full_profile():
    statuses = check_startup_dependencies("full")

    whisper = next(s for s in statuses if s.name == "faster-whisper")

    assert whisper.required is False


def test_local_data_dir_is_required():
    statuses = check_startup_dependencies("base")

    data_dir = next(s for s in statuses if s.name == "local-data-dir")

    assert data_dir.required is True


def test_startup_error_ignores_optional_missing():
    message = startup_error_message("ai")

    err = message
    if err:
        assert "demucs" not in err


def test_startup_warning_includes_optional_missing():
    message = startup_warning_message("ai")

    if message:
        assert "opcionais" in message
