# -*- mode: python ; coding: utf-8 -*-

import os
import shutil
import subprocess
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules, copy_metadata


project_root = Path(SPECPATH).resolve().parent
src_root = project_root / "src"


def safe_collect_data_files(package_name):
    try:
        return collect_data_files(package_name, include_py_files=False)
    except Exception:
        return []


def safe_collect_submodules(package_name):
    try:
        return collect_submodules(package_name)
    except Exception:
        return []


def safe_copy_metadata(distribution_name):
    try:
        return copy_metadata(distribution_name)
    except Exception:
        return []


def collect_tool_binary(name, env_name):
    explicit = os.environ.get(env_name)
    candidate = Path(explicit) if explicit else None
    if candidate and candidate.exists():
        return [(str(candidate), "bin")]
    resolved = shutil.which(name)
    if resolved:
        return [(resolved, "bin")]
    return []


datas = []
binaries = []
hiddenimports = []

hiddenimports += [
    "presentation.main",
    "presentation.splash",
    "presentation.widgets",
    "presentation.tabs.capture_tab",
    "presentation.tabs.stem_tab",
    "presentation.tabs.transcription_tab",
    "presentation.tabs.trim_tab",
    "presentation.tabs.tts_tab",
    "presentation.tabs.video_editor_tab",
    "application.bootstrap",
    "application.batch_separate_audio_use_case",
    "application.capture_media_use_case",
    "application.generate_tts_use_case",
    "application.separate_audio_use_case",
    "application.transcribe_audio_use_case",
    "application.output_organizer",
    "infrastructure.edge_tts_adapter",
    "infrastructure.path_config",
    "infrastructure.settings_store",
    "infrastructure.runtime_paths",
    "infrastructure.startup_doctor",
    "infrastructure.demucs_adapter",
    "infrastructure.downloader_adapter",
    "infrastructure.ffmpeg_adapter",
    "infrastructure.ai_runtime_manager",
    "infrastructure.runtime_downloader",
    "infrastructure.whisper_adapter",
    "domain.entities",
    "domain.interfaces",
    "domain.dependencies",
]

assets_dir = src_root / "presentation" / "assets"

if assets_dir.exists():
    for asset_file in assets_dir.iterdir():
        if asset_file.is_file():
            datas.append((str(asset_file), "presentation/assets"))
    print(f"[AudioLabEditor.spec] Assets included from {assets_dir}")
else:
    print(f"[AudioLabEditor.spec] WARNING: assets dir not found at {assets_dir}")

binaries += collect_tool_binary("ffmpeg", "AUDIO_LAB_EDITOR_FFMPEG")
binaries += collect_tool_binary("ffprobe", "AUDIO_LAB_EDITOR_FFPROBE")

for package_name in ["customtkinter", "yt_dlp", "PIL", "faster_whisper", "edge_tts"]:
    datas += safe_collect_data_files(package_name)
    hiddenimports += safe_collect_submodules(package_name)

for distribution_name in ["customtkinter", "yt-dlp", "pillow", "faster-whisper", "edge-tts"]:
    datas += safe_copy_metadata(distribution_name)

excludes = ["pytest", "numpy.tests", "PIL.tests", "torch", "torchaudio", "demucs"]

a = Analysis(
    [str(src_root / "presentation" / "main.py")],
    pathex=[str(src_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name="AudioLabEditor",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=sys.platform != "darwin",
    upx_exclude=[],
    console=False,
)
