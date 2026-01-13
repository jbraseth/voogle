# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Chunking stage for the ingestion pipeline.

Provides configurable chunking strategies for splitting content into
processable chunks for embedding and indexing:
- Fixed-size: Token-based chunking with configurable overlap
- Semantic: Embedding similarity-based boundary detection
- Structure-aware: Respects document structure (paragraphs, sections)
"""

from __future__ import annotations

import logging
import re
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol, runtime_checkable

from voogle.pipeline.base import Stage

logger = logging.getLogger(__name__)


class ChunkStrategy(Enum):
    """Available chunking strategies."""

    FIXED_SIZE = "fixed_size"
    SEMANTIC = "semantic"
    STRUCTURE_AWARE = "structure_aware"


@dataclass(frozen=True)
class ChunkConfig:
    """Configuration for the chunking stage.

    Attributes:
        size: Target chunk size (in tokens for fixed-size, chars for others).
        overlap: Number of tokens/chars to overlap between chunks.
        strategy: Chunking strategy to use.
        min_chunk_size: Minimum chunk size to emit (smaller chunks merged).
        max_chunk_size: Maximum chunk size (larger chunks split).
        separator_pattern: Regex pattern for structure-aware splitting.
        similarity_threshold: Threshold for semantic chunking (0.0-1.0).
    """

    size: int = 512
    overlap: int = 50
    strategy: ChunkStrategy = ChunkStrategy.FIXED_SIZE
    min_chunk_size: int = 50
    max_chunk_size: int | None = None
    separator_pattern: str = r"\n\n+"
    similarity_threshold: float = 0.5

    def __post_init__(self) -> None:
        """Validate chunk configuration."""
        if self.size < 1:
            raise ValueError(f"size must be >= 1, got {self.size}")
        if self.overlap < 0:
            raise ValueError(f"overlap must be >= 0, got {self.overlap}")
        if self.overlap >= self.size:
            raise ValueError(
                f"overlap ({self.overlap}) must be < size ({self.size})"
            )
        if self.min_chunk_size < 1:
            raise ValueError(f"min_chunk_size must be >= 1, got {self.min_chunk_size}")
        if self.max_chunk_size is not None and self.max_chunk_size < self.size:
            raise ValueError(
                f"max_chunk_size ({self.max_chunk_size}) must be >= size ({self.size})"
            )
        if not 0.0 <= self.similarity_threshold <= 1.0:
            raise ValueError(
                f"similarity_threshold must be in [0.0, 1.0], got {self.similarity_threshold}"
            )


@dataclass
class Chunk:
    """A chunk of content with metadata.

    Attributes:
        content: The text content of the chunk.
        index: Index of this chunk within the source document.
        start_offset: Character offset in original content where chunk starts.
        end_offset: Character offset in original content where chunk ends.
        metadata: Additional metadata about the chunk.
    """

    content: str
    index: int
    start_offset: int
    end_offset: int
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def token_count(self) -> int:
        """Approximate token count (words)."""
        return len(self.content.split())


@dataclass
class ChunkableContent:
    """Content to be chunked with source metadata.

    Attributes:
        text: The text content to chunk.
        source_id: Identifier for the source document.
        metadata: Additional metadata from the source.
    """

    text: str
    source_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class EmbeddingProvider(Protocol):
    """Protocol for embedding providers used in semantic chunking."""

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        ...


class ChunkingStrategy(ABC):
    """Base class for chunking strategies."""

    @abstractmethod
    def chunk(self, content: ChunkableContent, config: ChunkConfig) -> list[Chunk]:
        """Split content into chunks.

        Args:
            content: The content to chunk.
            config: Chunking configuration.

        Returns:
            List of chunks.
        """
        ...


class FixedSizeChunker(ChunkingStrategy):
    """Fixed-size chunking based on token count with overlap."""

    def chunk(self, content: ChunkableContent, config: ChunkConfig) -> list[Chunk]:
        """Split content into fixed-size chunks with overlap.

        Uses word-based tokenization for simplicity. Overlaps are added
        from the end of the previous chunk to maintain context.

        Args:
            content: The content to chunk.
            config: Chunking configuration.

        Returns:
            List of chunks with approximately `config.size` tokens each.
        """
        text = content.text
        if not text.strip():
            return []

        words = text.split()
        if not words:
            return []

        chunks: list[Chunk] = []
        step = config.size - config.overlap
        if step < 1:
            step = 1

        current_offset = 0
        word_idx = 0
        chunk_index = 0

        while word_idx < len(words):
            chunk_words = words[word_idx : word_idx + config.size]

            if len(chunk_words) < config.min_chunk_size and chunks:
                # Merge small trailing chunk with previous
                last_chunk = chunks[-1]
                merged_content = last_chunk.content + " " + " ".join(chunk_words)
                chunks[-1] = Chunk(
                    content=merged_content,
                    index=last_chunk.index,
                    start_offset=last_chunk.start_offset,
                    end_offset=len(text),
                    metadata={**content.metadata, "source_id": content.source_id},
                )
                break

            chunk_text = " ".join(chunk_words)

            # Calculate offsets in original text
            start_offset = current_offset
            end_offset = start_offset + len(chunk_text)

            chunks.append(
                Chunk(
                    content=chunk_text,
                    index=chunk_index,
                    start_offset=start_offset,
                    end_offset=end_offset,
                    metadata={**content.metadata, "source_id": content.source_id},
                )
            )

            word_idx += step
            current_offset = end_offset + 1  # +1 for space
            chunk_index += 1

        return chunks


class SemanticChunker(ChunkingStrategy):
    """Semantic chunking based on embedding similarity.

    Splits text at sentence boundaries where embedding similarity
    drops below the configured threshold.
    """

    def __init__(self, embedding_provider: EmbeddingProvider | None = None) -> None:
        """Initialize the semantic chunker.

        Args:
            embedding_provider: Provider for generating embeddings.
                If None, falls back to fixed-size chunking.
        """
        self._embedding_provider = embedding_provider

    def chunk(self, content: ChunkableContent, config: ChunkConfig) -> list[Chunk]:
        """Split content based on semantic similarity.

        First splits text into sentences, then groups sentences
        into chunks based on embedding similarity thresholds.

        Args:
            content: The content to chunk.
            config: Chunking configuration.

        Returns:
            List of semantically coherent chunks.
        """
        text = content.text
        if not text.strip():
            return []

        # Split into sentences
        sentences = self._split_sentences(text)
        if not sentences:
            return []

        if len(sentences) == 1:
            return [
                Chunk(
                    content=sentences[0],
                    index=0,
                    start_offset=0,
                    end_offset=len(text),
                    metadata={**content.metadata, "source_id": content.source_id},
                )
            ]

        # If no embedding provider, use fixed-size as fallback
        if self._embedding_provider is None:
            logger.warning("No embedding provider for semantic chunking, using fixed-size")
            return FixedSizeChunker().chunk(content, config)

        # Get embeddings for all sentences
        try:
            embeddings = self._embedding_provider.embed(sentences)
        except Exception as e:
            logger.warning(f"Embedding failed, falling back to fixed-size: {e}")
            return FixedSizeChunker().chunk(content, config)

        # Group sentences by similarity
        chunks: list[Chunk] = []
        current_sentences: list[str] = [sentences[0]]
        current_start = 0
        chunk_index = 0

        for i in range(1, len(sentences)):
            similarity = self._cosine_similarity(embeddings[i - 1], embeddings[i])

            if similarity < config.similarity_threshold:
                # Similarity drop - create new chunk
                chunk_content = " ".join(current_sentences)
                chunk_end = text.find(sentences[i - 1], current_start)
                if chunk_end == -1:
                    chunk_end = current_start + len(chunk_content)
                else:
                    chunk_end += len(sentences[i - 1])

                chunks.append(
                    Chunk(
                        content=chunk_content,
                        index=chunk_index,
                        start_offset=current_start,
                        end_offset=chunk_end,
                        metadata={**content.metadata, "source_id": content.source_id},
                    )
                )
                current_sentences = [sentences[i]]
                current_start = text.find(sentences[i], chunk_end)
                if current_start == -1:
                    current_start = chunk_end
                chunk_index += 1
            else:
                current_sentences.append(sentences[i])

        # Add final chunk
        if current_sentences:
            chunk_content = " ".join(current_sentences)
            chunks.append(
                Chunk(
                    content=chunk_content,
                    index=chunk_index,
                    start_offset=current_start,
                    end_offset=len(text),
                    metadata={**content.metadata, "source_id": content.source_id},
                )
            )

        return chunks

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        # Simple sentence splitting on common terminators
        pattern = r"(?<=[.!?])\s+"
        sentences = re.split(pattern, text.strip())
        return [s.strip() for s in sentences if s.strip()]

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(a) != len(b) or not a:
            return 0.0
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)


class StructureAwareChunker(ChunkingStrategy):
    """Structure-aware chunking that respects document structure.

    Splits on structural boundaries (paragraphs, sections) while
    ensuring chunks stay within size limits.
    """

    def chunk(self, content: ChunkableContent, config: ChunkConfig) -> list[Chunk]:
        """Split content respecting structural boundaries.

        First splits on the separator pattern, then merges or splits
        segments to fit within size constraints.

        Args:
            content: The content to chunk.
            config: Chunking configuration.

        Returns:
            List of structurally-aligned chunks.
        """
        text = content.text
        if not text.strip():
            return []

        # Split on structural boundaries
        pattern = config.separator_pattern
        segments = re.split(pattern, text)
        segments = [s.strip() for s in segments if s.strip()]

        if not segments:
            return []

        chunks: list[Chunk] = []
        current_segments: list[str] = []
        current_token_count = 0
        current_start = 0
        chunk_index = 0

        for segment in segments:
            segment_tokens = len(segment.split())

            # Check if adding this segment would exceed max size
            max_size = config.max_chunk_size or (config.size * 2)
            if current_token_count + segment_tokens > max_size and current_segments:
                # Create chunk from current segments
                chunk_content = "\n\n".join(current_segments)
                chunk_end = text.find(current_segments[-1], current_start)
                if chunk_end == -1:
                    chunk_end = current_start + len(chunk_content)
                else:
                    chunk_end += len(current_segments[-1])

                chunks.append(
                    Chunk(
                        content=chunk_content,
                        index=chunk_index,
                        start_offset=current_start,
                        end_offset=chunk_end,
                        metadata={**content.metadata, "source_id": content.source_id},
                    )
                )

                current_segments = []
                current_token_count = 0
                current_start = text.find(segment, chunk_end)
                if current_start == -1:
                    current_start = chunk_end
                chunk_index += 1

            # If a single segment is too large, split it with fixed-size
            if segment_tokens > max_size:
                sub_content = ChunkableContent(
                    text=segment,
                    source_id=content.source_id,
                    metadata=content.metadata,
                )
                sub_chunks = FixedSizeChunker().chunk(sub_content, config)
                for sub_chunk in sub_chunks:
                    sub_chunk.index = chunk_index
                    sub_chunk.start_offset += current_start
                    sub_chunk.end_offset += current_start
                    chunks.append(sub_chunk)
                    chunk_index += 1
                current_start += len(segment) + 2  # +2 for \n\n separator
                continue

            current_segments.append(segment)
            current_token_count += segment_tokens

        # Add final chunk
        if current_segments:
            chunk_content = "\n\n".join(current_segments)
            chunks.append(
                Chunk(
                    content=chunk_content,
                    index=chunk_index,
                    start_offset=current_start,
                    end_offset=len(text),
                    metadata={**content.metadata, "source_id": content.source_id},
                )
            )

        # Merge small chunks if needed
        merged_chunks: list[Chunk] = []
        for chunk in chunks:
            if (
                merged_chunks
                and chunk.token_count < config.min_chunk_size
                and merged_chunks[-1].token_count < config.size
            ):
                # Merge with previous
                prev = merged_chunks[-1]
                merged_content = prev.content + "\n\n" + chunk.content
                merged_chunks[-1] = Chunk(
                    content=merged_content,
                    index=prev.index,
                    start_offset=prev.start_offset,
                    end_offset=chunk.end_offset,
                    metadata=prev.metadata,
                )
            else:
                merged_chunks.append(chunk)

        # Re-index merged chunks
        for i, chunk in enumerate(merged_chunks):
            chunk.index = i

        return merged_chunks


class ChunkingStage(Stage[ChunkableContent, Chunk]):
    """Pipeline stage for chunking content.

    Supports multiple chunking strategies:
    - FIXED_SIZE: Token-based with overlap (default)
    - SEMANTIC: Embedding similarity-based boundaries
    - STRUCTURE_AWARE: Respects document structure

    Example:
        config = ChunkConfig(size=512, overlap=50)
        stage = ChunkingStage(config)

        async for chunk in stage.process(content_iterator):
            print(f"Chunk {chunk.index}: {chunk.content[:50]}...")
    """

    def __init__(
        self,
        config: ChunkConfig | None = None,
        embedding_provider: EmbeddingProvider | None = None,
    ) -> None:
        """Initialize the chunking stage.

        Args:
            config: Chunking configuration. Uses defaults if not provided.
            embedding_provider: Provider for semantic chunking embeddings.
        """
        self._config = config or ChunkConfig()
        self._embedding_provider = embedding_provider
        self._strategy: ChunkingStrategy | None = None

    @property
    def name(self) -> str:
        """Return the name of this stage."""
        return "chunking"

    @property
    def config(self) -> ChunkConfig:
        """Return the chunking configuration."""
        return self._config

    async def setup(self) -> None:
        """Initialize the chunking strategy."""
        if self._config.strategy == ChunkStrategy.FIXED_SIZE:
            self._strategy = FixedSizeChunker()
        elif self._config.strategy == ChunkStrategy.SEMANTIC:
            self._strategy = SemanticChunker(self._embedding_provider)
        elif self._config.strategy == ChunkStrategy.STRUCTURE_AWARE:
            self._strategy = StructureAwareChunker()
        else:
            self._strategy = FixedSizeChunker()

        logger.info(f"ChunkingStage initialized with {self._config.strategy.value} strategy")

    async def process(
        self, items: AsyncIterator[ChunkableContent]
    ) -> AsyncIterator[Chunk]:
        """Process content items and yield chunks.

        Args:
            items: Async iterator of content to chunk.

        Yields:
            Individual chunks from each content item.
        """
        if self._strategy is None:
            await self.setup()

        async for content in items:
            if not content.text.strip():
                logger.debug(f"Skipping empty content: {content.source_id}")
                continue

            try:
                chunks = self._strategy.chunk(content, self._config)  # type: ignore
                logger.debug(
                    f"Chunked {content.source_id} into {len(chunks)} chunks"
                )
                for chunk in chunks:
                    yield chunk
            except Exception as e:
                logger.error(f"Failed to chunk {content.source_id}: {e}")
                raise

    def __str__(self) -> str:
        """Return string representation."""
        return (
            f"ChunkingStage(strategy={self._config.strategy.value}, "
            f"size={self._config.size}, overlap={self._config.overlap})"
        )

    def __repr__(self) -> str:
        """Return detailed representation."""
        return (
            f"ChunkingStage(config={self._config!r}, "
            f"embedding_provider={self._embedding_provider!r})"
        )
