from dataclasses import dataclass
from pathlib import Path

from domain.interfaces import DownloaderPort, FFmpegPort, MediaInfo, ProgressCallback

CAPTURE_MODE_VIDEO_ORIGINAL = "video_original"
CAPTURE_MODE_VIDEO_COMPRESSED = "video_compressed"
CAPTURE_MODE_AUDIO_ONLY = "audio_only"


@dataclass
class CaptureMediaRequest:
    url: str
    output_dir: Path
    project_name: str
    mode: str = CAPTURE_MODE_VIDEO_ORIGINAL
    quality_preset: str = "Alta"
    audio_format: str = "mp3"
    audio_bitrate: int = 192


@dataclass
class CaptureMediaResult:
    output_path: Path
    media_kind: str
    source_path: Path | None = None


class CaptureMediaUseCase:
    def __init__(self, downloader: DownloaderPort, ffmpeg: FFmpegPort | None = None):
        self._downloader = downloader
        self._ffmpeg = ffmpeg

    def get_info(self, url: str) -> MediaInfo:
        return self._downloader.get_info(url)

    def execute(self, request: CaptureMediaRequest, progress_cb: ProgressCallback = None) -> CaptureMediaResult:
        self._notify(progress_cb, 0.0, "Iniciando captura...")

        if request.mode == CAPTURE_MODE_AUDIO_ONLY:
            output = self._downloader.download(
                url=request.url,
                output_dir=request.output_dir,
                audio_only=True,
                audio_format=request.audio_format,
                audio_bitrate=request.audio_bitrate,
                progress_cb=progress_cb,
            )
            return CaptureMediaResult(output_path=output, media_kind="audio")

        downloaded = self._downloader.download(
            url=request.url,
            output_dir=request.output_dir,
            audio_only=False,
            progress_cb=progress_cb,
        )

        if request.mode == CAPTURE_MODE_VIDEO_ORIGINAL:
            self._notify(progress_cb, 100.0, "Video preservado com qualidade original do provedor.")
            return CaptureMediaResult(output_path=downloaded, media_kind="video")

        if request.mode != CAPTURE_MODE_VIDEO_COMPRESSED:
            raise ValueError(f"Modo de captura nao suportado: {request.mode}")

        if self._ffmpeg is None:
            raise RuntimeError("FFmpegPort necessario para compressao de video")

        compressed = self._ffmpeg.compress_video(
            input_path=downloaded,
            output_dir=request.output_dir,
            quality_preset=request.quality_preset,
            progress_cb=progress_cb,
        )
        return CaptureMediaResult(output_path=compressed, media_kind="video", source_path=downloaded)

    @staticmethod
    def _notify(cb: ProgressCallback, percent: float, message: str):
        if cb:
            cb(percent, message)
