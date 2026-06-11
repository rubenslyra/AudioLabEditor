import importlib.util
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from infrastructure.runtime_paths import app_data_dir

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


def _venv_dir() -> Path:
    return app_data_dir() / "runtime" / "venv"


def _venv_python() -> Path:
    if sys.platform.startswith("win"):
        return _venv_dir() / "Scripts" / "python.exe"
    return _venv_dir() / "bin" / "python"


def _ensure_venv(progress_cb: ProgressSink | None = None) -> str | None:
    venv_python = _venv_python()
    if venv_python.exists():
        return str(venv_python)

    if progress_cb:
        progress_cb(0, "Preparando ambiente isolado...")

    python = _find_system_python()
    if not python:
        if progress_cb:
            progress_cb(None, "Python nao encontrado no sistema.")
        return None

    try:
        _venv_dir().parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [python, "-m", "venv", str(_venv_dir())],
            capture_output=True,
            text=True,
            timeout=120,
            check=True,
        )
        if progress_cb:
            progress_cb(50, "Ambiente isolado criado.")
        return str(_venv_python())
    except subprocess.CalledProcessError as exc:
        if progress_cb:
            progress_cb(None, f"Falha ao criar ambiente virtual: {exc.stderr}")
        return None
    except Exception as exc:
        if progress_cb:
            progress_cb(None, f"Erro ao preparar ambiente: {exc}")
        return None


def _check_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _find_system_python() -> str | None:
    candidates = ["python3", "python"]
    if sys.platform.startswith("win"):
        candidates = ["python", "python3", "py"]
    for name in candidates:
        resolved = shutil.which(name)
        if resolved:
            return resolved
    return None


def _check_venv_python(module: str) -> bool:
    venv_python = _venv_python()
    if not venv_python.exists():
        return False
    try:
        result = subprocess.run(
            [str(venv_python), "-c", f"import {module}"],
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
        if _check_module(pkg["import"]):
            continue
        if _check_venv_python(pkg["import"]):
            continue
        missing.append(pkg)
    return AiRuntimeStatus(
        available=len(missing) == 0,
        missing=missing,
        python_path=str(_venv_python()) if _venv_python().exists() else _find_system_python() or "python",
    )


def check_stem_runtime() -> AiRuntimeStatus:
    return _check_runtime(STEM_PACKAGES)


def check_transcription_runtime() -> AiRuntimeStatus:
    return _check_runtime(TRANSCRIPTION_PACKAGES)


def check_tts_runtime() -> AiRuntimeStatus:
    return _check_runtime(TTS_PACKAGES)


def install_packages(packages: list[dict[str, str]], progress_cb: ProgressSink | None = None) -> AiRuntimeStatus:
    if not packages:
        return AiRuntimeStatus(available=True)

    python = _ensure_venv(progress_cb)
    if not python:
        return AiRuntimeStatus(available=False, missing=packages)

    pkg_names = [pkg["pip"].split(">=")[0] for pkg in packages]
    total = len(pkg_names)

    if progress_cb:
        progress_cb(1, f"Instalando {total} pacote(s) no ambiente isolado...")

    cmd = [python, "-m", "pip", "install"] + pkg_names

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
                progress_cb(None, f"Falha na instalacao (codigo {returncode}).")
                for line in lines[-3:]:
                    progress_cb(None, f"  {line.strip()}")
            return AiRuntimeStatus(available=False, missing=packages)
    except FileNotFoundError:
        if progress_cb:
            progress_cb(None, "Python ou pip nao encontrado no ambiente isolado.")
        return AiRuntimeStatus(available=False, missing=packages)
    except Exception as exc:
        if progress_cb:
            progress_cb(None, f"Erro na instalacao: {exc}")
        return AiRuntimeStatus(available=False, missing=packages)

    if progress_cb:
        progress_cb(100, "Instalacao concluida com sucesso.")
    return AiRuntimeStatus(available=True)
