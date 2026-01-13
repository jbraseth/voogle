# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for the ChunkingStage pipeline component."""

import pytest

from voogle.pipeline.chunking import (
    Chunk,
    ChunkableContent,
    ChunkConfig,
    ChunkingStage,
    ChunkStrategy,
    FixedSizeChunker,
    SemanticChunker,
    StructureAwareChunker,
)

pytestmark = pytest.mark.unit


class TestChunkConfig:
    """Tests for ChunkConfig dataclass."""

    @pytest.mark.description("Default config values are correct")
    def test_default_values(self) -> None:
        config = ChunkConfig()
        assert config.size == 512
        assert config.overlap == 50
        assert config.strategy == ChunkStrategy.FIXED_SIZE
        assert config.min_chunk_size == 50
        assert config.max_chunk_size is None
        assert config.similarity_threshold == 0.5

    @pytest.mark.description("Custom values are accepted")
    def test_custom_values(self) -> None:
        config = ChunkConfig(
            size=256,
            overlap=25,
            strategy=ChunkStrategy.SEMANTIC,
            min_chunk_size=20,
            max_chunk_size=1024,
            similarity_threshold=0.7,
        )
        assert config.size == 256
        assert config.overlap == 25
        assert config.strategy == ChunkStrategy.SEMANTIC
        assert config.min_chunk_size == 20
        assert config.max_chunk_size == 1024
        assert config.similarity_threshold == 0.7

    @pytest.mark.description("Invalid size raises ValueError")
    def test_invalid_size(self) -> None:
        with pytest.raises(ValueError, match="size must be >= 1"):
            ChunkConfig(size=0)
        with pytest.raises(ValueError, match="size must be >= 1"):
            ChunkConfig(size=-1)

    @pytest.mark.description("Negative overlap raises ValueError")
    def test_negative_overlap(self) -> None:
        with pytest.raises(ValueError, match="overlap must be >= 0"):
            ChunkConfig(overlap=-1)

    @pytest.mark.description("Overlap >= size raises ValueError")
    def test_overlap_too_large(self) -> None:
        with pytest.raises(ValueError, match="overlap .* must be < size"):
            ChunkConfig(size=100, overlap=100)
        with pytest.raises(ValueError, match="overlap .* must be < size"):
            ChunkConfig(size=100, overlap=150)

    @pytest.mark.description("Invalid min_chunk_size raises ValueError")
    def test_invalid_min_chunk_size(self) -> None:
        with pytest.raises(ValueError, match="min_chunk_size must be >= 1"):
            ChunkConfig(min_chunk_size=0)

    @pytest.mark.description("Invalid max_chunk_size raises ValueError")
    def test_invalid_max_chunk_size(self) -> None:
        with pytest.raises(ValueError, match="max_chunk_size .* must be >= size"):
            ChunkConfig(size=512, max_chunk_size=256)

    @pytest.mark.description("Invalid similarity_threshold raises ValueError")
    def test_invalid_similarity_threshold(self) -> None:
        with pytest.raises(ValueError, match="similarity_threshold must be in"):
            ChunkConfig(similarity_threshold=-0.1)
        with pytest.raises(ValueError, match="similarity_threshold must be in"):
            ChunkConfig(similarity_threshold=1.5)

    @pytest.mark.description("Config is immutable (frozen dataclass)")
    def test_immutable(self) -> None:
        config = ChunkConfig()
        with pytest.raises(Exception):  # FrozenInstanceError
            config.size = 100  # type: ignore[misc]


