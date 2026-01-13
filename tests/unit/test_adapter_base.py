# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for ContentAdapter base class and related dataclasses."""
from collections.abc import AsyncIterator
from pathlib import Path

import pytest

from voogle.adapters.base import (
    ChunkConfig,
    ContentAdapter,
    ContentSource,
    RawChunk,
    TextChunk,
)
from voogle.core import ContentType, Location, TimestampLocation

pytestmark = pytest.mark.unit


class TestContentSource:
    """Tests for ContentSource dataclass."""

    @pytest.mark.description("ContentSource with path creates successfully")
    def test_create_with_path(self) -> None:
        source = ContentSource(
            source_id="src-123",
            source_type=ContentType.AUDIO,
            path=Path("/data/audio.mp3"),
        )
        assert source.source_id == "src-123"
        assert source.source_type == ContentType.AUDIO
        assert source.path == Path("/data/audio.mp3")
        assert source.url is None
        assert source.metadata == {}

    @pytest.mark.description("ContentSource with url creates successfully")
    def test_create_with_url(self) -> None:
        source = ContentSource(
            source_id="src-456",
            source_type=ContentType.VIDEO,
            url="https://example.com/video.mp4",
        )
        assert source.source_id == "src-456"
        assert source.source_type == ContentType.VIDEO
        assert source.path is None
        assert source.url == "https://example.com/video.mp4"

    @pytest.mark.description("ContentSource with both path and url creates successfully")
    def test_create_with_both(self) -> None:
        source = ContentSource(
            source_id="src-789",
            source_type=ContentType.DOCUMENT,
            path=Path("/data/doc.pdf"),
            url="https://example.com/doc.pdf",
            metadata={"author": "Test"},
        )
        assert source.path == Path("/data/doc.pdf")
        assert source.url == "https://example.com/doc.pdf"
        assert source.metadata == {"author": "Test"}

    @pytest.mark.description("ContentSource without path or url raises ValueError")
    def test_no_path_or_url_raises(self) -> None:
        with pytest.raises(ValueError, match="At least one of path or url must be provided"):
            ContentSource(
                source_id="src-fail",
                source_type=ContentType.AUDIO,
            )

    @pytest.mark.description("ContentSource with empty source_id raises ValueError")
    def test_empty_source_id_raises(self) -> None:
        with pytest.raises(ValueError, match="source_id cannot be empty"):
            ContentSource(
                source_id="",
                source_type=ContentType.AUDIO,
                path=Path("/data/audio.mp3"),
            )

    @pytest.mark.description("ContentSource is immutable")
    def test_immutable(self) -> None:
        source = ContentSource(
            source_id="src",
            source_type=ContentType.AUDIO,
            path=Path("/data/audio.mp3"),
        )
        with pytest.raises(Exception):  # FrozenInstanceError
            source.source_id = "changed"  # type: ignore[misc]


class TestRawChunk:
    """Tests for RawChunk dataclass."""

    @pytest.mark.description("RawChunk with minimal fields creates successfully")
    def test_create_minimal(self) -> None:
        chunk = RawChunk(text="Hello world")
        assert chunk.text == "Hello world"
        assert chunk.location is None
        assert chunk.confidence is None
        assert chunk.metadata == {}

    @pytest.mark.description("RawChunk with all fields creates successfully")
    def test_create_full(self) -> None:
        location = TimestampLocation(start_time=10.0, end_time=20.0)
        chunk = RawChunk(
            text="Sample text",
            location=location,
            confidence=0.95,
            metadata={"speaker": "Alice"},
        )
        assert chunk.text == "Sample text"
        assert chunk.location == location
        assert chunk.confidence == 0.95
        assert chunk.metadata == {"speaker": "Alice"}

    @pytest.mark.description("RawChunk with invalid confidence raises ValueError")
    def test_invalid_confidence_raises(self) -> None:
        with pytest.raises(ValueError, match="confidence must be between 0.0 and 1.0"):
            RawChunk(text="test", confidence=1.5)
        with pytest.raises(ValueError, match="confidence must be between 0.0 and 1.0"):
            RawChunk(text="test", confidence=-0.1)

    @pytest.mark.description("RawChunk boundary confidence values succeed")
    def test_boundary_confidence(self) -> None:
        chunk_zero = RawChunk(text="test", confidence=0.0)
        assert chunk_zero.confidence == 0.0
        chunk_one = RawChunk(text="test", confidence=1.0)
        assert chunk_one.confidence == 1.0


