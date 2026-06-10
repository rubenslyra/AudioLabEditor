from infrastructure.startup_doctor import (
    check_startup_dependencies,
    startup_error_message,
)


def test_system_tools_are_required():
    statuses = check_startup_dependencies()

    ffmpeg = next(s for s in statuses if s.name == "ffmpeg")
    ffprobe = next(s for s in statuses if s.name == "ffprobe")

    assert ffmpeg.required is True
    assert ffprobe.required is True


def test_local_data_dir_is_required():
    statuses = check_startup_dependencies()

    data_dir = next(s for s in statuses if s.name == "local-data-dir")

    assert data_dir.required is True


def test_startup_error_empty_when_all_ok():
    message = startup_error_message()

    assert message == ""