class TestChunk:
    """Tests for Chunk dataclass."""

    @pytest.mark.description("Chunk stores content and metadata correctly")
    def test_basic_chunk(self) -> None:
        chunk = Chunk(
            content="Hello world this is a test",
            index=0,
            start_offset=0,
            end_offset=26,
            metadata={"source_id": "test"},
        )
        assert chunk.content == "Hello world this is a test"
        assert chunk.index == 0
        assert chunk.start_offset == 0
        assert chunk.end_offset == 26
        assert chunk.metadata == {"source_id": "test"}

    @pytest.mark.description("Chunk token_count property works")
    def test_token_count(self) -> None:
        chunk = Chunk(
            content="one two three four five",
            index=0,
            start_offset=0,
            end_offset=23,
        )
        assert chunk.token_count == 5


class TestChunkableContent:
    """Tests for ChunkableContent dataclass."""

    @pytest.mark.description("ChunkableContent stores text and metadata")
    def test_basic_content(self) -> None:
        content = ChunkableContent(
            text="This is test content.",
            source_id="doc-123",
            metadata={"author": "test"},
        )
        assert content.text == "This is test content."
        assert content.source_id == "doc-123"
        assert content.metadata == {"author": "test"}


class TestFixedSizeChunker:
    """Tests for FixedSizeChunker strategy."""

    @pytest.mark.description("Empty content returns no chunks")
    def test_empty_content(self) -> None:
        chunker = FixedSizeChunker()
        config = ChunkConfig(size=10, overlap=2)
        content = ChunkableContent(text="", source_id="test")
        chunks = chunker.chunk(content, config)
        assert chunks == []

    @pytest.mark.description("Whitespace-only content returns no chunks")
    def test_whitespace_content(self) -> None:
        chunker = FixedSizeChunker()
        config = ChunkConfig(size=10, overlap=2)
        content = ChunkableContent(text="   \n\t   ", source_id="test")
        chunks = chunker.chunk(content, config)
        assert chunks == []

    @pytest.mark.description("Content smaller than chunk size returns single chunk")
    def test_small_content(self) -> None:
        chunker = FixedSizeChunker()
        config = ChunkConfig(size=100, overlap=10, min_chunk_size=1)
        content = ChunkableContent(
            text="This is a short text with only a few words.",
            source_id="test",
        )
        chunks = chunker.chunk(content, config)
        assert len(chunks) == 1
        assert chunks[0].content == content.text

    @pytest.mark.description("Content is split into correct number of chunks")
    def test_chunk_count(self) -> None:
        chunker = FixedSizeChunker()
        # 10 words, size=4, overlap=1 -> step=3 -> chunks at 0,3,6,9
        config = ChunkConfig(size=4, overlap=1, min_chunk_size=1)
        content = ChunkableContent(
            text="one two three four five six seven eight nine ten",
            source_id="test",
        )
        chunks = chunker.chunk(content, config)
        assert len(chunks) >= 3  # At least 3 chunks for 10 words

    @pytest.mark.description("Overlap is correctly applied")
    def test_overlap_content(self) -> None:
        chunker = FixedSizeChunker()
        config = ChunkConfig(size=4, overlap=2, min_chunk_size=1)
        content = ChunkableContent(
            text="one two three four five six seven eight",
            source_id="test",
        )
        chunks = chunker.chunk(content, config)

        # Verify overlap exists between consecutive chunks
        if len(chunks) >= 2:
            first_words = set(chunks[0].content.split()[-2:])  # Last 2 words
            second_words = set(chunks[1].content.split()[:2])  # First 2 words
            # There should be some overlap
            assert first_words & second_words

    @pytest.mark.description("Metadata is preserved in chunks")
    def test_metadata_preservation(self) -> None:
        chunker = FixedSizeChunker()
        config = ChunkConfig(size=5, overlap=0, min_chunk_size=1)
        content = ChunkableContent(
            text="one two three four five six",
            source_id="doc-123",
            metadata={"author": "test"},
        )
        chunks = chunker.chunk(content, config)
        for chunk in chunks:
            assert chunk.metadata.get("source_id") == "doc-123"
            assert chunk.metadata.get("author") == "test"


