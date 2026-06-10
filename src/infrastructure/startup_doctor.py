from pathlib import Path

from domain.dependencies import DependencyStatus
from infrastructure.runtime_paths import IS_FROZEN, app_data_dir, find_executable

BASE_TOOLS = ("ffmpeg", "ffprobe")


def check_startup_dependencies() -> list[DependencyStatus]:
    statuses: list[DependencyStatus] = []

    for tool in BASE_TOOLS:
        path = find_executable(tool)
        statuses.append(
            DependencyStatus(
                name=tool,
                available=path is not None,
                path=path,
                message="" if path else "Binario nao encontrado ao lado do executavel.",
                required=True,
            )
        )

    data_dir = app_data_dir()
    statuses.append(
        DependencyStatus(
            name="local-data-dir",
            available=not IS_FROZEN or _can_create_dir(data_dir),
            path=data_dir,
            message="" if not IS_FROZEN or data_dir.exists() else "Nao foi possivel preparar a pasta local de dados.",
            required=True,
        )
    )
    return statuses


def startup_error_message() -> str:
    missing = [item for item in check_startup_dependencies() if item.required and not item.available]
    if not missing:
        return ""
    lines = [
        "AudioLabEditor nao pode iniciar porque faltam dependencias obrigatorias.",
        "",
        "Itens ausentes:",
    ]
    for item in missing:
        detail = f" - {item.name}"
        if item.message:
            detail += f": {item.message}"
        lines.append(detail)
    lines.extend(
        [
            "",
            "Instale as dependencias faltantes ou baixe a versao completa da aplicacao.",
        ]
    )
    return "\n".join(lines)


def _can_create_dir(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except OSError:
        return False
