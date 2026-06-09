from pathlib import Path

from src.domain.interfaces import DemucsPort, StemRequest, StemResult, ProgressCallback
from src.infrastructure.path_config import PathConfig


class SeparateAudioUseCase:
    def __init__(self, demucs: DemucsPort, path_config: PathConfig | None = None):
        self._demucs = demucs
        self._path_config = path_config or PathConfig()

    def execute(self, request: StemRequest, progress_cb: ProgressCallback = None) -> StemResult:
        if not request.source_path.exists():
            raise RuntimeError(f"Arquivo nao encontrado: {request.source_path}")

        if not request.dest_dir:
            saved = self._path_config.get_dest_dir()
            if not saved:
                raise RuntimeError("Pasta de destino nao configurada.")
            request.dest_dir = saved

        return self._demucs.separate(request, progress_cb=progress_cb)
