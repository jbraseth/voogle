# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Abstract ContentAdapter base class for content extraction and chunking.

This module defines the interface that all content type adapters must implement.
Adapters handle extracting text from various content sources (audio transcripts,
PDFs, videos, slides, etc.) and chunking them into fragments suitable for
embedding and semantic search.
"""
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from voogle.core.fragment import ContentType
from voogle.core.location import Location


@dataclass(frozen=True)
class ContentSource:
    """Represents a content source to be processed by an adapter.

    Attributes:
        source_id: Unique identifier for this content source.
        source_type: The type of content (audio, video, document, etc.).
        path: Local file path to the content, if available.
        url: Remote URL to the content, if available.
        metadata: Additional source-specific metadata.
    """

    source_id: str
    source_type: ContentType
    path: Path | None = None
    url: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate that at least one of path or url is provided."""
        if not self.source_id:
            raise ValueError("source_id cannot be empty")
        if self.path is None and self.url is None:
            raise ValueError("At least one of path or url must be provided")


@dataclass(frozen=True)
class RawChunk:
    """A raw chunk of extracted content before text processing.

    Represents content extracted directly from a source with its
    location information, before any text normalization or chunking.

    Attributes:
        text: The raw extracted text content.
        location: Location within the source (timestamp, page, etc.).
        confidence: Extraction confidence score (0.0 to 1.0), if available.
        metadata: Additional extraction metadata.
    """

    text: str
    location: Location | None = None
    confidence: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate raw chunk data."""
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {self.confidence}")


@dataclass(frozen=True)
class TextChunk:
    """A processed text chunk ready for embedding.

    Represents a normalized, sized chunk of text that can be
    converted to an embedding vector for semantic search.

    Attributes:
        text: The processed text content.
        source_id: Identifier of the source this chunk came from.
        source_type: Type of content source.
        location: Location within the source for deep linking.
        sequence_index: Order of this chunk within the source.
        metadata: Additional chunk metadata.
    """

    text: str
    source_id: str
    source_type: ContentType
    location: Location | None = None
    sequence_index: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate text chunk data."""
        if not self.text:
            raise ValueError("text cannot be empty")
        if not self.source_id:
            raise ValueError("source_id cannot be empty")
        if self.sequence_index < 0:
            raise ValueError(f"sequence_index must be >= 0, got {self.sequence_index}")


@dataclass(frozen=True)
class ChunkConfig:
    """Configuration for chunking behavior.

    Attributes:
        target_words: Target number of words per chunk.
        max_words: Maximum number of words per chunk.
        overlap_words: Number of words to overlap between chunks.
        preserve_sentences: Whether to preserve sentence boundaries.
    """

    target_words: int = 40
    max_words: int = 60
    overlap_words: int = 5
    preserve_sentences: bool = True

    def __post_init__(self) -> None:
        """Validate chunk configuration."""
        if self.target_words < 1:
            raise ValueError(f"target_words must be >= 1, got {self.target_words}")
        if self.max_words < self.target_words:
            raise ValueError(f"max_words must be >= target_words, got {self.max_words}")
        if self.overlap_words < 0:
            raise ValueError(f"overlap_words must be >= 0, got {self.overlap_words}")
        if self.overlap_words >= self.target_words:
            raise ValueError("overlap_words must be < target_words")


class ContentAdapter(ABC):
    """Abstract base class for content type adapters.

    Subclasses implement content extraction and chunking for specific
    content types (audio, video, PDF, slides, etc.). Each adapter
    handles the full pipeline from raw content to searchable chunks.
    """

    @property
    @abstractmethod
    def supported_types(self) -> frozenset[ContentType]:
        """Return the content types this adapter can process.

        Returns:
            Frozen set of ContentType values this adapter supports.
        """

    @abstractmethod
    def supports(self, source: ContentSource) -> bool:
        """Check if this adapter can process the given source.

        Args:
            source: The content source to check.

        Returns:
            True if this adapter can process the source, False otherwise.
        """

    @abstractmethod
    async def extract(self, source: ContentSource) -> AsyncIterator[RawChunk]:
        """Extract raw content chunks from the source.

        Yields raw chunks of content with location information as they
        are extracted from the source. For large sources, this should
        stream results to avoid loading everything into memory.

        Args:
            source: The content source to extract from.

        Yields:
            RawChunk instances containing extracted text and locations.

        Raises:
            ValueError: If the source is not supported by this adapter.
        """
        # This yield is required to make this an async generator
        # Subclasses should override this entirely
        if False:  # pragma: no cover
            yield RawChunk(text="")

    @abstractmethod
    def chunk(
        self,
        raw_chunks: list[RawChunk],
        source: ContentSource,
        config: ChunkConfig | None = None,
    ) -> list[TextChunk]:
        """Process raw chunks into text chunks for embedding.

        Combines, splits, and normalizes raw chunks according to the
        chunking configuration to produce properly-sized text chunks.

        Args:
            raw_chunks: List of raw chunks from extraction.
            source: The source these chunks came from.
            config: Chunking configuration. Uses defaults if not provided.

        Returns:
            List of TextChunk instances ready for embedding.
        """

    @abstractmethod
    def get_location(self, chunk: TextChunk) -> Location | None:
        """Get the location for a text chunk.

        Args:
            chunk: The text chunk to get location for.

        Returns:
            Location instance for deep linking, or None if not available.
        """

    @abstractmethod
    def get_deep_link(self, chunk: TextChunk, base_url: str) -> str | None:
        """Generate a deep link URL for a text chunk.

        Args:
            chunk: The text chunk to generate a link for.
            base_url: The base URL of the content source.

        Returns:
            Full URL to navigate directly to this chunk, or None if
            deep linking is not supported.
        """
