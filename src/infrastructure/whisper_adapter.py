import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from domain.interfaces import ProgressCallback, TranscriptionPort, TranscriptionRequest, TranscriptionResult

WHISPER_LANGUAGES = {
    "Português (BR)": "pt",
    "Inglês": "en",
    "Espanhol": "es",
    "Francês": "fr",
    "Alemão": "de",
    "Italiano": "it",
    "Japonês": "ja",
    "Chinês": "zh",
    "Árabe": "ar",
    "Hindi": "hi",
}

WHISPER_MODELS = ["tiny", "base", "small", "medium", "large-v3"]


class WhisperError(RuntimeError):
    pass


class WhisperSubprocessAdapter(TranscriptionPort):
    def __init__(self, frozen: bool = False):
        self._frozen = frozen

    def transcribe(self, request: TranscriptionRequest, progress_cb: ProgressCallback = None) -> TranscriptionResult:
        if not request.source_path.exists():
            raise WhisperError(f"Arquivo nao encontrado: {request.source_path}")

        self._notify(progress_cb, 0.0, "Iniciando transcricao com faster-whisper...")

        dest = Path(request.dest_dir)
        project = request.project_name or "ALE"
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_dir = dest / project / f"transcription-{timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)

        script = self._build_script(request, output_dir)

        env = os.environ.copy()
        env["PYTHONWARNINGS"] = "ignore"

        if self._frozen:
            self._run_in_process(script, progress_cb)
        else:
            self._run_subprocess(script, env, progress_cb)

        result_file = output_dir / "result.json"
        if not result_file.exists():
            raise WhisperError("Falha ao obter resultado da transcricao.")

        with open(result_file) as f:
            data = json.load(f)

        return TranscriptionResult(
            output_dir=output_dir,
            source_name=request.source_path.stem,
            language=data.get("language", request.language),
            segments_count=data.get("segments_count", 0),
        )

    def _build_script(self, request: TranscriptionRequest, output_dir: Path) -> str:
        source = str(request.source_path.resolve())
        output = str(output_dir.resolve())
        return (
            "import json, sys\n"
            "from faster_whisper import WhisperModel\n"
            f"model = WhisperModel('{request.model_size}', device='cpu', compute_type='int8')\n"
            f"segments, info = model.transcribe('{source}', language='{request.language}')\n"
            "result = {'language': info.language, 'duration': info.duration, 'segments_count': 0}\n"
            "segments_list = []\n"
            "for i, seg in enumerate(segments):\n"
            "    segments_list.append({'start': seg.start, 'end': seg.end, 'text': seg.text})\n"
            "result['segments_count'] = len(segments_list)\n"
            "with open(os.path.join(output_dir, 'transcript.txt'), 'w') as f:\n"
            "    for seg in segments_list:\n"
            "        f.write(f'[{seg[\"start\"]:.2f}s -> {seg[\"end\"]:.2f}s] {seg[\"text\"]}\\n')\n"
            "with open(os.path.join(output_dir, 'transcript.srt'), 'w') as f:\n"
            "    for i, seg in enumerate(segments_list, 1):\n"
            "        start_s = _fmt_srt(seg['start'])\n"
            "        end_s = _fmt_srt(seg['end'])\n"
            "        f.write(f'{i}\\n{start_s} --> {end_s}\\n{seg[\"text\"]}\\n\\n')\n"
            f"with open('{output}/result.json', 'w') as f:\n"
            "    json.dump(result, f)\n"
            "def _fmt_srt(secs):\n"
            "    h = int(secs // 3600); m = int((secs % 3600) // 60); s = int(secs % 60); ms = int((secs % 1) * 1000)\n"
            "    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'\n"
        )

    def _run_subprocess(self, script: str, env: dict[str, str], progress_cb: ProgressCallback):
        python = self._resolve_python()
        process = subprocess.Popen(
            [python, "-c", script],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=env,
        )
        self._stream_output(process, progress_cb)

    def _run_in_process(self, script: str, progress_cb: ProgressCallback):
        import io
        from contextlib import redirect_stdout

        old_env = os.environ.copy()
        old_argv = sys.argv[:]
        try:
            env = os.environ.copy()
            env["PYTHONWARNINGS"] = "ignore"
            os.environ.update(env)
            sys.argv = ["whisper"]
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(script)
                f.flush()
                script_path = f.name
            stream = io.StringIO()
            with redirect_stdout(stream):
                try:
                    exec(open(script_path).read())
                except Exception as exc:
                    raise WhisperError(f"Transcricao falhou: {exc}") from exc
            output = stream.getvalue()
            if output.strip() and progress_cb:
                progress_cb(None, output.strip())
        finally:
            os.environ.clear()
            os.environ.update(old_env)
            sys.argv = old_argv
            if "script_path" in locals():
                Path(script_path).unlink(missing_ok=True)
        self._notify(progress_cb, 100.0, "Transcricao concluida com sucesso.")

    def _stream_output(self, process: subprocess.Popen, progress_cb: ProgressCallback):
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
            raise WhisperError(f"Transcricao falhou com codigo {return_code}")
        self._notify(progress_cb, 100.0, "Transcricao concluida com sucesso.")

    @staticmethod
    def _process_line(line: str, started_at: float, progress_cb: ProgressCallback):
        elapsed = int(time.monotonic() - started_at)
        mins, secs = divmod(elapsed, 60)
        elapsed_str = f"{mins}min{secs:02d}s" if mins else f"{secs}s"
        if "%" in line:
            import re
            m = re.search(r"(\d+)%", line)
            if m:
                pct = min(100, int(m.group(1)))
                if progress_cb:
                    progress_cb(float(pct), f"Transcrevendo: {pct}% ({elapsed_str})")
        elif progress_cb:
            progress_cb(None, line)

    def _resolve_python(self) -> str:
        import shutil
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

    @staticmethod
    def _notify(cb: ProgressCallback, percent: float, message: str):
        if cb:
            cb(percent, message)
