# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Modular ingestion pipeline architecture.

This module provides the core infrastructure for building content processing
pipelines. Pipelines orchestrate source fetching, content extraction,
chunking, embedding, and indexing through composable stages.

Exports:
    Pipeline: Main pipeline orchestrator class.
    Stage: Abstract base class for pipeline stages.
    PipelineConfig: Configuration for pipeline execution.
    RetryConfig: Configuration for retry behavior.
    RetryStrategy: Enum for retry strategies (none, fixed, exponential).
    StageStatus: Enum for stage execution status.
    StageProgress: Progress tracking for individual stages.
    PipelineProgress: Progress tracking for entire pipeline.
    StageError: Exception for stage processing failures.
    PipelineError: Exception for pipeline-level failures.

Fetching Stage Exports:
    ContentType: Enum for content MIME types.
    ContentTypeError: Exception for unsupported content types.
    FetchError: Exception for fetching failures.
    FetchResult: Dataclass for fetch operation results.
    StorageError: Exception for storage operation failures.

Example:
    from voogle.pipeline import Pipeline, Stage, PipelineConfig

    class FetchStage(Stage[str, dict]):
        @property
        def name(self) -> str:
            return "fetch"

        async def process(self, items):
            async for url in items:
                yield await fetch_data(url)

    config = PipelineConfig(max_concurrency=4)
    pipeline = Pipeline([FetchStage()], config)

    async for result in pipeline.execute(urls):
        print(result)
"""

from dataclasses import dataclass
from enum import Enum

from voogle.pipeline.base import (
    Pipeline,
    PipelineConfig,
    PipelineError,
    PipelineProgress,
    RetryConfig,
    RetryStrategy,
    Stage,
    StageError,
    StageProgress,
    StageStatus,
)
from voogle.pipeline.chunking import (
    Chunk,
    ChunkableContent,
    ChunkConfig,
    ChunkingStage,
    ChunkStrategy,
)
from voogle.pipeline.indexing import (
    EmbeddedFragment,
    IndexingConfig,
    IndexingResult,
    IndexingStage,
    generate_point_id,
)


# Fetching stage exceptions - use simpler signature than base StageError
class FetchError(Exception):
    """Raised when content fetching fails."""


class ContentTypeError(Exception):
    """Raised when content type is unsupported or cannot be detected."""


class StorageError(Exception):
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
    def from_mime(cls, mime_type: str) -> "ContentType":
        """Convert MIME type string to ContentType enum."""
        mime_lower = mime_type.lower().split(";")[0].strip()
        for content_type in cls:
            if content_type.value == mime_lower:
                return content_type
        return cls.UNKNOWN

    @classmethod
    def from_extension(cls, extension: str) -> "ContentType":
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


__all__ = [
    "Chunk",
    "ChunkConfig",
    "ChunkStrategy",
    "ChunkableContent",
    "ChunkingStage",
    "ContentType",
    "ContentTypeError",
    "EmbeddedFragment",
    "FetchError",
    "FetchResult",
    "IndexingConfig",
    "IndexingResult",
    "IndexingStage",
    "Pipeline",
    "PipelineConfig",
    "PipelineError",
    "PipelineProgress",
    "RetryConfig",
    "RetryStrategy",
    "Stage",
    "StageError",
    "StageProgress",
    "StageStatus",
    "StorageError",
    "generate_point_id",
]
