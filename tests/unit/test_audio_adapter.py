# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for AudioAdapter content adapter."""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from voogle.adapters.audio import (
    AUDIO_EXTENSIONS,
    AudioAdapter,
    TranscriptionConfig,
)
from voogle.adapters.base import ChunkConfig, ContentSource, RawChunk
from voogle.core.fragment import ContentType
from voogle.core.location import TimestampLocation

pytestmark = pytest.mark.unit


class TestAudioAdapterInit:
    """Tests for AudioAdapter initialization."""

    @pytest.mark.description("AudioAdapter initializes with default config")
    def test_init_default_config(self) -> None:
        adapter = AudioAdapter()
        assert adapter._config.model_name == "small"
        assert adapter._config.device == "cpu"
        assert adapter._config.compute_type == "int8"
        assert adapter._config.word_timestamps is False

    @pytest.mark.description("AudioAdapter initializes with custom config")
    def test_init_custom_config(self) -> None:
        config = TranscriptionConfig(
            model_name="large",
            device="cuda",
            compute_type="float16",
            word_timestamps=True,
            language="en",
        )
        adapter = AudioAdapter(config=config)
        assert adapter._config.model_name == "large"
        assert adapter._config.device == "cuda"
        assert adapter._config.word_timestamps is True


class TestAudioAdapterSupportedTypes:
    """Tests for AudioAdapter.supported_types property."""

    @pytest.mark.description("supported_types returns AUDIO only")
    def test_supported_types(self) -> None:
        adapter = AudioAdapter()
        assert adapter.supported_types == frozenset({ContentType.AUDIO})


class TestAudioAdapterSupports:
    """Tests for AudioAdapter.supports method."""

    @pytest.mark.description("supports returns True for MP3 files")
    def test_supports_mp3(self) -> None:
        adapter = AudioAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.AUDIO,
            path=Path("/data/audio.mp3"),
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns True for WAV files")
    def test_supports_wav(self) -> None:
        adapter = AudioAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.AUDIO,
            path=Path("/data/audio.wav"),
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns True for FLAC files")
    def test_supports_flac(self) -> None:
        adapter = AudioAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.AUDIO,
            path=Path("/data/audio.flac"),
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns True for M4A files")
    def test_supports_m4a(self) -> None:
        adapter = AudioAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.AUDIO,
            path=Path("/data/audio.m4a"),
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns False for non-audio content type")
    def test_rejects_non_audio_type(self) -> None:
        adapter = AudioAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.VIDEO,
            path=Path("/data/video.mp4"),
        )
        assert adapter.supports(source) is False

    @pytest.mark.description("supports returns False for unsupported extension")
    def test_rejects_unsupported_extension(self) -> None:
        adapter = AudioAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.AUDIO,
            path=Path("/data/audio.ogg"),
        )
        assert adapter.supports(source) is False

    @pytest.mark.description("supports works with URL sources")
    def test_supports_url_source(self) -> None:
        adapter = AudioAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.AUDIO,
            url="https://example.com/podcast.mp3",
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns True for audio MIME type")
    def test_supports_mime_type(self) -> None:
        adapter = AudioAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.AUDIO,
            url="https://example.com/stream",
            metadata={"mime_type": "audio/mpeg"},
        )
        assert adapter.supports(source) is True


