import pytest

from src.application.output_organizer import OutputOrganizer
from src.domain.entities import MediaType, OutputCategory, OutputRequest
from src.infrastructure.path_config import PathConfig
from src.infrastructure.settings_store import SettingsStore


def make_path_config(tmp_path):
    return PathConfig(SettingsStore(tmp_path / "settings.json"))


class TestOutputOrganizer:
    def test_build_output_path_with_project(self, tmp_path):
        config = make_path_config(tmp_path)
        organizer = OutputOrganizer(config)

        request = OutputRequest(
            media_type=MediaType.AUDIO,
            category=OutputCategory.TRIM,
            project_name="MinhaMusica",
            extension="mp3",
        )

        path = organizer.build_output_path(request, dest_dir=str(tmp_path), timestamp="20260609_143022")

        assert path.parent.name == "MinhaMusica"
        assert path.name == "audio-trimmed-20260609_143022.mp3"
        assert path.exists() is False

    def test_build_output_path_fallback_project(self, tmp_path):
        config = make_path_config(tmp_path)
        organizer = OutputOrganizer(config)

        request = OutputRequest(
            media_type=MediaType.VIDEO,
            category=OutputCategory.CAPTURE,
            project_name="",
            extension="mp4",
        )

        path = organizer.build_output_path(request, dest_dir=str(tmp_path), timestamp="20260609_143022")

        assert path.parent.name == "ALE"
        assert path.name == "video-captured-20260609_143022.mp4"

    def test_build_output_path_creates_dir(self, tmp_path):
        config = make_path_config(tmp_path)
        organizer = OutputOrganizer(config)

        request = OutputRequest(
            media_type=MediaType.STEM,
            category=OutputCategory.STEM_VOCALS,
            project_name="Teste",
            extension="wav",
        )

        path = organizer.build_output_path(request, dest_dir=str(tmp_path), timestamp="20260609_150000")

        assert path.parent.is_dir()
        assert path.name == "stem-stem-vocals-20260609_150000.wav"

    def test_build_output_path_raises_without_dest(self, tmp_path):
        config = make_path_config(tmp_path)
        organizer = OutputOrganizer(config)

        request = OutputRequest(
            media_type=MediaType.AUDIO,
            category=OutputCategory.CAPTURE,
            project_name="Test",
            extension="mp3",
        )

        with pytest.raises(RuntimeError, match="Pasta de destino nao configurada"):
            organizer.build_output_path(request)

    def test_build_output_dir(self, tmp_path):
        config = make_path_config(tmp_path)
        organizer = OutputOrganizer(config)

        directory = organizer.build_output_dir(
            MediaType.AUDIO,
            OutputCategory.TRIM,
            dest_dir=str(tmp_path),
            project_name="ProjetoX",
        )

        assert directory.name == "ProjetoX"
        assert directory.is_dir()

    def test_build_stem_output_dir(self, tmp_path):
        config = make_path_config(tmp_path)
        organizer = OutputOrganizer(config)

        directory = organizer.build_stem_output_dir(
            "vocals",
            dest_dir=str(tmp_path),
            project_name="ProjetoX",
            timestamp="20260609_150000",
        )

        assert directory.name == "audio-stem-vocals-20260609_150000"
        assert directory.is_dir()
        assert directory.parent.name == "ProjetoX"

    def test_build_stem_output_dir_no_project(self, tmp_path):
        config = make_path_config(tmp_path)
        organizer = OutputOrganizer(config)

        directory = organizer.build_stem_output_dir(
            "full4",
            dest_dir=str(tmp_path),
            timestamp="20260609_150000",
        )

        assert directory.name == "audio-stem-full4-20260609_150000"
        assert directory.parent.name == "ALE"

    def test_build_stem_output_dir_raises_without_dest(self, tmp_path):
        config = make_path_config(tmp_path)
        organizer = OutputOrganizer(config)

        with pytest.raises(RuntimeError, match="Pasta de destino nao configurada"):
            organizer.build_stem_output_dir("vocals")

    def test_get_or_create_project_dir(self, tmp_path):
        config = make_path_config(tmp_path)
        organizer = OutputOrganizer(config)

        directory = organizer.get_or_create_project_dir(dest_dir=str(tmp_path), project_name="NovoProjeto")

        assert directory.name == "NovoProjeto"
        assert directory.is_dir()

    def test_get_or_create_project_dir_uses_fallback(self, tmp_path):
        config = make_path_config(tmp_path)
        organizer = OutputOrganizer(config)

        directory = organizer.get_or_create_project_dir(dest_dir=str(tmp_path))

        assert directory.name == "ALE"
        assert directory.is_dir()

    def test_get_or_create_project_dir_raises_without_dest(self, tmp_path):
        config = make_path_config(tmp_path)
        organizer = OutputOrganizer(config)

        with pytest.raises(RuntimeError, match="Pasta de destino nao configurada"):
            organizer.get_or_create_project_dir()


class TestOutputRequest:
    def test_prefix_suffix(self):
        request = OutputRequest(
            media_type=MediaType.AUDIO,
            category=OutputCategory.CAPTURE,
            project_name="Test",
            extension="mp3",
        )
        assert request.prefix == "audio"
        assert request.suffix == "captured"

    def test_stem_prefix(self):
        request = OutputRequest(
            media_type=MediaType.STEM,
            category=OutputCategory.STEM_VOCALS,
            project_name="Test",
            extension="wav",
        )
        assert request.prefix == "stem"
        assert request.suffix == "stem-vocals"
