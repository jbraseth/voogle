# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for VideoAdapter content adapter."""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from voogle.adapters.video import (
    VIDEO_EXTENSIONS,
    VideoAdapter,
    VideoConfig,
    _is_youtube_url,
)
from voogle.adapters.base import ChunkConfig, ContentSource, RawChunk
from voogle.core.fragment import ContentType
from voogle.core.location import SlideLocation, TimestampLocation

pytestmark = pytest.mark.unit


class TestVideoAdapterInit:
    """Tests for VideoAdapter initialization."""

    @pytest.mark.description("VideoAdapter initializes with default config")
    def test_init_default_config(self) -> None:
        adapter = VideoAdapter()
        assert adapter._config.model_name == "small"
        assert adapter._config.device == "cpu"
        assert adapter._config.compute_type == "int8"
        assert adapter._config.word_timestamps is False
        assert adapter._config.extract_keyframes is True
        assert adapter._config.enable_slide_ocr is False
        assert adapter._config.generate_thumbnails is False

    @pytest.mark.description("VideoAdapter initializes with custom config")
    def test_init_custom_config(self) -> None:
        config = VideoConfig(
            model_name="large",
            device="cuda",
            compute_type="float16",
            word_timestamps=True,
            language="en",
            extract_keyframes=False,
            enable_slide_ocr=True,
            generate_thumbnails=True,
        )
        adapter = VideoAdapter(config=config)
        assert adapter._config.model_name == "large"
        assert adapter._config.device == "cuda"
        assert adapter._config.word_timestamps is True
        assert adapter._config.extract_keyframes is False
        assert adapter._config.enable_slide_ocr is True


class TestVideoAdapterSupportedTypes:
    """Tests for VideoAdapter.supported_types property."""

    @pytest.mark.description("supported_types returns VIDEO only")
    def test_supported_types(self) -> None:
        adapter = VideoAdapter()
        assert adapter.supported_types == frozenset({ContentType.VIDEO})


class TestVideoAdapterSupports:
    """Tests for VideoAdapter.supports method."""

    @pytest.mark.description("supports returns True for MP4 files")
    def test_supports_mp4(self) -> None:
        adapter = VideoAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.VIDEO,
            path=Path("/data/video.mp4"),
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns True for WebM files")
    def test_supports_webm(self) -> None:
        adapter = VideoAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.VIDEO,
            path=Path("/data/video.webm"),
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns True for MKV files")
    def test_supports_mkv(self) -> None:
        adapter = VideoAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.VIDEO,
            path=Path("/data/video.mkv"),
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns True for AVI files")
    def test_supports_avi(self) -> None:
        adapter = VideoAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.VIDEO,
            path=Path("/data/video.avi"),
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns True for MOV files")
    def test_supports_mov(self) -> None:
        adapter = VideoAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.VIDEO,
            path=Path("/data/video.mov"),
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns False for non-video content type")
    def test_rejects_non_video_type(self) -> None:
        adapter = VideoAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.AUDIO,
            path=Path("/data/audio.mp3"),
        )
        assert adapter.supports(source) is False

    @pytest.mark.description("supports returns False for unsupported extension")
    def test_rejects_unsupported_extension(self) -> None:
        adapter = VideoAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.VIDEO,
            path=Path("/data/video.flv"),
        )
        assert adapter.supports(source) is False

    @pytest.mark.description("supports works with URL sources")
    def test_supports_url_source(self) -> None:
        adapter = VideoAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.VIDEO,
            url="https://example.com/video.mp4",
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns True for YouTube URLs")
    def test_supports_youtube_url(self) -> None:
        adapter = VideoAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.VIDEO,
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns True for YouTube short URLs")
    def test_supports_youtube_short_url(self) -> None:
        adapter = VideoAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.VIDEO,
            url="https://youtu.be/dQw4w9WgXcQ",
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns True for video MIME type")
    def test_supports_mime_type(self) -> None:
        adapter = VideoAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.VIDEO,
            url="https://example.com/stream",
            metadata={"mime_type": "video/mp4"},
        )
        assert adapter.supports(source) is True


