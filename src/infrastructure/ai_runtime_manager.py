import importlib.util
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from infrastructure.runtime_paths import IS_FROZEN

STEM_PACKAGES: list[dict[str, str]] = [
    {"import": "torch", "pip": "torch>=2.0"},
    {"import": "torchaudio", "pip": "torchaudio>=2.0"},
    {"import": "dora", "pip": "dora-search>=0.4"},
    {"import": "julius", "pip": "julius>=0.3"},
    {"import": "einops", "pip": "einops>=0.8"},
    {"import": "omegaconf", "pip": "omegaconf>=2.3"},
    {"import": "yaml", "pip": "PyYAML>=6.0"},
    {"import": "numpy", "pip": "numpy>=1.26"},
    {"import": "tqdm", "pip": "tqdm>=4.66"},
    {"import": "lameenc", "pip": "lameenc>=1.7"},
    {"import": "openunmix", "pip": "openunmix>=1.3"},
]

TRANSCRIPTION_PACKAGES: list[dict[str, str]] = [
    {"import": "faster_whisper", "pip": "faster-whisper>=1.1.0"},
]

TTS_PACKAGES: list[dict[str, str]] = [
    {"import": "edge_tts", "pip": "edge-tts>=7.2.8"},
]


ProgressSink = Callable[[int | None, str], None]


@dataclass
class AiRuntimeStatus:
    available: bool = False
    missing: list[dict[str, str]] = field(default_factory=list)


def _ai_runtime_python() -> Path | None:
    from infrastructure.runtime_downloader import AI_DIR
    python = AI_DIR / "bin" / "python3"
    if sys.platform.startswith("win"):
        python = AI_DIR / "Scripts" / "python.exe"
    return python if python.exists() else None


def _check_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _check_via_runtime(module: str) -> bool:
    python = _ai_runtime_python()
    if not python:
        return False
    try:
        result = subprocess.run(
            [str(python), "-c", f"import {module}"],
            capture_output=True, text=True, timeout=15,
        )
        return result.returncode == 0
    except Exception:
        return False


def _check_bundled_or_system(module: str) -> bool:
    if _check_module(module):
        return True
    if _check_via_runtime(module):
        return True
    if not IS_FROZEN:
        return False
    try:
        result = subprocess.run(
            [sys.executable, "-c", f"import {module}"],
            capture_output=True, text=True, timeout=15,
        )
        return result.returncode == 0
    except Exception:
        return False


def _check_runtime(packages: list[dict[str, str]]) -> AiRuntimeStatus:
    missing: list[dict[str, str]] = []
    for pkg in packages:
        if not _check_bundled_or_system(pkg["import"]):
            missing.append(pkg)
    return AiRuntimeStatus(
        available=len(missing) == 0,
        missing=missing,
    )


def check_stem_runtime() -> AiRuntimeStatus:
    return _check_runtime(STEM_PACKAGES)


def check_transcription_runtime() -> AiRuntimeStatus:
    return _check_runtime(TRANSCRIPTION_PACKAGES)


def check_tts_runtime() -> AiRuntimeStatus:
    return _check_runtime(TTS_PACKAGES)
