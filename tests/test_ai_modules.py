from pathlib import Path
from unittest.mock import MagicMock

import pytest

from domain.entities import MediaType, OutputCategory
from domain.interfaces import (
    BatchStemResult,
    StemResult,
    TranscriptionRequest,
    TranscriptionResult,
    TtsRequest,
    TtsResult,
)
from infrastructure.edge_tts_adapter import TTS_VOICES, EdgeTtsSubprocessAdapter
from infrastructure.whisper_adapter import WHISPER_LANGUAGES, WHISPER_MODELS, WhisperSubprocessAdapter

LANG_KEYS = list(WHISPER_LANGUAGES.values())
MODEL_KEYS = WHISPER_MODELS


class TestDomainEntities:
    def test_media_type_has_transcription(self):
        assert MediaType.TRANSCRIPTION.value == "transcription"

    def test_media_type_has_tts(self):
        assert MediaType.TTS.value == "tts"

    def test_output_category_has_transcription(self):
        assert OutputCategory.TRANSCRIPTION.value == "transcribed"

    def test_output_category_has_tts(self):
        assert OutputCategory.TTS.value == "tts"


class TestDomainInterfaces:
    def test_transcription_request_defaults(self):
        req = TranscriptionRequest(source_path=Path("/tmp/test.wav"))
        assert req.language == "pt"
        assert req.model_size == "base"
        assert req.dest_dir == ""
        assert req.project_name == ""

    def test_transcription_request_custom(self):
        req = TranscriptionRequest(
            source_path=Path("/tmp/test.wav"),
            language="en",
            model_size="large-v3",
            dest_dir="/output",
            project_name="MyProject",
        )
        assert req.language == "en"
        assert req.model_size == "large-v3"

    def test_transcription_result(self):
        result = TranscriptionResult(
            output_dir=Path("/out"),
            source_name="test",
            language="pt",
            segments_count=42,
        )
        assert result.source_name == "test"
        assert result.segments_count == 42

    def test_tts_request_defaults(self):
        req = TtsRequest(text="Hello world")
        assert req.voice == "pt-BR-FranciscaNeural"
        assert req.dest_dir == ""
        assert req.project_name == ""

    def test_tts_request_custom(self):
        req = TtsRequest(
            text="Hello",
            voice="en-US-JennyNeural",
            dest_dir="/out",
            project_name="Proj",
        )
        assert req.voice == "en-US-JennyNeural"

    def test_tts_result(self):
        result = TtsResult(
            output_path=Path("/out/tts.mp3"),
            voice="pt-BR-FranciscaNeural",
            text_length=42,
        )
        assert result.output_path.name == "tts.mp3"
        assert result.text_length == 42


class TestWhisperConstants:
    def test_whisper_languages_has_portuguese(self):
        assert WHISPER_LANGUAGES["Português (BR)"] == "pt"

    def test_whisper_languages_has_english(self):
        assert WHISPER_LANGUAGES["Inglês"] == "en"

    def test_whisper_languages_count(self):
        assert len(WHISPER_LANGUAGES) >= 10

    def test_whisper_models_has_base(self):
        assert "base" in WHISPER_MODELS

    def test_whisper_models_has_large(self):
        assert "large-v3" in WHISPER_MODELS

    def test_whisper_models_first_is_tiny(self):
        assert WHISPER_MODELS[0] == "tiny"


class TestTtsConstants:
    def test_tts_voices_has_brazilian_portuguese(self):
        assert "pt-BR-FranciscaNeural" in TTS_VOICES
        assert "pt-BR-AntonioNeural" in TTS_VOICES

    def test_tts_voices_has_english(self):
        assert "en-US-JennyNeural" in TTS_VOICES
        assert "en-GB-SoniaNeural" in TTS_VOICES

    def test_tts_voices_count(self):
        assert len(TTS_VOICES) >= 18


