import time
from pathlib import Path

from domain.interfaces import (
    BatchStemResult,
    DemucsPort,
    ProgressCallback,
    StemRequest,
    StemResult,
)
from infrastructure.path_config import PathConfig


class BatchSeparateAudioUseCase:
    def __init__(self, demucs: DemucsPort, path_config: PathConfig | None = None):
        self._demucs = demucs
        self._path_config = path_config or PathConfig()

    def execute(
        self,
        source_paths: list[Path],
        mode: str = "vocals",
        output_format: str = "wav",
        dest_dir: str = "",
        project_name: str = "",
        progress_cb: ProgressCallback = None,
    ) -> BatchStemResult:
        if not source_paths:
            raise RuntimeError("Nenhum arquivo selecionado para processamento.")

        if not dest_dir:
            saved = self._path_config.get_dest_dir()
            if not saved:
                raise RuntimeError("Pasta de destino nao configurada.")
            dest_dir = saved

        dest = Path(dest_dir)
        project = project_name or "ALE"
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        batch_output_dir = dest / project / f"batch-stems-{timestamp}"
        batch_output_dir.mkdir(parents=True, exist_ok=True)

        results: list[StemResult] = []
        failed: list[tuple[str, str]] = []
        total = len(source_paths)

        for i, source_path in enumerate(source_paths, 1):
            if progress_cb:
                progress_cb(0.0, f"Arquivo {i}/{total}: {source_path.name}")

            if not source_path.exists():
                failed.append((source_path.name, "Arquivo nao encontrado"))
                if progress_cb:
                    progress_cb(100.0, f"[{i}/{total}] Falha: {source_path.name} (arquivo nao encontrado)")
                continue

            request = StemRequest(
                source_path=source_path,
                mode=mode,
                output_format=output_format,
                dest_dir=str(batch_output_dir),
                project_name="",
            )

            def _wrap_progress(file_index: int, file_total: int, file_name: str) -> ProgressCallback:
                def _cb(percent: float | None, message: str):
                    overall = ((file_index - 1) / file_total) * 100.0
                    file_pct = (percent or 0.0) / file_total
                    if progress_cb:
                        progress_cb(overall + file_pct, f"[{file_index}/{file_total}] {file_name}: {message or ''}")
                return _cb

            try:
                result = self._demucs.separate(
                    request,
                    progress_cb=_wrap_progress(i, total, source_path.name),
                )
                results.append(result)
                if progress_cb:
                    progress_cb(float(i) / total * 100.0, f"[{i}/{total}] Concluido: {source_path.name}")
            except Exception as exc:
                failed.append((source_path.name, str(exc)))
                if progress_cb:
                    progress_cb(float(i) / total * 100.0, f"[{i}/{total}] Falha: {source_path.name} - {exc}")

        if progress_cb:
            msg = f"Lote concluido: {len(results)} ok, {len(failed)} falhas"
            progress_cb(100.0, msg)

        return BatchStemResult(
            output_dir=batch_output_dir,
            results=results,
            failed=failed,
            total=total,
            succeeded=len(results),
        )
