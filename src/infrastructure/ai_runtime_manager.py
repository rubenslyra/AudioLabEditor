import importlib.util
from dataclasses import dataclass, field
from typing import Callable

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


def _check_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _check_runtime(packages: list[dict[str, str]]) -> AiRuntimeStatus:
    missing: list[dict[str, str]] = []
    for pkg in packages:
        if not _check_module(pkg["import"]):
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