class TestTextChunk:
    """Tests for TextChunk dataclass."""

    @pytest.mark.description("TextChunk with required fields creates successfully")
    def test_create_minimal(self) -> None:
        chunk = TextChunk(
            text="Hello world",
            source_id="src-1",
            source_type=ContentType.AUDIO,
        )
        assert chunk.text == "Hello world"
        assert chunk.source_id == "src-1"
        assert chunk.source_type == ContentType.AUDIO
        assert chunk.location is None
        assert chunk.sequence_index == 0
        assert chunk.metadata == {}

    @pytest.mark.description("TextChunk with all fields creates successfully")
    def test_create_full(self) -> None:
        location = TimestampLocation(start_time=5.0)
        chunk = TextChunk(
            text="Sample",
            source_id="src-2",
            source_type=ContentType.VIDEO,
            location=location,
            sequence_index=3,
            metadata={"chapter": 1},
        )
        assert chunk.location == location
        assert chunk.sequence_index == 3
        assert chunk.metadata == {"chapter": 1}

    @pytest.mark.description("TextChunk with empty text raises ValueError")
    def test_empty_text_raises(self) -> None:
        with pytest.raises(ValueError, match="text cannot be empty"):
            TextChunk(text="", source_id="src", source_type=ContentType.AUDIO)

    @pytest.mark.description("TextChunk with empty source_id raises ValueError")
    def test_empty_source_id_raises(self) -> None:
        with pytest.raises(ValueError, match="source_id cannot be empty"):
            TextChunk(text="test", source_id="", source_type=ContentType.AUDIO)

    @pytest.mark.description("TextChunk with negative sequence_index raises ValueError")
    def test_negative_sequence_index_raises(self) -> None:
        with pytest.raises(ValueError, match="sequence_index must be >= 0"):
            TextChunk(
                text="test",
                source_id="src",
                source_type=ContentType.AUDIO,
                sequence_index=-1,
            )


class TestChunkConfig:
    """Tests for ChunkConfig dataclass."""

    @pytest.mark.description("ChunkConfig with defaults creates successfully")
    def test_default_values(self) -> None:
        config = ChunkConfig()
        assert config.target_words == 40
        assert config.max_words == 60
        assert config.overlap_words == 5
        assert config.preserve_sentences is True

    @pytest.mark.description("ChunkConfig with custom values creates successfully")
    def test_custom_values(self) -> None:
        config = ChunkConfig(
            target_words=50,
            max_words=80,
            overlap_words=10,
            preserve_sentences=False,
        )
        assert config.target_words == 50
        assert config.max_words == 80
        assert config.overlap_words == 10
        assert config.preserve_sentences is False

    @pytest.mark.description("ChunkConfig with invalid target_words raises ValueError")
    def test_invalid_target_words_raises(self) -> None:
        with pytest.raises(ValueError, match="target_words must be >= 1"):
            ChunkConfig(target_words=0)

    @pytest.mark.description("ChunkConfig with max_words < target_words raises ValueError")
    def test_max_less_than_target_raises(self) -> None:
        with pytest.raises(ValueError, match="max_words must be >= target_words"):
            ChunkConfig(target_words=50, max_words=40)

    @pytest.mark.description("ChunkConfig with negative overlap_words raises ValueError")
    def test_negative_overlap_raises(self) -> None:
        with pytest.raises(ValueError, match="overlap_words must be >= 0"):
            ChunkConfig(overlap_words=-1)

    @pytest.mark.description("ChunkConfig with overlap_words >= target_words raises ValueError")
    def test_overlap_too_large_raises(self) -> None:
        with pytest.raises(ValueError, match="overlap_words must be < target_words"):
            ChunkConfig(target_words=40, overlap_words=40)


