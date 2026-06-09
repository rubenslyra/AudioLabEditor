from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DependencyStatus:
    name: str
    available: bool
    path: Path | None = None
    message: str = ""