class TestAudioAdapterExtract:
    """Tests for AudioAdapter.extract method."""

    @pytest.mark.description("extract raises ValueError for unsupported source")
    @pytest.mark.asyncio
    async def test_extract_unsupported_raises(self) -> None:
        adapter = AudioAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.VIDEO,
            path=Path("/data/video.mp4"),
        )
        with pytest.raises(ValueError, match="Unsupported source"):
            async for _ in adapter.extract(source):
                pass

    @pytest.mark.description("extract raises ValueError for URL-only source")
    @pytest.mark.asyncio
    async def test_extract_url_only_raises(self) -> None:
        adapter = AudioAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.AUDIO,
            url="https://example.com/audio.mp3",
        )
        with pytest.raises(ValueError, match="requires a local file path"):
            async for _ in adapter.extract(source):
                pass

    @pytest.mark.description("extract raises ValueError for missing file")
    @pytest.mark.asyncio
    async def test_extract_missing_file_raises(self) -> None:
        adapter = AudioAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.AUDIO,
            path=Path("/nonexistent/audio.mp3"),
        )
        with pytest.raises(ValueError, match="Audio file not found"):
            async for _ in adapter.extract(source):
                pass

    @pytest.mark.description("extract yields RawChunks with segment timestamps")
    @pytest.mark.asyncio
    async def test_extract_segment_level(self, tmp_path: Path) -> None:
        # Create a mock audio file
        audio_file = tmp_path / "test.mp3"
        audio_file.touch()

        # Create mock segment
        mock_segment = MagicMock()
        mock_segment.start = 0.0
        mock_segment.end = 5.0
        mock_segment.text = " Hello world "
        mock_segment.avg_logprob = -0.5
        mock_segment.id = 1

        # Create mock transcription info
        mock_info = MagicMock()
        mock_info.language = "en"
        mock_info.language_probability = 0.99

        # Create mock model
        mock_model = MagicMock()
        mock_model.transcribe.return_value = ([mock_segment], mock_info)

        adapter = AudioAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.AUDIO,
            path=audio_file,
        )

        with patch("voogle.adapters.audio._get_model", return_value=mock_model):
            chunks = []
            async for chunk in adapter.extract(source):
                chunks.append(chunk)

        assert len(chunks) == 1
        assert chunks[0].text == "Hello world"
        assert isinstance(chunks[0].location, TimestampLocation)
        assert chunks[0].location.start_time == 0.0
        assert chunks[0].location.end_time == 5.0
        assert chunks[0].metadata["language"] == "en"
        assert chunks[0].metadata["avg_logprob"] == -0.5  # Stored in metadata, not confidence

    @pytest.mark.description("extract yields word-level chunks when enabled")
    @pytest.mark.asyncio
    async def test_extract_word_level(self, tmp_path: Path) -> None:
        # Create a mock audio file
        audio_file = tmp_path / "test.mp3"
        audio_file.touch()

        # Create mock words
        mock_word1 = MagicMock()
        mock_word1.word = "Hello"
        mock_word1.start = 0.0
        mock_word1.end = 0.5
        mock_word1.probability = 0.95

        mock_word2 = MagicMock()
        mock_word2.word = "world"
        mock_word2.start = 0.6
        mock_word2.end = 1.0
        mock_word2.probability = 0.92

        # Create mock segment with words
        mock_segment = MagicMock()
        mock_segment.words = [mock_word1, mock_word2]
        mock_segment.id = 1

        # Create mock transcription info
        mock_info = MagicMock()
        mock_info.language = "en"

        # Create mock model
        mock_model = MagicMock()
        mock_model.transcribe.return_value = ([mock_segment], mock_info)

        config = TranscriptionConfig(word_timestamps=True)
        adapter = AudioAdapter(config=config)
        source = ContentSource(
            source_id="test",
            source_type=ContentType.AUDIO,
            path=audio_file,
        )

        with patch("voogle.adapters.audio._get_model", return_value=mock_model):
            chunks = []
            async for chunk in adapter.extract(source):
                chunks.append(chunk)

        assert len(chunks) == 2
        assert chunks[0].text == "Hello"
        assert chunks[0].location.start_time == 0.0
        assert chunks[0].location.end_time == 0.5
        assert chunks[1].text == "world"
        assert chunks[1].location.start_time == 0.6


class TestAudioAdapterChunk:
    """Tests for AudioAdapter.chunk method."""

    @pytest.mark.description("chunk returns empty list for empty input")
    def test_chunk_empty_input(self) -> None:
        adapter = AudioAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.AUDIO,
            path=Path("/data/audio.mp3"),
        )
        result = adapter.chunk([], source)
        assert result == []

    @pytest.mark.description("chunk combines words into target-sized chunks")
    def test_chunk_combines_words(self) -> None:
        adapter = AudioAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.AUDIO,
            path=Path("/data/audio.mp3"),
        )

        # Create raw chunks that together have more than target words
        words = "one two three four five six seven eight nine ten " * 5  # 50 words
        raw_chunks = [
            RawChunk(
                text=words,
                location=TimestampLocation(start_time=0.0, end_time=30.0),
            )
        ]

        config = ChunkConfig(target_words=40, overlap_words=5)
        result = adapter.chunk(raw_chunks, source, config)

        assert len(result) >= 1
        assert all(chunk.source_id == "test" for chunk in result)
        assert all(chunk.source_type == ContentType.AUDIO for chunk in result)

    @pytest.mark.description("chunk preserves timestamps from raw chunks")
    def test_chunk_preserves_timestamps(self) -> None:
        adapter = AudioAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.AUDIO,
            path=Path("/data/audio.mp3"),
        )

        raw_chunks = [
            RawChunk(
                text="word " * 45,
                location=TimestampLocation(start_time=0.0, end_time=30.0),
            )
        ]

        config = ChunkConfig(target_words=40, overlap_words=5)
        result = adapter.chunk(raw_chunks, source, config)

        assert len(result) >= 1
        assert result[0].location is not None
        assert isinstance(result[0].location, TimestampLocation)
        assert result[0].location.start_time == 0.0

    @pytest.mark.description("chunk increments sequence_index correctly")
    def test_chunk_sequence_index(self) -> None:
        adapter = AudioAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.AUDIO,
            path=Path("/data/audio.mp3"),
        )

        # Create enough words for multiple chunks
        raw_chunks = [
            RawChunk(
                text="word " * 100,
                location=TimestampLocation(start_time=0.0, end_time=60.0),
            )
        ]

        config = ChunkConfig(target_words=40, overlap_words=5)
        result = adapter.chunk(raw_chunks, source, config)

        assert len(result) >= 2
        for i, chunk in enumerate(result):
            assert chunk.sequence_index == i


