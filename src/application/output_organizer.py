from datetime import datetime
from pathlib import Path

from src.domain.entities import MediaType, OutputCategory, OutputRequest
from src.infrastructure.path_config import PathConfig


PROJECT_NAME_FALLBACK = "ALE"


class OutputOrganizer:
    def __init__(self, path_config: PathConfig | None = None):
        self._path_config = path_config or PathConfig()

    def build_output_path(
        self,
        request: OutputRequest,
        *,
        dest_dir: str | None = None,
        project_name: str | None = None,
        timestamp: str | None = None,
    ) -> Path:
        dest = dest_dir or self._path_config.get_dest_dir()
        if not dest:
            dest = str(PathConfig.default_dest_dir())

        project = (project_name or request.project_name or "").strip() or PROJECT_NAME_FALLBACK
        ts = timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")

        base = Path(dest) / project
        base.mkdir(parents=True, exist_ok=True)

        filename = f"{request.prefix}-{request.suffix}-{ts}.{request.extension.lstrip('.')}"
        return base / filename

    def build_output_dir(
        self,
        media_type: MediaType,
        category: OutputCategory,
        *,
        dest_dir: str | None = None,
        project_name: str | None = None,
        timestamp: str | None = None,
    ) -> Path:
        request = OutputRequest(
            media_type=media_type,
            category=category,
            project_name=project_name or PROJECT_NAME_FALLBACK,
            extension="",
        )
        path = self.build_output_path(
            request,
            dest_dir=dest_dir,
            project_name=project_name,
            timestamp=timestamp,
        )
        return path.parent

    def get_or_create_project_dir(
        self,
        dest_dir: str | None = None,
        project_name: str | None = None,
    ) -> Path:
        dest = dest_dir or self._path_config.get_dest_dir()
        if not dest:
            dest = str(PathConfig.default_dest_dir())
        project = (project_name or "").strip() or PROJECT_NAME_FALLBACK
        path = Path(dest) / project
        path.mkdir(parents=True, exist_ok=True)
        return path
