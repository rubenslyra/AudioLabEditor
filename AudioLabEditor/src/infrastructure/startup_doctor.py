import importlib.util
from pathlib import Path

from domain.dependencies import DependencyStatus
from infrastructure.runtime_paths import IS_FROZEN, app_data_dir, find_executable

BASE_TOOLS = ("ffmpeg", "ffprobe")
AI_MODULES = ("yt_dlp", "demucs")
FULL_MODULES = ("faster_whisper", "paddleocr")


def module_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def check_startup_dependencies(profile: str = "ai") -> list[DependencyStatus]:
    profile = (profile or "ai").lower()
    statuses: list[DependencyStatus] = []

    for tool in BASE_TOOLS:
        path = find_executable(tool)
        statuses.append(
            DependencyStatus(
                name=tool,
                available=path is not None,
                path=path,
                message="" if path else "Binario nao encontrado ao lado do executavel.",
            )
        )

    modules = list(AI_MODULES)
    if profile == "full":
        modules.extend(FULL_MODULES)
    for module_name in modules:
        available = module_available(module_name)
        statuses.append(
            DependencyStatus(
                name=module_name.replace("_", "-"),
                available=available,
                message="" if available else f"Pacote Python {module_name} nao foi embarcado.",
            )
        )

    data_dir = app_data_dir()
    statuses.append(
        DependencyStatus(
            name="local-data-dir",
            available=not IS_FROZEN or _can_create_dir(data_dir),
            path=data_dir,
            message="" if not IS_FROZEN or data_dir.exists() else "Nao foi possivel preparar a pasta local de dados.",
        )
    )
    return statuses


def startup_error_message(profile: str = "ai") -> str:
    missing = [item for item in check_startup_dependencies(profile) if not item.available]
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
            "Use um pacote completo com _internal/bin ou reinstale a aplicacao.",
        ]
    )
    return "\n".join(lines)


def _can_create_dir(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except OSError:
        return False
