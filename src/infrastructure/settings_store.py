import json
import threading
from pathlib import Path


class SettingsStore:
    def __init__(self, file_path: Path | None = None):
        if file_path is None:
            file_path = Path.home() / ".config" / "audiolab-editor" / "settings.json"
        self.file_path = file_path
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        if not self.file_path.exists():
            self._atomic_write({})

    def read(self) -> dict:
        try:
            data = json.loads(self.file_path.read_text(encoding="utf-8"))
        except Exception:
            return {}
        return data if isinstance(data, dict) else {}

    def get(self, key: str, default=None):
        return self.read().get(key, default)

    def set(self, key: str, value):
        with self._lock:
            data = self.read()
            data[key] = value
            self._atomic_write(data)

    def _atomic_write(self, data: dict):
        temp_path = self.file_path.with_suffix(self.file_path.suffix + ".tmp")
        temp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        temp_path.replace(self.file_path)
