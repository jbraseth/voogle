# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""External source adapters for ingesting media into Voogle.

This module provides adapters for external platforms (YouTube, etc.) that
produce local files + RSS feeds that can be consumed by the existing
collection pipeline.

The core abstractions are:
- LocalFeed: Represents a generated RSS feed file
- SourceAdapter: Protocol that all source adapters must implement
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class SourceAdapterError(Exception):
    """Base exception for source adapter errors."""


class ConfigurationError(SourceAdapterError):
    """Raised when adapter configuration is invalid."""


class FeedGenerationError(SourceAdapterError):
    """Raised when RSS feed generation fails."""


@dataclass(frozen=True)
class LocalFeed:
    """Represents a generated RSS feed file for local content.

    Attributes:
        path: Absolute path to the generated RSS feed XML file
        source_id: Identifier for the source adapter (e.g., "youtube")
        channel_url: Logical URL for the channel (e.g., "local://youtube/PLxxx")

    The channel_url uses the local:// scheme to distinguish from HTTP feeds.
    This URL is used as the unique identifier for the channel in the database.
    """

    path: Path
    source_id: str
    channel_url: str

    def __post_init__(self) -> None:
        """Validate feed at boundary (fail loud)."""
        if not self.path.is_absolute():
            raise ConfigurationError(f"Feed path must be absolute: {self.path}")

        if not self.path.suffix == ".xml":
            raise ConfigurationError(f"Feed path must be XML file: {self.path}")

        if not self.channel_url.startswith("local://"):
            raise ConfigurationError(
                f"Channel URL must use local:// scheme: {self.channel_url}"
            )

        if not self.source_id:
            raise ConfigurationError("source_id cannot be empty")

    def exists(self) -> bool:
        """Check if the feed file exists on disk."""
        return self.path.exists()


class SourceAdapter(Protocol):
    """Protocol for adapters that generate RSS feeds from various sources.

    Implementations must:
    1. Read source configuration from their designated directory
    2. Generate valid RSS 2.0 XML files
    3. Return LocalFeed references to generated files
    4. Handle all errors explicitly (fail loud)

    Example implementations:
    - YouTubePlaylistAdapter: Generates feeds from YouTube playlists
    - LocalMediaAdapter: Generates feeds from local audio file directories
    """

    @property
    def adapter_id(self) -> str:
        """Unique identifier for this adapter (e.g., 'youtube').

        Used for:
        - Organizing generated feed files: data/generated-feeds/{adapter_id}/
        - Constructing channel URLs: local://{adapter_id}/...
        """
        ...

    @property
    def config_dir(self) -> Path:
        """Directory where this adapter reads its configuration.

        Example: data/local/youtube/ contains JSON files describing playlists
        """
        ...

    @property
    def output_dir(self) -> Path:
        """Directory where this adapter writes generated RSS feeds.

        Example: data/generated-feeds/youtube/
        """
        ...

    def generate_feeds(self) -> list[LocalFeed]:
        """Generate RSS feed files from source configuration.

        Returns:
            List of LocalFeed objects pointing to generated XML files

        Raises:
            ConfigurationError: If configuration is invalid
            FeedGenerationError: If feed generation fails
        """
        ...


__all__ = [
    "ConfigurationError",
    "FeedGenerationError",
    "LocalFeed",
    "SourceAdapter",
    "SourceAdapterError",
]