class TestAudioAdapterGetLocation:
    """Tests for AudioAdapter.get_location method."""

    @pytest.mark.description("get_location returns chunk location")
    def test_get_location_returns_location(self) -> None:
        from voogle.adapters.base import TextChunk

        adapter = AudioAdapter()
        location = TimestampLocation(start_time=10.0, end_time=20.0)
        chunk = TextChunk(
            text="test",
            source_id="test",
            source_type=ContentType.AUDIO,
            location=location,
        )

        result = adapter.get_location(chunk)
        assert result == location

    @pytest.mark.description("get_location returns None when no location")
    def test_get_location_returns_none(self) -> None:
        from voogle.adapters.base import TextChunk

        adapter = AudioAdapter()
        chunk = TextChunk(
            text="test",
            source_id="test",
            source_type=ContentType.AUDIO,
        )

        result = adapter.get_location(chunk)
        assert result is None


class TestAudioAdapterGetDeepLink:
    """Tests for AudioAdapter.get_deep_link method."""

    @pytest.mark.description("get_deep_link generates timestamp URL")
    def test_get_deep_link_with_timestamp(self) -> None:
        from voogle.adapters.base import TextChunk

        adapter = AudioAdapter()
        location = TimestampLocation(start_time=120.5, end_time=130.0)
        chunk = TextChunk(
            text="test",
            source_id="test",
            source_type=ContentType.AUDIO,
            location=location,
        )

        result = adapter.get_deep_link(chunk, "https://example.com/audio.mp3")
        assert result is not None
        assert "t=120.5" in result

    @pytest.mark.description("get_deep_link returns None without location")
    def test_get_deep_link_without_location(self) -> None:
        from voogle.adapters.base import TextChunk

        adapter = AudioAdapter()
        chunk = TextChunk(
            text="test",
            source_id="test",
            source_type=ContentType.AUDIO,
        )

        result = adapter.get_deep_link(chunk, "https://example.com/audio.mp3")
        assert result is None


class TestTranscriptionConfig:
    """Tests for TranscriptionConfig dataclass."""

    @pytest.mark.description("TranscriptionConfig has correct defaults")
    def test_default_values(self) -> None:
        config = TranscriptionConfig()
        assert config.model_name == "small"
        assert config.device == "cpu"
        assert config.compute_type == "int8"
        assert config.word_timestamps is False
        assert config.language is None
        assert config.initial_prompt is None

    @pytest.mark.description("TranscriptionConfig accepts custom values")
    def test_custom_values(self) -> None:
        config = TranscriptionConfig(
            model_name="large-v3",
            device="cuda",
            compute_type="float16",
            word_timestamps=True,
            language="es",
            initial_prompt="This is a podcast about...",
        )
        assert config.model_name == "large-v3"
        assert config.device == "cuda"
        assert config.word_timestamps is True
        assert config.language == "es"


class TestAudioExtensions:
    """Tests for AUDIO_EXTENSIONS constant."""

    @pytest.mark.description("AUDIO_EXTENSIONS contains required formats")
    def test_required_formats(self) -> None:
        assert ".mp3" in AUDIO_EXTENSIONS
        assert ".wav" in AUDIO_EXTENSIONS
        assert ".flac" in AUDIO_EXTENSIONS
        assert ".m4a" in AUDIO_EXTENSIONS

    @pytest.mark.description("AUDIO_EXTENSIONS is frozen")
    def test_is_frozen(self) -> None:
        assert isinstance(AUDIO_EXTENSIONS, frozenset)
