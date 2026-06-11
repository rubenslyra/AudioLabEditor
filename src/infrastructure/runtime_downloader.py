import hashlib
import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path
from typing import Callable

from infrastructure.runtime_paths import app_data_dir

RUNTIME_DIR = app_data_dir() / "runtime"
AI_DIR = RUNTIME_DIR / "ai"
MODELS_DIR = app_data_dir() / "models"

ProgressSink = Callable[[int | None, str], None]

RUNTIME_BUNDLE_URL = "https://github.com/anomalyco/AudioLabEditor/releases/download/runtime-v1/audiolabeditor-runtime-linux-x86_64.tar.gz"
RUNTIME_BUNDLE_SHA256 = ""

DEMUCS_MODELS = {
    "htdemucs": "https://huggingface.co/facebook/demucs/resolve/main/htdemucs-4c7a3f8.th",
    "htdemucs_ft": "https://huggingface.co/facebook/demucs/resolve/main/htdemucs_ft-2f47bc2.th",
    "htdemucs_6s": "https://huggingface.co/facebook/demucs/resolve/main/htdemucs_6s-7b5ef63.th",
}


def _tool(name: str) -> str:
    resolved = shutil.which(name)
    if resolved:
        return resolved
    for candidate in ["curl", "wget", "python3 -m wget"]:
        c = shutil.which(candidate.split()[0])
        if c:
            return candidate
    raise RuntimeError("Nenhum downloader disponivel (curl/wget).")


def _download(url: str, dest: Path, progress_cb: ProgressSink | None = None) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tool = _tool("curl")
    if "curl" in tool:
        cmd = [tool, "-L", "-o", str(dest), url]
    else:
        cmd = [tool, url, "-O", str(dest)]
    if progress_cb:
        progress_cb(0, f"Baixando {dest.name}...")
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=str(dest.parent),
        )
        if proc.stdout:
            for line in proc.stdout:
                if progress_cb:
                    line = line.strip()
                    if line and "%" in line:
                        parts = line.split()
                        for p in parts:
                            if p.endswith("%"):
                                try:
                                    pct = int(p.rstrip("%"))
                                    progress_cb(pct, f"Baixando {dest.name}... {pct}%")
                                except ValueError:
                                    progress_cb(None, line)
        returncode = proc.wait()
        if returncode != 0:
            raise RuntimeError(f"Falha ao baixar {url} (codigo {returncode})")
    except FileNotFoundError:
        raise RuntimeError(f"Downloader nao encontrado: {tool}")
    if not dest.exists():
        raise RuntimeError(f"Arquivo nao foi baixado: {dest}")
    return dest


def _verify_hash(file_path: Path, expected_sha256: str) -> bool:
    if not expected_sha256:
        return True
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)
    return sha.hexdigest() == expected_sha256


def _extract(archive: Path, dest: Path, progress_cb: ProgressSink | None = None):
    if progress_cb:
        progress_cb(None, f"Extraindo {archive.name}...")
    dest.mkdir(parents=True, exist_ok=True)
    if archive.suffix == ".zip":
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(dest)
    else:
        with tarfile.open(archive) as tf:
            tf.extractall(dest)
    if progress_cb:
        progress_cb(100, f"Extraido para {dest}")


def ensure_runtime(progress_cb: ProgressSink | None = None) -> bool:
    ai_python = AI_DIR / "bin" / "python3"
    if ai_python.exists():
        return True

    if progress_cb:
        progress_cb(0, "Recursos de IA nao encontrados.")

    url = RUNTIME_BUNDLE_URL
    archive = RUNTIME_DIR / "runtime-bundle.tar.gz"
    try:
        _download(url, archive, progress_cb)
        if RUNTIME_BUNDLE_SHA256:
            if not _verify_hash(archive, RUNTIME_BUNDLE_SHA256):
                raise RuntimeError("Hash do runtime nao confere. Download corrompido.")
        _extract(archive, RUNTIME_DIR, progress_cb)
        archive.unlink(missing_ok=True)
        if progress_cb:
            progress_cb(100, "Runtime de IA instalado com sucesso.")
        return ai_python.exists()
    except Exception as exc:
        if progress_cb:
            progress_cb(None, f"Erro: {exc}")
        return False


def ensure_demucs_models(progress_cb: ProgressSink | None = None) -> bool:
    models_dest = MODELS_DIR / "demucs"
    models_dest.mkdir(parents=True, exist_ok=True)

    all_ok = True
    for name, url in DEMUCS_MODELS.items():
        model_file = models_dest / f"{name}.th"
        if model_file.exists():
            continue
        try:
            _download(url, model_file, progress_cb)
        except Exception as exc:
            if progress_cb:
                progress_cb(None, f"Falha ao baixar modelo {name}: {exc}")
            all_ok = False
    return all_ok
