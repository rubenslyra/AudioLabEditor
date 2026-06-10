# -*- mode: python ; coding: utf-8 -*-

import os
import shutil
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules, copy_metadata


project_root = Path(SPECPATH).resolve().parent
src_root = project_root / "src"
profile = os.environ.get("AUDIO_LAB_EDITOR_PROFILE", "base").lower()


def safe_collect_submodules(package_name):
    try:
        return collect_submodules(package_name)
    except Exception:
        return []


def safe_collect_data_files(package_name):
    try:
        return collect_data_files(package_name, include_py_files=False)
    except Exception:
        return []


def safe_collect_dynamic_libs(package_name):
    try:
        return collect_dynamic_libs(package_name)
    except Exception:
        return []


def safe_copy_metadata(distribution_name):
    try:
        return copy_metadata(distribution_name)
    except Exception:
        return []


def collect_python_package(package_name, distribution_name=None, include_dynamic_libs=False, include_submodules=True):
    collected_datas = safe_collect_data_files(package_name)
    collected_binaries = safe_collect_dynamic_libs(package_name) if include_dynamic_libs else []
    collected_hiddenimports = safe_collect_submodules(package_name) if include_submodules else []
    collected_metadata = safe_copy_metadata(distribution_name or package_name)
    return collected_datas + collected_metadata, collected_binaries, collected_hiddenimports


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
    "presentation.tabs.trim_tab",
    "presentation.tabs.video_editor_tab",
    "application.bootstrap",
    "application.capture_media_use_case",
    "application.separate_audio_use_case",
    "application.output_organizer",
    "infrastructure.path_config",
    "infrastructure.settings_store",
    "infrastructure.runtime_paths",
    "infrastructure.startup_doctor",
    "infrastructure.demucs_adapter",
    "infrastructure.downloader_adapter",
    "infrastructure.ffmpeg_adapter",
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

for package_name in ["customtkinter", "yt_dlp", "PIL"]:
    datas += safe_collect_data_files(package_name)
    hiddenimports += safe_collect_submodules(package_name)

for distribution_name in ["customtkinter", "yt-dlp", "pillow"]:
    datas += safe_copy_metadata(distribution_name)

if profile in {"ai", "full"}:
    ai_packages = [
        ("demucs", "demucs", False, True),
        ("dora", "dora-search", False, True),
        ("julius", "julius", False, True),
        ("lameenc", "lameenc", True, True),
        ("openunmix", "openunmix", False, True),
        ("torch", "torch", True, False),
        ("torchaudio", "torchaudio", True, False),
        ("faster_whisper", "faster-whisper", False, True),
        ("edge_tts", "edge-tts", False, True),
        ("ctranslate2", "ctranslate2", True, False),
    ]
    for package_name, distribution_name, include_dynamic_libs, include_submodules in ai_packages:
        package_datas, package_binaries, package_hiddenimports = collect_python_package(
            package_name,
            distribution_name,
            include_dynamic_libs=include_dynamic_libs,
            include_submodules=include_submodules,
        )
        datas += package_datas
        binaries += package_binaries
        hiddenimports += package_hiddenimports

if profile == "full":
    full_packages = [
        ("paddleocr", "paddleocr", False, True),
        ("paddle", "paddlepaddle", True, False),
    ]
    for package_name, distribution_name, include_dynamic_libs, include_submodules in full_packages:
        package_datas, package_binaries, package_hiddenimports = collect_python_package(
            package_name,
            distribution_name,
            include_dynamic_libs=include_dynamic_libs,
            include_submodules=include_submodules,
        )
        datas += package_datas
        binaries += package_binaries
        hiddenimports += package_hiddenimports

excludes = ["pytest", "numpy.tests", "PIL.tests"]
if profile == "base":
    excludes += ["demucs", "faster_whisper", "edge_tts", "paddle", "paddleocr"]
if profile == "ai":
    excludes += ["paddle", "paddleocr"]


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
    upx=True,
    upx_exclude=[],
    console=False,
)
