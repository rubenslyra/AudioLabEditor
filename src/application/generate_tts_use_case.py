from domain.interfaces import ProgressCallback, TtsPort, TtsRequest, TtsResult
from infrastructure.path_config import PathConfig


class GenerateTtsUseCase:
    def __init__(self, tts: TtsPort, path_config: PathConfig | None = None):
        self._tts = tts
        self._path_config = path_config or PathConfig()

    def execute(self, request: TtsRequest, progress_cb: ProgressCallback = None) -> TtsResult:
        if not request.text.strip():
            raise RuntimeError("Texto para sintetizar esta vazio.")

        if not request.dest_dir:
            saved = self._path_config.get_dest_dir()
            if not saved:
                raise RuntimeError("Pasta de destino nao configurada.")
            request.dest_dir = saved

        return self._tts.synthesize(request, progress_cb=progress_cb)