class TestVideoAdapterExtract:
    """Tests for VideoAdapter.extract method."""

    @pytest.mark.description("extract raises ValueError for unsupported source")
    @pytest.mark.asyncio
    async def test_extract_unsupported_raises(self) -> None:
        adapter = VideoAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.AUDIO,
            path=Path("/data/audio.mp3"),
        )
        with pytest.raises(ValueError, match="Unsupported source"):
            async for _ in adapter.extract(source):
                pass

    @pytest.mark.description("extract raises ValueError for missing file")
    @pytest.mark.asyncio
    async def test_extract_missing_file_raises(self) -> None:
        adapter = VideoAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.VIDEO,
            path=Path("/nonexistent/video.mp4"),
        )
        with pytest.raises(ValueError, match="Video file not found"):
            async for _ in adapter.extract(source):
                pass

    @pytest.mark.description("extract yields RawChunks with segment timestamps")
    @pytest.mark.asyncio
    async def test_extract_segment_level(self, tmp_path: Path) -> None:
        # Create a mock video file
        video_file = tmp_path / "test.mp4"
        video_file.touch()

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

        # Disable keyframe extraction for this test
        config = VideoConfig(extract_keyframes=False)
        adapter = VideoAdapter(config=config)
        source = ContentSource(
            source_id="test",
            source_type=ContentType.VIDEO,
            path=video_file,
        )

        with patch("voogle.adapters.video._get_model", return_value=mock_model):
            chunks = []
            async for chunk in adapter.extract(source):
                chunks.append(chunk)

        assert len(chunks) == 1
        assert chunks[0].text == "Hello world"
        assert isinstance(chunks[0].location, TimestampLocation)
        assert chunks[0].location.start_time == 0.0
        assert chunks[0].location.end_time == 5.0
        assert chunks[0].metadata["language"] == "en"
        assert chunks[0].metadata["chunk_type"] == "transcription"

    @pytest.mark.description("extract yields word-level chunks when enabled")
    @pytest.mark.asyncio
    async def test_extract_word_level(self, tmp_path: Path) -> None:
        video_file = tmp_path / "test.mp4"
        video_file.touch()

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
        mock_info.language_probability = 0.99

        # Create mock model
        mock_model = MagicMock()
        mock_model.transcribe.return_value = ([mock_segment], mock_info)

        config = VideoConfig(word_timestamps=True, extract_keyframes=False)
        adapter = VideoAdapter(config=config)
        source = ContentSource(
            source_id="test",
            source_type=ContentType.VIDEO,
            path=video_file,
        )

        with patch("voogle.adapters.video._get_model", return_value=mock_model):
            chunks = []
            async for chunk in adapter.extract(source):
                chunks.append(chunk)

        assert len(chunks) == 2
        assert chunks[0].text == "Hello"
        assert chunks[0].location.start_time == 0.0
        assert chunks[0].location.end_time == 0.5
        assert chunks[1].text == "world"
        assert chunks[1].location.start_time == 0.6


