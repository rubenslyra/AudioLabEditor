from pathlib import Path

import yt_dlp

from domain.interfaces import DownloaderPort, MediaInfo, ProgressCallback


class YtDlpAdapter(DownloaderPort):
    def get_info(self, url: str) -> MediaInfo:
        opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "socket_timeout": 30,
            "retries": 5,
            "fragment_retries": 5,
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return MediaInfo(
                    title=info.get("title"),
                    duration=info.get("duration"),
                    uploader=info.get("uploader"),
                    thumbnail=info.get("thumbnail"),
                    webpage_url=info.get("webpage_url"),
                )
        except Exception as exc:
            raise RuntimeError(f"Nao foi possivel analisar a URL: {exc}") from exc

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
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        opts = {
            "outtmpl": str(output_dir / "%(title).180s.%(ext)s"),
            "noplaylist": True,
            "progress_hooks": [self._make_hook(progress_cb)],
            "quiet": True,
            "no_warnings": True,
            "socket_timeout": 30,
            "retries": 10,
            "fragment_retries": 10,
            "extractor_retries": 5,
            "file_access_retries": 5,
            "concurrent_fragment_downloads": 8,
            "http_chunk_size": 10 * 1024 * 1024,
        }
        if audio_only:
            opts["format"] = "bestaudio/best"
            opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": audio_format,
                    "preferredquality": str(audio_bitrate),
                }
            ]
        else:
            opts["format"] = video_format
            opts["merge_output_format"] = "mp4"

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                out = self._resolve_downloaded_path(info, ydl.prepare_filename(info), audio_only)
                if progress_cb:
                    progress_cb(100.0, f"Arquivo salvo em: {out}")
                return out
        except Exception as exc:
            raise RuntimeError(f"Nao foi possivel baixar a midia: {exc}") from exc

    def _make_hook(self, progress_cb: ProgressCallback):
        def hook(data):
            if not progress_cb:
                return
            status = data.get("status")
            if status == "downloading":
                total = data.get("total_bytes") or data.get("total_bytes_estimate") or 0
                downloaded = data.get("downloaded_bytes") or 0
                percent = (downloaded / total * 100.0) if total else 0.0
                speed = data.get("speed")
                eta = data.get("eta")
                speed_text = f"{speed / 1024 / 1024:.2f} MB/s" if speed else "?"
                eta_text = f"{eta}s" if eta is not None else "?"
                progress_cb(percent, f"Baixando... {percent:.1f}% | {speed_text} | ETA {eta_text}")
            elif status == "finished":
                progress_cb(100.0, "Download concluido. Pos-processando...")
        return hook

    @staticmethod
    def _resolve_downloaded_path(info: dict, prepared_filename: str, audio_only: bool) -> Path:
        requested = info.get("requested_downloads") or []
        for item in requested:
            filepath = item.get("filepath")
            if filepath:
                return Path(filepath)
        filepath = info.get("_filename")
        if filepath:
            return Path(filepath)
        prepared = Path(prepared_filename)
        if audio_only:
            candidates = [
                prepared.with_suffix(suffix)
                for suffix in [".mp3", ".m4a", ".wav", ".flac", ".ogg", ".aac", ".opus"]
            ]
            for candidate in candidates:
                if candidate.exists():
                    return candidate
        return prepared
