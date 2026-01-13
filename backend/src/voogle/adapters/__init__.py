# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Content adapters for extracting and chunking various content types.

This module provides the abstract base class and data structures for
building content adapters that handle different media formats (audio,
video, documents, slides, etc.).
"""
from voogle.adapters.base import (
    ChunkConfig,
    ContentAdapter,
    ContentSource,
    RawChunk,
    TextChunk,
)
from voogle.adapters.registry import AdapterRegistry

__all__ = [
    "AdapterRegistry",
    "ChunkConfig",
    "ContentAdapter",
    "ContentSource",
    "RawChunk",
    "TextChunk",
]