class TestWhisperAdapterInit:
    def test_default_construction(self):
        adapter = WhisperSubprocessAdapter()
        assert adapter._frozen is False

    def test_frozen_construction(self):
        adapter = WhisperSubprocessAdapter(frozen=True)
        assert adapter._frozen is True

    def test_transcribe_raises_on_missing_file(self):
        adapter = WhisperSubprocessAdapter()
        req = TranscriptionRequest(source_path=Path("/nonexistent/file.wav"))
        with pytest.raises(RuntimeError, match="Arquivo nao encontrado"):
            adapter.transcribe(req)


class TestEdgeTtsAdapterInit:
    def test_default_construction(self):
        adapter = EdgeTtsSubprocessAdapter()
        assert adapter._frozen is False

    def test_frozen_construction(self):
        adapter = EdgeTtsSubprocessAdapter(frozen=True)
        assert adapter._frozen is True

    def test_synthesize_raises_on_empty_text(self):
        adapter = EdgeTtsSubprocessAdapter()
        req = TtsRequest(text="")
        with pytest.raises(RuntimeError, match="Texto para sintetizar esta vazio"):
            adapter.synthesize(req)

    def test_synthesize_raises_on_whitespace_only(self):
        adapter = EdgeTtsSubprocessAdapter()
        req = TtsRequest(text="   ")
        with pytest.raises(RuntimeError, match="Texto para sintetizar esta vazio"):
            adapter.synthesize(req)


class TestTranscribeUseCase:
    def test_raises_on_missing_file(self):
        from application.transcribe_audio_use_case import TranscribeAudioUseCase

        mock_transcriber = MagicMock()
        use_case = TranscribeAudioUseCase(transcriber=mock_transcriber)

        request = TranscriptionRequest(source_path=Path("/nonexistent/file.wav"), dest_dir="/tmp")
        with pytest.raises(RuntimeError, match="Arquivo nao encontrado"):
            use_case.execute(request)
        mock_transcriber.transcribe.assert_not_called()

    def test_raises_without_dest_dir(self, tmp_path):
        from application.transcribe_audio_use_case import TranscribeAudioUseCase

        mock_transcriber = MagicMock()
        use_case = TranscribeAudioUseCase(transcriber=mock_transcriber)

        source = tmp_path / "test.wav"
        source.write_text("dummy")
        request = TranscriptionRequest(source_path=source)
        with pytest.raises(RuntimeError, match="Pasta de destino nao configurada"):
            use_case.execute(request)

    def test_executes_successfully(self, tmp_path):
        from application.transcribe_audio_use_case import TranscribeAudioUseCase

        expected = TranscriptionResult(
            output_dir=tmp_path / "out",
            source_name="test",
            language="pt",
            segments_count=10,
        )

        mock_transcriber = MagicMock()
        mock_transcriber.transcribe.return_value = expected

        use_case = TranscribeAudioUseCase(transcriber=mock_transcriber)

        source = tmp_path / "audio.wav"
        source.write_text("dummy")
        request = TranscriptionRequest(source_path=source, dest_dir=str(tmp_path))

        result = use_case.execute(request)
        assert result.segments_count == 10
        mock_transcriber.transcribe.assert_called_once()


class TestTtsUseCase:
    def test_raises_on_empty_text(self):
        from application.generate_tts_use_case import GenerateTtsUseCase

        mock_tts = MagicMock()
        use_case = GenerateTtsUseCase(tts=mock_tts)

        request = TtsRequest(text="", dest_dir="/tmp")
        with pytest.raises(RuntimeError, match="Texto para sintetizar esta vazio"):
            use_case.execute(request)
        mock_tts.synthesize.assert_not_called()

    def test_raises_without_dest_dir(self, tmp_path):
        from application.generate_tts_use_case import GenerateTtsUseCase

        mock_tts = MagicMock()
        use_case = GenerateTtsUseCase(tts=mock_tts)

        request = TtsRequest(text="Hello")
        with pytest.raises(RuntimeError, match="Pasta de destino nao configurada"):
            use_case.execute(request)

    def test_executes_successfully(self, tmp_path):
        from application.generate_tts_use_case import GenerateTtsUseCase

        expected = TtsResult(
            output_path=tmp_path / "out" / "tts.mp3",
            voice="pt-BR-FranciscaNeural",
            text_length=5,
        )

        mock_tts = MagicMock()
        mock_tts.synthesize.return_value = expected

        use_case = GenerateTtsUseCase(tts=mock_tts)

        request = TtsRequest(text="Hello", dest_dir=str(tmp_path))
        result = use_case.execute(request)
        assert result.text_length == 5
        mock_tts.synthesize.assert_called_once()


