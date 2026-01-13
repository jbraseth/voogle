# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Pipeline stages for media processing.

This module provides the Stage protocol and concrete implementations
for processing media through various stages:
- Fetching: Retrieve content from URLs, files, cloud storage, YouTube, RSS
- Transcription: Convert audio to text
- Embedding: Generate vector embeddings
- Indexing: Store in vector database
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class StageError(Exception):
    """Base exception for stage errors."""


class FetchError(StageError):
    """Raised when content fetching fails."""


class ContentTypeError(StageError):
    """Raised when content type is unsupported or cannot be detected."""


class StorageError(StageError):
    """Raised when storage operations fail."""


class ContentType(Enum):
    """Supported content types for fetching."""

    AUDIO_MP3 = "audio/mpeg"
    AUDIO_WAV = "audio/wav"
    AUDIO_OGG = "audio/ogg"
    AUDIO_FLAC = "audio/flac"
    AUDIO_M4A = "audio/mp4"
    VIDEO_MP4 = "video/mp4"
    VIDEO_WEBM = "video/webm"
    APPLICATION_RSS = "application/rss+xml"
    APPLICATION_XML = "application/xml"
    TEXT_XML = "text/xml"
    UNKNOWN = "application/octet-stream"

    @classmethod
    def from_mime(cls, mime_type: str) -> ContentType:
        """Convert MIME type string to ContentType enum."""
        mime_lower = mime_type.lower().split(";")[0].strip()
        for content_type in cls:
            if content_type.value == mime_lower:
                return content_type
        return cls.UNKNOWN

    @classmethod
    def from_extension(cls, extension: str) -> ContentType:
        """Infer content type from file extension."""
        ext_map = {
            ".mp3": cls.AUDIO_MP3,
            ".wav": cls.AUDIO_WAV,
            ".ogg": cls.AUDIO_OGG,
            ".flac": cls.AUDIO_FLAC,
            ".m4a": cls.AUDIO_M4A,
            ".mp4": cls.VIDEO_MP4,
            ".webm": cls.VIDEO_WEBM,
            ".xml": cls.APPLICATION_XML,
            ".rss": cls.APPLICATION_RSS,
        }
        return ext_map.get(extension.lower(), cls.UNKNOWN)

    def is_audio(self) -> bool:
        """Check if content type is audio."""
        return self.value.startswith("audio/")

    def is_video(self) -> bool:
        """Check if content type is video."""
        return self.value.startswith("video/")

    def is_media(self) -> bool:
        """Check if content type is audio or video."""
        return self.is_audio() or self.is_video()


@dataclass(frozen=True)
class FetchResult:
    """Result of a fetch operation.

    Attributes:
        source: Original source URL/path
        local_path: Path to fetched content on local filesystem
        content_type: Detected content type
        size_bytes: Content size in bytes
        metadata: Additional metadata from the source
    """

    source: str
    local_path: str
    content_type: ContentType
    size_bytes: int
    metadata: dict


class Stage(Protocol):
    """Protocol for pipeline stages.

    Stages should:
    - Validate inputs at boundaries (fail loud)
    - Handle errors explicitly
    - Be composable with other stages
    """

    def process(self, source: str) -> FetchResult:
        """Process input and return result.

        Args:
            source: Source URL or path to process

        Returns:
            FetchResult with local path and metadata

        Raises:
            StageError: If processing fails
        """
        ...

    def __repr__(self) -> str:
        """Return string representation of stage."""
        ...


__all__ = [
    "ContentType",
    "ContentTypeError",
    "FetchError",
    "FetchResult",
    "Stage",
    "StageError",
    "StorageError",
]