class TestContentAdapter:
    """Tests for ContentAdapter abstract base class."""

    @pytest.mark.description("ContentAdapter requires all abstract methods")
    def test_abstract_methods_required(self) -> None:
        # Verify the abstract methods exist
        abstract_methods = ContentAdapter.__abstractmethods__
        assert "supported_types" in abstract_methods
        assert "supports" in abstract_methods
        assert "extract" in abstract_methods
        assert "chunk" in abstract_methods
        assert "get_location" in abstract_methods
        assert "get_deep_link" in abstract_methods

    @pytest.mark.description("ContentAdapter cannot be instantiated directly")
    def test_cannot_instantiate(self) -> None:
        with pytest.raises(TypeError, match="abstract"):
            ContentAdapter()  # type: ignore[abstract]

    @pytest.mark.description("Concrete adapter implementation works correctly")
    def test_concrete_implementation(self) -> None:
        """Test that a concrete implementation can be created and used."""

        class MockAdapter(ContentAdapter):
            @property
            def supported_types(self) -> frozenset[ContentType]:
                return frozenset({ContentType.AUDIO})

            def supports(self, source: ContentSource) -> bool:
                return source.source_type in self.supported_types

            async def extract(self, source: ContentSource) -> AsyncIterator[RawChunk]:
                yield RawChunk(text="test chunk")

            def chunk(
                self,
                raw_chunks: list[RawChunk],
                source: ContentSource,
                config: ChunkConfig | None = None,
            ) -> list[TextChunk]:
                return [
                    TextChunk(
                        text=rc.text,
                        source_id=source.source_id,
                        source_type=source.source_type,
                        sequence_index=i,
                    )
                    for i, rc in enumerate(raw_chunks)
                ]

            def get_location(self, chunk: TextChunk) -> Location | None:
                return chunk.location

            def get_deep_link(self, chunk: TextChunk, base_url: str) -> str | None:
                if chunk.location:
                    return chunk.location.to_deep_link(base_url)
                return None

        adapter = MockAdapter()
        assert adapter.supported_types == frozenset({ContentType.AUDIO})

        audio_source = ContentSource(
            source_id="test",
            source_type=ContentType.AUDIO,
            path=Path("/test.mp3"),
        )
        video_source = ContentSource(
            source_id="test",
            source_type=ContentType.VIDEO,
            path=Path("/test.mp4"),
        )

        assert adapter.supports(audio_source) is True
        assert adapter.supports(video_source) is False

    @pytest.mark.description("Concrete adapter extract is async generator")
    @pytest.mark.asyncio
    async def test_extract_async_generator(self) -> None:
        """Test that extract returns an async iterator."""

        class MockAdapter(ContentAdapter):
            @property
            def supported_types(self) -> frozenset[ContentType]:
                return frozenset({ContentType.TEXT})

            def supports(self, source: ContentSource) -> bool:
                return True

            async def extract(self, source: ContentSource) -> AsyncIterator[RawChunk]:
                for i in range(3):
                    yield RawChunk(text=f"chunk {i}")

            def chunk(
                self,
                raw_chunks: list[RawChunk],
                source: ContentSource,
                config: ChunkConfig | None = None,
            ) -> list[TextChunk]:
                return []

            def get_location(self, chunk: TextChunk) -> Location | None:
                return None

            def get_deep_link(self, chunk: TextChunk, base_url: str) -> str | None:
                return None

        adapter = MockAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            path=Path("/test.txt"),
        )

        chunks = []
        async for chunk in adapter.extract(source):
            chunks.append(chunk)

        assert len(chunks) == 3
        assert chunks[0].text == "chunk 0"
        assert chunks[1].text == "chunk 1"
        assert chunks[2].text == "chunk 2"
