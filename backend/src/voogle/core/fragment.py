# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Fragment dataclass for representing searchable content units.

A Fragment represents the atomic unit of searchable content in Voogle,
regardless of the source type (audio, video, document, etc.). It provides
polymorphic location support for different content types.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class ContentType(Enum):
    """Type of content source for a fragment.

    Used to determine how to interpret location and deep_link fields.
    """

    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    SLIDE = "slide"
    TEXT = "text"


@dataclass(frozen=True)
class Fragment:
    """A searchable unit of content from any source type.

    Represents a fragment of text that has been indexed for semantic search,
    along with its source information and relevance score.

    Attributes:
        id: Unique identifier for this fragment.
        text: The text content of this fragment.
        score: Relevance score from semantic search (0.0 to 1.0).
        source_id: Identifier of the source containing this fragment.
        source_type: Type of content source (audio, video, document, etc.).
        location: Source-specific location data (e.g., timestamp for audio,
            page number for documents). None if not applicable.
        deep_link: URL or path to directly access this fragment in context.
            None if not available.
        metadata: Additional source-specific metadata as key-value pairs.
    """

    id: str
    text: str
    score: float
    source_id: str
    source_type: ContentType
    location: Optional[Any] = None
    deep_link: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate fragment data after initialization."""
        if not self.id:
            raise ValueError("id cannot be empty")
        if not self.text:
            raise ValueError("text cannot be empty")
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(f"score must be between 0.0 and 1.0, got {self.score}")
        if not self.source_id:
            raise ValueError("source_id cannot be empty")