class TestVideoAdapterChunk:
    """Tests for VideoAdapter.chunk method."""

    @pytest.mark.description("chunk returns empty list for empty input")
    def test_chunk_empty_input(self) -> None:
        adapter = VideoAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.VIDEO,
            path=Path("/data/video.mp4"),
        )
        result = adapter.chunk([], source)
        assert result == []

    @pytest.mark.description("chunk combines transcription words into target-sized chunks")
    def test_chunk_combines_transcription(self) -> None:
        adapter = VideoAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.VIDEO,
            path=Path("/data/video.mp4"),
        )

        # Create raw chunks that together have more than target words
        words = "one two three four five six seven eight nine ten " * 5  # 50 words
        raw_chunks = [
            RawChunk(
                text=words,
                location=TimestampLocation(start_time=0.0, end_time=30.0),
                metadata={"chunk_type": "transcription"},
            )
        ]

        config = ChunkConfig(target_words=40, overlap_words=5)
        result = adapter.chunk(raw_chunks, source, config)

        assert len(result) >= 1
        assert all(chunk.source_id == "test" for chunk in result)
        assert all(chunk.source_type == ContentType.VIDEO for chunk in result)

    @pytest.mark.description("chunk preserves timestamps from transcription chunks")
    def test_chunk_preserves_timestamps(self) -> None:
        adapter = VideoAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.VIDEO,
            path=Path("/data/video.mp4"),
        )

        raw_chunks = [
            RawChunk(
                text="word " * 45,
                location=TimestampLocation(start_time=0.0, end_time=30.0),
                metadata={"chunk_type": "transcription"},
            )
        ]

        config = ChunkConfig(target_words=40, overlap_words=5)
        result = adapter.chunk(raw_chunks, source, config)

        assert len(result) >= 1
        assert result[0].location is not None
        assert isinstance(result[0].location, TimestampLocation)
        assert result[0].location.start_time == 0.0

    @pytest.mark.description("chunk keeps slide chunks separate")
    def test_chunk_keeps_slides_separate(self) -> None:
        adapter = VideoAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.VIDEO,
            path=Path("/data/video.mp4"),
        )

        raw_chunks = [
            RawChunk(
                text="Slide 1 content",
                location=SlideLocation(slide_number=1),
                metadata={"chunk_type": "slide"},
            ),
            RawChunk(
                text="Slide 2 content",
                location=SlideLocation(slide_number=2),
                metadata={"chunk_type": "slide"},
            ),
        ]

        result = adapter.chunk(raw_chunks, source)

        assert len(result) == 2
        assert result[0].text == "Slide 1 content"
        assert result[1].text == "Slide 2 content"
        assert isinstance(result[0].location, SlideLocation)
        assert result[0].location.slide_number == 1

    @pytest.mark.description("chunk handles mixed transcription and slide chunks")
    def test_chunk_mixed_content(self) -> None:
        adapter = VideoAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.VIDEO,
            path=Path("/data/video.mp4"),
        )

        raw_chunks = [
            RawChunk(
                text="word " * 45,
                location=TimestampLocation(start_time=0.0, end_time=30.0),
                metadata={"chunk_type": "transcription"},
            ),
            RawChunk(
                text="Slide content",
                location=SlideLocation(slide_number=1),
                metadata={"chunk_type": "slide"},
            ),
        ]

        config = ChunkConfig(target_words=40, overlap_words=5)
        result = adapter.chunk(raw_chunks, source, config)

        # Should have transcription chunks + slide chunks
        assert len(result) >= 2
        # Find the slide chunk
        slide_chunks = [c for c in result if c.metadata.get("chunk_type") == "slide"]
        assert len(slide_chunks) == 1
        assert slide_chunks[0].text == "Slide content"

    @pytest.mark.description("chunk increments sequence_index correctly")
    def test_chunk_sequence_index(self) -> None:
        adapter = VideoAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.VIDEO,
            path=Path("/data/video.mp4"),
        )

        raw_chunks = [
            RawChunk(
                text="word " * 100,
                location=TimestampLocation(start_time=0.0, end_time=60.0),
                metadata={"chunk_type": "transcription"},
            )
        ]

        config = ChunkConfig(target_words=40, overlap_words=5)
        result = adapter.chunk(raw_chunks, source, config)

        assert len(result) >= 2
        for i, chunk in enumerate(result):
            assert chunk.sequence_index == i


class TestVideoAdapterGetLocation:
    """Tests for VideoAdapter.get_location method."""

    @pytest.mark.description("get_location returns timestamp location")
    def test_get_location_returns_timestamp(self) -> None:
        from voogle.adapters.base import TextChunk

        adapter = VideoAdapter()
        location = TimestampLocation(start_time=10.0, end_time=20.0)
        chunk = TextChunk(
            text="test",
            source_id="test",
            source_type=ContentType.VIDEO,
            location=location,
        )

        result = adapter.get_location(chunk)
        assert result == location

    @pytest.mark.description("get_location returns slide location")
    def test_get_location_returns_slide(self) -> None:
        from voogle.adapters.base import TextChunk

        adapter = VideoAdapter()
        location = SlideLocation(slide_number=5)
        chunk = TextChunk(
            text="test",
            source_id="test",
            source_type=ContentType.VIDEO,
            location=location,
        )

        result = adapter.get_location(chunk)
        assert result == location

    @pytest.mark.description("get_location returns None when no location")
    def test_get_location_returns_none(self) -> None:
        from voogle.adapters.base import TextChunk

        adapter = VideoAdapter()
        chunk = TextChunk(
            text="test",
            source_id="test",
            source_type=ContentType.VIDEO,
        )

        result = adapter.get_location(chunk)
        assert result is None


