from pathlib import Path

from domain.interfaces import FFmpegPort, ProgressCallback

QUALITY_PRESETS = {
    "Alta": {"crf": 18, "preset": "slow", "audio_bitrate": 192},
    "Balanceada": {"crf": 22, "preset": "medium", "audio_bitrate": 160},
    "Compacta": {"crf": 26, "preset": "medium", "audio_bitrate": 128},
}


class FFmpegAdapter(FFmpegPort):
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self._ffmpeg_path = ffmpeg_path

    def compress_video(
        self,
        input_path: Path,
        output_dir: Path,
        *,
        quality_preset: str = "Alta",
        progress_cb: ProgressCallback = None,
    ) -> Path:
        import os
        import subprocess

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self._unique_path(output_dir / f"{input_path.stem}_compactado.mp4")

        preset = QUALITY_PRESETS.get(quality_preset, QUALITY_PRESETS["Alta"])
        threads = str(max(1, os.cpu_count() or 1))
        command = [
            self._ffmpeg_path,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-threads",
            threads,
            "-i",
            str(input_path),
            "-map",
            "0:v:0",
            "-map",
            "0:a?",
            "-sn",
            "-c:v",
            "libx264",
            "-preset",
            preset["preset"],
            "-crf",
            str(preset["crf"]),
            "-c:a",
            "aac",
            "-b:a",
            f"{preset['audio_bitrate']}k",
            "-movflags",
            "+faststart",
            "-progress",
            "pipe:1",
            "-nostats",
            str(output_path),
        ]

        if progress_cb:
            progress_cb(0.0, f"Comprimindo video com preset {quality_preset}...")

        try:
            proc = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            for line in proc.stdout or []:
                if line.startswith("out_time_us="):
                    pass
                elif line.startswith("progress=end"):
                    if progress_cb:
                        progress_cb(100.0, "Compressao concluida")
            proc.wait()
            if proc.returncode != 0:
                raise RuntimeError(f"FFmpeg falhou com codigo {proc.returncode}")
        except Exception as exc:
            raise RuntimeError(f"Erro na compressao de video: {exc}") from exc

        return output_path

    @staticmethod
    def _unique_path(path: Path) -> Path:
        if not path.exists():
            return path
        for index in range(2, 1000):
            candidate = path.with_name(f"{path.stem}_{index}{path.suffix}")
            if not candidate.exists():
                return candidate
        raise RuntimeError(f"Nao foi possivel gerar nome unico para {path}")
