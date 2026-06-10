from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_install_script_has_core_build():
    install_script = (ROOT / "scripts" / "install.sh").read_text(encoding="utf-8")

    assert "AudioLabEditor.spec" in install_script


def test_pyinstaller_spec_excludes_torch():
    spec = (ROOT / "scripts" / "AudioLabEditor.spec").read_text(encoding="utf-8")

    assert "demucs" in spec
    assert "torch" in spec


def test_pyinstaller_spec_includes_core_packages():
    spec = (ROOT / "scripts" / "AudioLabEditor.spec").read_text(encoding="utf-8")

    assert "presentation.tabs.stem_tab" in spec
    assert "infrastructure.ai_runtime_manager" in spec
