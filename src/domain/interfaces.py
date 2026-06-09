from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional


ProgressCallback = Optional[Callable[[float, str], None]]


@dataclass(frozen=True)
class MediaInfo:
    title: str | None = None
    duration: int | None = None
    uploader: str | None = None
    thumbnail: str | None = None
    webpage_url: str | None = None


class DownloaderPort:
    def get_info(self, url: str) -> MediaInfo:
        ...

    def download(
        self,
        url: str,
        output_dir: Path,
        *,
        audio_only: bool = False,
        audio_format: str = "mp3",
        audio_bitrate: int = 192,
        video_format: str = "bv*+ba/b",
        progress_cb: ProgressCallback = None,
    ) -> Path:
        ...


class FFmpegPort:
    def compress_video(
        self,
        input_path: Path,
        output_dir: Path,
        *,
        quality_preset: str = "Alta",
        progress_cb: ProgressCallback = None,
    ) -> Path:
        ...
