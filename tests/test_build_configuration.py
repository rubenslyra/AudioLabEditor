from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_install_script_defaults_to_base_profile():
    install_script = (ROOT / "scripts" / "install.sh").read_text(encoding="utf-8")

    assert 'PROFILE="${AUDIO_LAB_EDITOR_PROFILE:-base}"' in install_script


def test_pyinstaller_spec_collects_torch_for_ai_profile():
    spec = (ROOT / "scripts" / "AudioLabEditor.spec").read_text(encoding="utf-8")

    assert '("torch", "torch", True, False)' in spec
    assert "collect_python_package(" in spec


def test_pyinstaller_spec_includes_demucs_as_hidden_import():
    spec = (ROOT / "scripts" / "AudioLabEditor.spec").read_text(encoding="utf-8")

    assert 'hiddenimports += ["demucs"]' in spec
