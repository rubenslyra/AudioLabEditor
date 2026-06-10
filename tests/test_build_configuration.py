from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_install_script_defaults_to_base_profile():
    install_script = (ROOT / "scripts" / "install.sh").read_text(encoding="utf-8")

    assert 'PROFILE="${AUDIO_LAB_EDITOR_PROFILE:-base}"' in install_script


def test_pyinstaller_spec_still_supports_ai_profile():
    spec = (ROOT / "scripts" / "AudioLabEditor.spec").read_text(encoding="utf-8")

    assert '("demucs", "demucs", False, True)' in spec
    assert "collect_python_package(" in spec


def test_pyinstaller_spec_collects_demucs_runtime_dependencies():
    spec = (ROOT / "scripts" / "AudioLabEditor.spec").read_text(encoding="utf-8")

    for package in ("torch", "torchaudio", "lameenc", "openunmix", "julius", "dora"):
        assert f'("{package}",' in spec
    assert '("torch", "torch", True, False)' in spec
    assert '("torchaudio", "torchaudio", True, False)' in spec
