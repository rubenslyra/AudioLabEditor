from infrastructure.ai_runtime_manager import (
    STEM_PACKAGES,
    TRANSCRIPTION_PACKAGES,
    TTS_PACKAGES,
    _check_module,
    check_stem_runtime,
)


def test_stem_packages_list_has_required_entries():
    imports = {p["import"] for p in STEM_PACKAGES}
    assert "torch" in imports
    assert "numpy" in imports
    assert "tqdm" in imports
    assert "openunmix" in imports
    assert len(STEM_PACKAGES) >= 11


def test_stem_packages_does_not_include_transcription():
    imports = {p["import"] for p in STEM_PACKAGES}
    assert "faster_whisper" not in imports
    assert "edge_tts" not in imports


def test_transcription_packages():
    imports = {p["import"] for p in TRANSCRIPTION_PACKAGES}
    assert "faster_whisper" in imports


def test_tts_packages():
    imports = {p["import"] for p in TTS_PACKAGES}
    assert "edge_tts" in imports


def test_check_module_known_package():
    assert _check_module("os") is True


def test_check_module_unknown_package():
    assert _check_module("_nonexistent_package_xyz_") is False


def test_check_stem_runtime_returns_status_object():
    status = check_stem_runtime()
    assert hasattr(status, "available")
    assert hasattr(status, "missing")
    assert hasattr(status, "python_path")