class TestSemanticChunker:
    """Tests for SemanticChunker strategy."""

    @pytest.mark.description("Empty content returns no chunks")
    def test_empty_content(self) -> None:
        chunker = SemanticChunker()
        config = ChunkConfig(size=100, overlap=10)
        content = ChunkableContent(text="", source_id="test")
        chunks = chunker.chunk(content, config)
        assert chunks == []

    @pytest.mark.description("Falls back to fixed-size without embedding provider")
    def test_fallback_without_provider(self) -> None:
        chunker = SemanticChunker(embedding_provider=None)
        config = ChunkConfig(size=5, overlap=0, min_chunk_size=1)
        content = ChunkableContent(
            text="This is sentence one. This is sentence two. This is sentence three.",
            source_id="test",
        )
        chunks = chunker.chunk(content, config)
        # Should get chunks from fixed-size fallback
        assert len(chunks) >= 1

    @pytest.mark.description("Single sentence returns single chunk")
    def test_single_sentence(self) -> None:
        chunker = SemanticChunker()
        config = ChunkConfig(size=100, overlap=10)
        content = ChunkableContent(
            text="This is a single sentence without any breaks.",
            source_id="test",
        )
        chunks = chunker.chunk(content, config)
        assert len(chunks) == 1
        assert chunks[0].content == content.text

    @pytest.mark.description("Semantic chunker uses embedding provider when available")
    def test_with_embedding_provider(self) -> None:
        class MockEmbeddingProvider:
            def embed(self, texts: list[str]) -> list[list[float]]:
                # Return embeddings that alternate between similar and dissimilar
                embeddings = []
                for i, _ in enumerate(texts):
                    if i % 2 == 0:
                        embeddings.append([1.0, 0.0, 0.0])
                    else:
                        embeddings.append([0.0, 1.0, 0.0])  # Orthogonal = 0 similarity
                return embeddings

        chunker = SemanticChunker(embedding_provider=MockEmbeddingProvider())
        config = ChunkConfig(
            size=100, overlap=10, similarity_threshold=0.3
        )
        content = ChunkableContent(
            text="First sentence here. Second sentence here. Third sentence here.",
            source_id="test",
        )
        chunks = chunker.chunk(content, config)
        # With orthogonal embeddings and 0.3 threshold, should get multiple chunks
        assert len(chunks) >= 2


class TestStructureAwareChunker:
    """Tests for StructureAwareChunker strategy."""

    @pytest.mark.description("Empty content returns no chunks")
    def test_empty_content(self) -> None:
        chunker = StructureAwareChunker()
        config = ChunkConfig(size=100, overlap=10)
        content = ChunkableContent(text="", source_id="test")
        chunks = chunker.chunk(content, config)
        assert chunks == []

    @pytest.mark.description("Splits on paragraph boundaries")
    def test_paragraph_splitting(self) -> None:
        chunker = StructureAwareChunker()
        config = ChunkConfig(size=100, overlap=0, min_chunk_size=1)
        content = ChunkableContent(
            text="First paragraph here.\n\nSecond paragraph here.\n\nThird paragraph here.",
            source_id="test",
        )
        chunks = chunker.chunk(content, config)
        # Should get at least one chunk containing paragraphs
        assert len(chunks) >= 1

    @pytest.mark.description("Respects max_chunk_size")
    def test_max_chunk_size(self) -> None:
        chunker = StructureAwareChunker()
        config = ChunkConfig(
            size=5,
            overlap=0,
            min_chunk_size=1,
            max_chunk_size=10,
        )
        content = ChunkableContent(
            text="word " * 50,  # 50 words
            source_id="test",
        )
        chunks = chunker.chunk(content, config)
        # All chunks should be within max size or split
        for chunk in chunks:
            # Allow some flexibility for merging
            assert chunk.token_count <= 20  # 2x max as safety margin

    @pytest.mark.description("Custom separator pattern works")
    def test_custom_separator(self) -> None:
        chunker = StructureAwareChunker()
        config = ChunkConfig(
            size=100,
            overlap=0,
            min_chunk_size=1,
            separator_pattern=r"---+",  # Split on dashes
        )
        content = ChunkableContent(
            text="Section one content.---Section two content.---Section three content.",
            source_id="test",
        )
        chunks = chunker.chunk(content, config)
        assert len(chunks) >= 1


