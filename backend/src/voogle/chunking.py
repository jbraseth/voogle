# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Chunking configuration for text fragmentation.

Provides per-channel chunking configuration for experimentation with different
chunk sizes, overlaps, and minimum lengths.
"""
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ChunkingConfig:
    """Configuration for text chunking strategy.

    Attributes:
        chunk_size_words: Target number of words per fragment.
        chunk_overlap_words: Number of words to overlap between fragments.
        min_chunk_length_words: Minimum words required to include a fragment.
    """

    chunk_size_words: int = 40
    chunk_overlap_words: int = 0
    min_chunk_length_words: int = 10

    def __post_init__(self) -> None:
        if self.chunk_size_words < 1:
            raise ValueError(f"chunk_size_words must be >= 1, got {self.chunk_size_words}")
        if self.chunk_overlap_words < 0:
            raise ValueError(
                f"chunk_overlap_words must be >= 0, got {self.chunk_overlap_words}"
            )
        if self.chunk_overlap_words >= self.chunk_size_words:
            raise ValueError(
                f"chunk_overlap_words ({self.chunk_overlap_words}) "
                f"must be < chunk_size_words ({self.chunk_size_words})"
            )
        if self.min_chunk_length_words < 1:
            raise ValueError(
                f"min_chunk_length_words must be >= 1, got {self.min_chunk_length_words}"
            )


DEFAULT_CONFIG = ChunkingConfig()


def _get_config_path() -> Path:
    """Return path to chunking config file."""
    return Path(__file__).parent.parent.parent.parent / "config" / "chunking.yaml"


def load_chunking_config(channel_id: Optional[str] = None) -> ChunkingConfig:
    """Load chunking config for a channel.

    Args:
        channel_id: Optional channel ID for per-channel config lookup.

    Returns:
        ChunkingConfig with channel-specific or default settings.

    Raises:
        ValueError: If config file contains invalid values.
    """
    config_path = _get_config_path()
    if not config_path.exists():
        logger.debug(f"no chunking config at {config_path}, using defaults")
        return DEFAULT_CONFIG

    with open(config_path) as f:
        data = yaml.safe_load(f)

    if data is None:
        return DEFAULT_CONFIG

    # Get channel-specific or default config
    if channel_id and "channels" in data and channel_id in data["channels"]:
        channel_data = data["channels"][channel_id]
        config_data = {**data.get("default", {}), **channel_data}
        logger.info(f"using channel-specific chunking config for {channel_id}")
    else:
        config_data = data.get("default", {})

    if not config_data:
        return DEFAULT_CONFIG

    return ChunkingConfig(**config_data)
