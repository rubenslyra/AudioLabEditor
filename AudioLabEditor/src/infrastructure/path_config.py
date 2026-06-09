from infrastructure.settings_store import SettingsStore


class PathConfig:
    KEY_SOURCE_DIR = "source_dir"
    KEY_DEST_DIR = "dest_dir"

    def __init__(self, store: SettingsStore | None = None):
        self._store = store or SettingsStore()

    def get_source_dir(self) -> str:
        return self._store.get(self.KEY_SOURCE_DIR, "")

    def set_source_dir(self, path: str):
        self._store.set(self.KEY_SOURCE_DIR, path)

    def get_dest_dir(self) -> str:
        return self._store.get(self.KEY_DEST_DIR, "")

    def set_dest_dir(self, path: str):
        self._store.set(self.KEY_DEST_DIR, path)

    def is_configured(self) -> bool:
        return bool(self.get_source_dir()) and bool(self.get_dest_dir())