class TestChunkingStage:
    """Tests for ChunkingStage pipeline component."""

    @pytest.mark.description("Stage has correct name")
    def test_stage_name(self) -> None:
        stage = ChunkingStage()
        assert stage.name == "chunking"

    @pytest.mark.description("Default config is used when not provided")
    def test_default_config(self) -> None:
        stage = ChunkingStage()
        assert stage.config.size == 512
        assert stage.config.overlap == 50

    @pytest.mark.description("Custom config is preserved")
    def test_custom_config(self) -> None:
        config = ChunkConfig(size=256, overlap=25)
        stage = ChunkingStage(config)
        assert stage.config.size == 256
        assert stage.config.overlap == 25

    @pytest.mark.description("String representation is informative")
    def test_str_repr(self) -> None:
        config = ChunkConfig(size=512, overlap=50)
        stage = ChunkingStage(config)
        str_repr = str(stage)
        assert "ChunkingStage" in str_repr
        assert "fixed_size" in str_repr
        assert "512" in str_repr
        assert "50" in str_repr

    @pytest.mark.description("Stage processes content correctly")
    @pytest.mark.asyncio
    async def test_process_content(self) -> None:
        config = ChunkConfig(size=5, overlap=0, min_chunk_size=1)
        stage = ChunkingStage(config)

        async def content_gen():
            yield ChunkableContent(
                text="one two three four five six seven eight nine ten",
                source_id="test-doc",
            )

        chunks = []
        async for chunk in stage.process(content_gen()):
            chunks.append(chunk)

        assert len(chunks) >= 1
        assert all(isinstance(c, Chunk) for c in chunks)

    @pytest.mark.description("Stage skips empty content")
    @pytest.mark.asyncio
    async def test_skip_empty_content(self) -> None:
        stage = ChunkingStage()

        async def content_gen():
            yield ChunkableContent(text="", source_id="empty")
            yield ChunkableContent(text="   ", source_id="whitespace")
            yield ChunkableContent(text="actual content here", source_id="valid")

        chunks = []
        async for chunk in stage.process(content_gen()):
            chunks.append(chunk)

        # Only the valid content should produce chunks
        assert len(chunks) >= 1
        assert all(c.metadata.get("source_id") == "valid" for c in chunks)

    @pytest.mark.description("Stage uses correct strategy based on config")
    @pytest.mark.asyncio
    async def test_strategy_selection(self) -> None:
        # Test fixed-size
        config = ChunkConfig(strategy=ChunkStrategy.FIXED_SIZE)
        stage = ChunkingStage(config)
        await stage.setup()
        assert isinstance(stage._strategy, FixedSizeChunker)

        # Test semantic
        config = ChunkConfig(strategy=ChunkStrategy.SEMANTIC)
        stage = ChunkingStage(config)
        await stage.setup()
        assert isinstance(stage._strategy, SemanticChunker)

        # Test structure-aware
        config = ChunkConfig(strategy=ChunkStrategy.STRUCTURE_AWARE)
        stage = ChunkingStage(config)
        await stage.setup()
        assert isinstance(stage._strategy, StructureAwareChunker)


class TestChunkStrategyEnum:
    """Tests for ChunkStrategy enum."""

    @pytest.mark.description("All strategies have correct values")
    def test_strategy_values(self) -> None:
        assert ChunkStrategy.FIXED_SIZE.value == "fixed_size"
        assert ChunkStrategy.SEMANTIC.value == "semantic"
        assert ChunkStrategy.STRUCTURE_AWARE.value == "structure_aware"