class TestVideoAdapterGetDeepLink:
    """Tests for VideoAdapter.get_deep_link method."""

    @pytest.mark.description("get_deep_link generates timestamp URL")
    def test_get_deep_link_with_timestamp(self) -> None:
        from voogle.adapters.base import TextChunk

        adapter = VideoAdapter()
        location = TimestampLocation(start_time=120.5, end_time=130.0)
        chunk = TextChunk(
            text="test",
            source_id="test",
            source_type=ContentType.VIDEO,
            location=location,
        )

        result = adapter.get_deep_link(chunk, "https://example.com/video.mp4")
        assert result is not None
        assert "t=120.5" in result

    @pytest.mark.description("get_deep_link generates slide URL")
    def test_get_deep_link_with_slide(self) -> None:
        from voogle.adapters.base import TextChunk

        adapter = VideoAdapter()
        location = SlideLocation(slide_number=5)
        chunk = TextChunk(
            text="test",
            source_id="test",
            source_type=ContentType.VIDEO,
            location=location,
        )

        result = adapter.get_deep_link(chunk, "https://example.com/presentation")
        assert result is not None
        assert "slide=5" in result

    @pytest.mark.description("get_deep_link returns None without location")
    def test_get_deep_link_without_location(self) -> None:
        from voogle.adapters.base import TextChunk

        adapter = VideoAdapter()
        chunk = TextChunk(
            text="test",
            source_id="test",
            source_type=ContentType.VIDEO,
        )

        result = adapter.get_deep_link(chunk, "https://example.com/video.mp4")
        assert result is None


class TestVideoConfig:
    """Tests for VideoConfig dataclass."""

    @pytest.mark.description("VideoConfig has correct defaults")
    def test_default_values(self) -> None:
        config = VideoConfig()
        assert config.model_name == "small"
        assert config.device == "cpu"
        assert config.compute_type == "int8"
        assert config.word_timestamps is False
        assert config.language is None
        assert config.initial_prompt is None
        assert config.extract_keyframes is True
        assert config.scene_threshold == 30.0
        assert config.min_scene_duration == 2.0
        assert config.enable_slide_ocr is False
        assert config.ocr_language == "eng"
        assert config.generate_thumbnails is False
        assert config.thumbnail_size == (320, 180)
        assert config.thumbnail_dir is None

    @pytest.mark.description("VideoConfig accepts custom values")
    def test_custom_values(self) -> None:
        config = VideoConfig(
            model_name="large-v3",
            device="cuda",
            compute_type="float16",
            word_timestamps=True,
            language="es",
            extract_keyframes=True,
            scene_threshold=25.0,
            min_scene_duration=5.0,
            enable_slide_ocr=True,
            ocr_language="deu",
            generate_thumbnails=True,
            thumbnail_size=(640, 360),
            thumbnail_dir=Path("/thumbnails"),
        )
        assert config.model_name == "large-v3"
        assert config.device == "cuda"
        assert config.word_timestamps is True
        assert config.language == "es"
        assert config.scene_threshold == 25.0
        assert config.min_scene_duration == 5.0
        assert config.enable_slide_ocr is True
        assert config.ocr_language == "deu"
        assert config.thumbnail_dir == Path("/thumbnails")


class TestVideoExtensions:
    """Tests for VIDEO_EXTENSIONS constant."""

    @pytest.mark.description("VIDEO_EXTENSIONS contains required formats")
    def test_required_formats(self) -> None:
        assert ".mp4" in VIDEO_EXTENSIONS
        assert ".webm" in VIDEO_EXTENSIONS
        assert ".mkv" in VIDEO_EXTENSIONS
        assert ".avi" in VIDEO_EXTENSIONS
        assert ".mov" in VIDEO_EXTENSIONS

    @pytest.mark.description("VIDEO_EXTENSIONS is frozen")
    def test_is_frozen(self) -> None:
        assert isinstance(VIDEO_EXTENSIONS, frozenset)


class TestYouTubeUrlDetection:
    """Tests for _is_youtube_url helper function."""

    @pytest.mark.description("detects standard YouTube watch URLs")
    def test_standard_youtube_url(self) -> None:
        assert _is_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ") is True
        assert _is_youtube_url("http://www.youtube.com/watch?v=dQw4w9WgXcQ") is True
        assert _is_youtube_url("https://youtube.com/watch?v=dQw4w9WgXcQ") is True

    @pytest.mark.description("detects YouTube short URLs")
    def test_youtube_short_url(self) -> None:
        assert _is_youtube_url("https://youtu.be/dQw4w9WgXcQ") is True
        assert _is_youtube_url("http://youtu.be/dQw4w9WgXcQ") is True

    @pytest.mark.description("detects YouTube embed URLs")
    def test_youtube_embed_url(self) -> None:
        assert _is_youtube_url("https://www.youtube.com/embed/dQw4w9WgXcQ") is True

    @pytest.mark.description("rejects non-YouTube URLs")
    def test_non_youtube_url(self) -> None:
        assert _is_youtube_url("https://vimeo.com/123456") is False
        assert _is_youtube_url("https://example.com/video.mp4") is False
        assert _is_youtube_url("https://google.com") is False
