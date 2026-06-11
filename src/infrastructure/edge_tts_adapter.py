import os
import re
import subprocess
import sys
import time
from pathlib import Path

from domain.interfaces import ProgressCallback, TtsPort, TtsRequest, TtsResult

TTS_VOICES = [
    "pt-BR-FranciscaNeural",
    "pt-BR-AntonioNeural",
    "pt-PT-DuarteNeural",
    "pt-PT-RaquelNeural",
    "en-US-JennyNeural",
    "en-US-GuyNeural",
    "en-GB-SoniaNeural",
    "en-GB-RyanNeural",
    "es-ES-AlvaroNeural",
    "es-ES-ElviraNeural",
    "fr-FR-DeniseNeural",
    "fr-FR-HenriNeural",
    "de-DE-KatjaNeural",
    "de-DE-ConradNeural",
    "it-IT-ElsaNeural",
    "it-IT-DiegoNeural",
    "ja-JP-NanamiNeural",
    "zh-CN-XiaoxiaoNeural",
]


class TtsError(RuntimeError):
    pass


class EdgeTtsSubprocessAdapter(TtsPort):
    def __init__(self, frozen: bool = False):
        self._frozen = frozen

    def synthesize(self, request: TtsRequest, progress_cb: ProgressCallback = None) -> TtsResult:
        if not request.text.strip():
            raise TtsError("Texto para sintetizar esta vazio.")

        self._notify(progress_cb, 0.0, "Iniciando sintese de voz com edge-tts...")

        dest = Path(request.dest_dir)
        project = request.project_name or "ALE"
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", request.text[:30])
        output_dir = dest / project / f"tts-{timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"tts_{safe_name}.mp3"
        subtitles_file = output_dir / f"tts_{safe_name}.srt"

        env = os.environ.copy()

        self._run_edge_tts(
            text=request.text,
            voice=request.voice,
            output_file=output_file,
            subtitles_file=subtitles_file,
            env=env,
            progress_cb=progress_cb,
        )

        return TtsResult(
            output_path=output_file,
            voice=request.voice,
            text_length=len(request.text),
        )

    def _run_edge_tts(
        self,
        text: str,
        voice: str,
        output_file: Path,
        subtitles_file: Path,
        env: dict[str, str],
        progress_cb: ProgressCallback,
    ):
        edge_cmd = self._resolve_edge_tts()
        cmd = [
            edge_cmd,
            "--text", text,
            "--voice", voice,
            "--write-media", str(output_file),
            "--write-subtitles", str(subtitles_file),
        ]

        self._notify(progress_cb, 10.0, "Conectando ao servico de voz...")

        process = subprocess.Popen(
            cmd,
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
                    elapsed = int(time.monotonic() - started_at)
                    mins, secs = divmod(elapsed, 60)
                    elapsed_str = f"{mins}min{secs:02d}s" if mins else f"{secs}s"
                    if progress_cb:
                        progress_cb(None, f"Sintetizando: {line} ({elapsed_str})")
            else:
                buffer += char

        return_code = process.wait()
        if return_code:
            raise TtsError(f"edge-tts falhou com codigo {return_code}")

        if not output_file.exists():
            raise TtsError("Arquivo de audio nao foi gerado pelo edge-tts.")

        self._notify(progress_cb, 100.0, f"Audio TTS gerado: {output_file.name}")

    def _resolve_edge_tts(self) -> str:
        from infrastructure.ai_runtime_manager import _venv_python

        venv_python = _venv_python()
        if venv_python.exists():
            venv_bin = venv_python.parent
            edge_cli = venv_bin / "edge-tts"
            if edge_cli.exists():
                return str(edge_cli)

        import importlib.util
        import shutil

        edge = shutil.which("edge-tts")
        if edge:
            return edge

        if not getattr(sys, "frozen", False):
            spec = importlib.util.find_spec("edge_tts")
            if spec and spec.origin:
                edge_dir = Path(spec.origin).parent
                maybe = edge_dir / "__main__.py"
                if maybe.exists():
                    return f"{sys.executable} -m edge_tts"

        raise TtsError(
            "edge-tts nao encontrado no PATH.\n"
            "Instale as dependencias de TTS pela interface do aplicativo."
        )

    @staticmethod
    def _notify(cb: ProgressCallback, percent: float, message: str):
        if cb:
            cb(percent, message)
