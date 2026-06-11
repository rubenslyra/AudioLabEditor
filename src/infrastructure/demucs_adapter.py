import importlib.util
import os
import re
import shutil
import subprocess
import sys
import time
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from domain.interfaces import DemucsPort, ProgressCallback, StemRequest, StemResult

STEM_MODES = ("vocals", "full4", "extended6")
STEM_FORMATS = ("wav", "mp3", "flac")


class DemucsError(RuntimeError):
    pass


class MissingDependencyError(DemucsError):
    pass


class DemucsSubprocessAdapter(DemucsPort):
    def __init__(self, model_cache_dir: Path | None = None, frozen: bool = False):
        self._model_cache_dir = model_cache_dir or Path.home() / ".cache" / "torch" / "hub"
        self._frozen = frozen

    def separate(self, request: StemRequest, progress_cb: ProgressCallback = None) -> StemResult:
        if not self._torch_available():
            raise MissingDependencyError(
                "PyTorch nao encontrado no ambiente.\n"
                "Instale as dependencias de IA: pip install 'audiolab-editor[ai]'"
            )

        self._notify(progress_cb, 0.0, "Iniciando separacao de stems com Demucs...")

        mode_config = {
            "vocals": {"model": "htdemucs", "two_stems": "vocals"},
            "full4": {"model": "htdemucs", "two_stems": None},
            "extended6": {"model": "htdemucs_6s", "two_stems": None},
        }

        cfg = mode_config.get(request.mode)
        if not cfg:
            raise DemucsError(f"Modo de separacao invalido: {request.mode}")
        if request.output_format not in STEM_FORMATS:
            raise DemucsError(f"Formato de saida invalido: {request.output_format}")

        dest = Path(request.dest_dir)
        project = request.project_name or "ALE"
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_dir = dest / project / f"audio-stem-{request.mode}-{timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)

        demucs_args = [
            "-n",
            cfg["model"],
            "-o",
            str(output_dir),
        ]
        if cfg["two_stems"]:
            demucs_args.extend(["--two-stems", cfg["two_stems"]])
        if request.output_format == "mp3":
            demucs_args.extend(["--mp3", "--mp3-bitrate", "320"])
        elif request.output_format == "flac":
            demucs_args.append("--flac")
        demucs_args.append(str(request.source_path))

        env = os.environ.copy()
        env["PYTHONWARNINGS"] = "ignore"
        self._model_cache_dir.mkdir(parents=True, exist_ok=True)
        env.setdefault("TORCH_HOME", str(self._model_cache_dir))
        env.setdefault("XDG_CACHE_HOME", str(self._model_cache_dir.parent))

        if self._frozen:
            self._run_in_process(demucs_args, env, progress_cb)
        else:
            self._run_subprocess(demucs_args, env, progress_cb)

        return StemResult(
            output_dir=output_dir,
            mode=request.mode,
            output_format=request.output_format,
            source_name=request.source_path.stem,
        )

    def _torch_available(self) -> bool:
        if self._frozen:
            return False
        if importlib.util.find_spec("torch") is not None:
            return True
        python = self._resolve_python()
        try:
            result = subprocess.run([python, "-c", "import torch"], capture_output=True, text=True, timeout=15)
            return result.returncode == 0
        except Exception:
            return False

    def _resolve_python(self) -> str:
        from infrastructure.ai_runtime_manager import _venv_python
        venv = _venv_python()
        if venv.exists():
            return str(venv)
        if getattr(sys, "frozen", False):
            candidates = ["python3", "python"]
            if sys.platform.startswith("win"):
                candidates = ["python", "python3", "py"]
            for name in candidates:
                resolved = shutil.which(name)
                if resolved:
                    return resolved
            return "python" if sys.platform.startswith("win") else "python3"
        return sys.executable

    def _run_subprocess(self, demucs_args: list[str], env: dict[str, str], progress_cb: ProgressCallback):
        python = self._resolve_python()
        command = [python, "-m", "demucs"] + demucs_args
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=env,
        )
        buffer = ""
        started_at = time.monotonic()

        while True:
            char = process.stdout.read(1) if process.stdout else ""
            if char == "" and process.poll() is not None:
                break
            if not char:
                continue
            if char in ("\r", "\n"):
                line = buffer.strip()
                buffer = ""
                if line:
                    self._process_line(line, started_at, progress_cb)
            else:
                buffer += char

        if buffer.strip() and progress_cb:
            progress_cb(None, buffer.strip())

        return_code = process.wait()
        if return_code:
            raise DemucsError(f"Demucs falhou com codigo {return_code}")
        self._notify(progress_cb, 100.0, "Stems gerados com sucesso.")

    def _run_in_process(self, demucs_args: list[str], env: dict[str, str], progress_cb: ProgressCallback):
        old_env = os.environ.copy()
        old_argv = sys.argv[:]
        try:
            os.environ.update(env)
            sys.argv = ["demucs"] + demucs_args
            try:
                from demucs.separate import main as demucs_main
            except Exception as exc:
                raise MissingDependencyError("PyTorch/demucs empacotado de forma incompleta.") from exc
            stream = _ProgressStream(progress_cb)
            with redirect_stdout(stream), redirect_stderr(stream):
                demucs_main()
        except SystemExit as exc:
            code = int(exc.code or 0) if isinstance(exc.code, int) else 1
            if code:
                raise DemucsError(f"Demucs falhou com codigo {code}") from exc
        finally:
            os.environ.clear()
            os.environ.update(old_env)
            sys.argv = old_argv
        self._notify(progress_cb, 100.0, "Stems gerados com sucesso.")

    @staticmethod
    def _process_line(line: str, started_at: float, progress_cb: ProgressCallback):
        percent_match = re.search(r"(\d{1,3})%", line)
        elapsed = int(time.monotonic() - started_at)
        mins, secs = divmod(elapsed, 60)
        elapsed_str = f"{mins}min{secs:02d}s" if mins else f"{secs}s"
        if percent_match:
            pct = min(100, int(percent_match.group(1)))
            if progress_cb:
                progress_cb(float(pct), f"Separando stems: {pct}% ({elapsed_str})")
        elif "Separating track" in line and progress_cb:
            progress_cb(None, "Analisando e separando a musica...")

    @staticmethod
    def _notify(cb: ProgressCallback, percent: float, message: str):
        if cb:
            cb(percent, message)


class _ProgressStream:
    def __init__(self, progress_cb: ProgressCallback):
        self.progress_cb = progress_cb
        self.buffer = ""

    def write(self, text: str):
        for char in text:
            if char in ("\r", "\n"):
                self._flush()
            else:
                self.buffer += char
        return len(text)

    def flush(self):
        self._flush()

    def _flush(self):
        line = self.buffer.strip()
        self.buffer = ""
        if not line or not self.progress_cb:
            return
        percent_match = re.search(r"(\d{1,3})%", line)
        if percent_match:
            pct = min(100, int(percent_match.group(1)))
            self.progress_cb(float(pct), f"Separando stems: {pct}%")
        elif "Separating track" in line:
            self.progress_cb(None, "Analisando e separando a musica...")
