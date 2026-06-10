from infrastructure import runtime_paths


def test_frozen_lookup_does_not_use_system_path(monkeypatch, tmp_path):
    monkeypatch.setattr(runtime_paths, "IS_FROZEN", True)
    monkeypatch.setattr(runtime_paths, "EXECUTABLE_DIR", tmp_path / "app")
    monkeypatch.setattr(runtime_paths, "BUNDLE_DIR", tmp_path / "app" / "_internal")
    monkeypatch.setattr(runtime_paths.shutil, "which", lambda _name: "/usr/bin/ffmpeg")

    assert runtime_paths.find_executable("ffmpeg") is None


def test_bundled_executable_is_preferred(monkeypatch, tmp_path):
    bin_dir = tmp_path / "app" / "_internal" / "bin"
    bin_dir.mkdir(parents=True)
    binary = bin_dir / "ffmpeg"
    binary.write_text("binary", encoding="utf-8")
    monkeypatch.setattr(runtime_paths, "IS_FROZEN", True)
    monkeypatch.setattr(runtime_paths, "EXECUTABLE_DIR", tmp_path / "app")
    monkeypatch.setattr(runtime_paths, "BUNDLE_DIR", tmp_path / "app" / "_internal")

    assert runtime_paths.find_executable("ffmpeg") == binary


def test_managed_runtime_executable_is_used_in_frozen_mode(monkeypatch, tmp_path):
    runtime = tmp_path / "data" / "runtime"
    bin_dir = runtime / "tools" / "ffmpeg" / "bin"
    bin_dir.mkdir(parents=True)
    binary = bin_dir / "ffmpeg"
    binary.write_text("binary", encoding="utf-8")

    monkeypatch.setattr(runtime_paths, "IS_FROZEN", True)
    monkeypatch.setattr(runtime_paths, "EXECUTABLE_DIR", tmp_path / "app")
    monkeypatch.setattr(runtime_paths, "BUNDLE_DIR", tmp_path / "app" / "_internal")
    monkeypatch.setattr(runtime_paths, "runtime_dir", lambda: runtime)
    monkeypatch.setattr(runtime_paths, "tools_dir", lambda: runtime / "tools")
    monkeypatch.setattr(runtime_paths.shutil, "which", lambda _name: "/usr/bin/ffmpeg")

    assert runtime_paths.find_executable("ffmpeg") == binary


def test_linux_data_dir_uses_xdg_data_home(monkeypatch, tmp_path):
    monkeypatch.setattr(runtime_paths.sys, "platform", "linux")
    monkeypatch.setitem(runtime_paths.environ, "XDG_DATA_HOME", str(tmp_path / "xdg-data"))

    assert runtime_paths.app_data_dir() == tmp_path / "xdg-data" / "audiolabeditor"
