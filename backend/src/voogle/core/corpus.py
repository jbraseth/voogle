# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Corpus dataclass for organizing searchable content collections.

A Corpus represents a collection of documents that can be searched together,
providing organizational structure and collection-level settings.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from voogle.core.fragment import ContentType


@dataclass
class Corpus:
    """A searchable collection of documents.

    Represents a logical grouping of content that can be searched together,
    with its own settings and metadata.

    Attributes:
        id: Unique identifier for this corpus.
        name: Human-readable name for the corpus.
        description: Optional description of the corpus contents.
        content_types: List of content types allowed in this corpus.
        settings: Corpus-level configuration as key-value pairs.
        created_at: Timestamp when the corpus was created.
        updated_at: Timestamp when the corpus was last modified.
        document_count: Number of documents in this corpus.
    """

    id: str
    name: str
    description: str
    content_types: list[ContentType]
    settings: dict[str, Any]
    document_count: int
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate corpus data after initialization."""
        if not self.id:
            raise ValueError("id cannot be empty")
        if not self.name:
            raise ValueError("name cannot be empty")
        if self.document_count < 0:
            raise ValueError("document_count must be >= 0")