class TestBatchStemDomain:
    def test_batch_stem_result_dataclass(self):
        result = BatchStemResult(
            output_dir=Path("/out"),
            results=[],
            failed=[],
            total=3,
            succeeded=0,
        )
        assert result.total == 3
        assert result.succeeded == 0

    def test_batch_stem_result_with_results(self):
        sr = StemResult(
            output_dir=Path("/out/stem1"),
            mode="vocals",
            output_format="wav",
            source_name="song1",
        )
        result = BatchStemResult(
            output_dir=Path("/out"),
            results=[sr],
            failed=[("song2", "erro")],
            total=2,
            succeeded=1,
        )
        assert len(result.results) == 1
        assert len(result.failed) == 1
        assert result.succeeded == 1


class TestBatchSeparateUseCase:
    def test_raises_on_empty_list(self):
        from application.batch_separate_audio_use_case import BatchSeparateAudioUseCase

        mock_demucs = MagicMock()
        use_case = BatchSeparateAudioUseCase(demucs=mock_demucs)

        with pytest.raises(RuntimeError, match="Nenhum arquivo selecionado"):
            use_case.execute(source_paths=[])

    def test_raises_without_dest_dir(self, tmp_path):
        from application.batch_separate_audio_use_case import BatchSeparateAudioUseCase

        mock_demucs = MagicMock()
        use_case = BatchSeparateAudioUseCase(demucs=mock_demucs)

        source = tmp_path / "test.wav"
        source.write_text("dummy")

        with pytest.raises(RuntimeError, match="Pasta de destino nao configurada"):
            use_case.execute(source_paths=[source])

    def test_skips_missing_files(self, tmp_path):
        from application.batch_separate_audio_use_case import BatchSeparateAudioUseCase

        mock_demucs = MagicMock()
        mock_demucs.separate.return_value = StemResult(
            output_dir=tmp_path / "out",
            mode="vocals",
            output_format="wav",
            source_name="exists",
        )
        use_case = BatchSeparateAudioUseCase(demucs=mock_demucs)

        existing = tmp_path / "exists.wav"
        existing.write_text("dummy")
        missing = tmp_path / "missing.wav"

        result = use_case.execute(
            source_paths=[existing, missing],
            dest_dir=str(tmp_path),
        )

        assert result.succeeded == 1
        assert len(result.failed) == 1
        assert result.failed[0][0] == "missing.wav"
        mock_demucs.separate.assert_called_once()

    def test_processes_all_files(self, tmp_path):
        from application.batch_separate_audio_use_case import BatchSeparateAudioUseCase

        mock_demucs = MagicMock()

        def fake_separate(request, progress_cb=None):
            return StemResult(
                output_dir=tmp_path / "out",
                mode=request.mode,
                output_format=request.output_format,
                source_name=request.source_path.stem,
            )

        mock_demucs.separate.side_effect = fake_separate
        use_case = BatchSeparateAudioUseCase(demucs=mock_demucs)

        files = []
        for name in ["a.wav", "b.wav", "c.wav"]:
            p = tmp_path / name
            p.write_text("dummy")
            files.append(p)

        result = use_case.execute(
            source_paths=files,
            mode="full4",
            output_format="mp3",
            dest_dir=str(tmp_path),
            project_name="LoteTeste",
        )

        assert result.succeeded == 3
        assert len(result.failed) == 0
        assert result.total == 3
        assert mock_demucs.separate.call_count == 3
