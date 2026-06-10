import importlib.util
import shutil
import subprocess
import sys
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
    python_path: str = ""


def _check_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _find_system_python() -> str | None:
    candidates = ["python3", "python"]
    for name in candidates:
        resolved = shutil.which(name)
        if resolved:
            return resolved
    return None


def _check_system_python(module: str) -> bool:
    if getattr(sys, "frozen", False):
        python = _find_system_python()
    else:
        python = sys.executable
    if not python:
        return False
    try:
        result = subprocess.run(
            [python, "-c", f"import {module}"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return result.returncode == 0
    except Exception:
        return False


def _check_runtime(packages: list[dict[str, str]]) -> AiRuntimeStatus:
    missing: list[dict[str, str]] = []
    for pkg in packages:
        if not _check_module(pkg["import"]):
            if not _check_system_python(pkg["import"]):
                missing.append(pkg)
    return AiRuntimeStatus(
        available=len(missing) == 0,
        missing=missing,
        python_path="python3" if getattr(sys, "frozen", False) else sys.executable,
    )


def check_stem_runtime() -> AiRuntimeStatus:
    return _check_runtime(STEM_PACKAGES)


def check_transcription_runtime() -> AiRuntimeStatus:
    return _check_runtime(TRANSCRIPTION_PACKAGES)


def check_tts_runtime() -> AiRuntimeStatus:
    return _check_runtime(TTS_PACKAGES)


def _pip_install_command(packages: list[str]) -> list[str]:
    python = "python3" if getattr(sys, "frozen", False) else sys.executable
    return [python, "-m", "pip", "install", "--upgrade"] + packages


def install_packages(packages: list[dict[str, str]], progress_cb: ProgressSink | None = None) -> AiRuntimeStatus:
    if not packages:
        return AiRuntimeStatus(available=True)

    pkg_names = [pkg["pip"].split(">=")[0] for pkg in packages]
    cmd = _pip_install_command(pkg_names)

    if progress_cb:
        progress_cb(0, f"Instalando {len(packages)} pacotes...")

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        lines: list[str] = []
        if process.stdout:
            for line in process.stdout:
                lines.append(line)
                if progress_cb:
                    line_stripped = line.strip()
                    if line_stripped:
                        progress_cb(None, line_stripped)

        returncode = process.wait()
        if returncode != 0:
            if progress_cb:
                progress_cb(None, f"pip falhou com codigo {returncode}")
                for l in lines[-3:]:
                    progress_cb(None, f"  {l.strip()}")
            failed_pips = [p["pip"] for p in packages]
            return AiRuntimeStatus(available=False, missing=packages)
    except FileNotFoundError:
        if progress_cb:
            progress_cb(None, "python3 ou pip nao encontrado no PATH do sistema.")
        return AiRuntimeStatus(available=False, missing=packages)
    except Exception as exc:
        if progress_cb:
            progress_cb(None, f"Erro na instalacao: {exc}")
        return AiRuntimeStatus(available=False, missing=packages)

    return AiRuntimeStatus(available=True)
