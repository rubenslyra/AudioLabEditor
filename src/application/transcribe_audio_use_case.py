from domain.interfaces import ProgressCallback, TranscriptionPort, TranscriptionRequest, TranscriptionResult
from infrastructure.path_config import PathConfig


class TranscribeAudioUseCase:
    def __init__(self, transcriber: TranscriptionPort, path_config: PathConfig | None = None):
        self._transcriber = transcriber
        self._path_config = path_config or PathConfig()

    def execute(self, request: TranscriptionRequest, progress_cb: ProgressCallback = None) -> TranscriptionResult:
        if not request.source_path.exists():
            raise RuntimeError(f"Arquivo nao encontrado: {request.source_path}")

        if not request.dest_dir:
            saved = self._path_config.get_dest_dir()
            if not saved:
                raise RuntimeError("Pasta de destino nao configurada.")
            request.dest_dir = saved

        return self._transcriber.transcribe(request, progress_cb=progress_cb)
