# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""MCP tool for corpus discovery with statistics.

Provides the MCP tool for listing available corpora with optional
statistics including document count and last updated timestamp.
"""
import base64
import json
from dataclasses import dataclass
from typing import Any, Optional

from voogle.services.corpus_service import CorpusService


@dataclass
class CorpusInfo:
    """Information about a single corpus.

    Attributes:
        id: Unique identifier of the corpus.
        name: Human-readable name of the corpus.
        description: Description of the corpus contents.
        document_count: Number of documents in the corpus (if stats requested).
        last_updated: ISO timestamp of last update (if stats requested).
    """

    id: str
    name: str
    description: str
    document_count: Optional[int] = None
    last_updated: Optional[str] = None


@dataclass
class ListCorporaOutput:
    """Output from the list_corpora tool.

    Attributes:
        corpora: List of corpus information objects.
        total_count: Total number of corpora available.
        next_cursor: Cursor for fetching the next page of results.
            None if no more results are available.
    """

    corpora: list[CorpusInfo]
    total_count: int
    next_cursor: Optional[str]


class ListCorporaTool:
    """MCP tool for corpus discovery.

    Provides corpus listing capabilities with support for:
    - Optional statistics (document count, last updated)
    - Cursor-based pagination
    - Cached statistics for performance
    """

    name: str = "list_corpora"
    description: str = (
        "List available corpora for semantic search. "
        "Returns corpus metadata with optional statistics like document count "
        "and last updated timestamp."
    )

    # Default page size
    DEFAULT_LIMIT: int = 20
    MAX_LIMIT: int = 100

    def __init__(self, corpus_service: Optional[CorpusService] = None) -> None:
        """Initialize the list corpora tool.

        Args:
            corpus_service: Optional CorpusService instance for fetching corpora.
                If None, creates a new service with default configuration.
        """
        self._corpus_service = corpus_service
        # Cache for corpus stats (keyed by corpus_id)
        self._stats_cache: dict[str, dict[str, Any]] = {}

    @property
    def corpus_service(self) -> CorpusService:
        """Get or lazily initialize the corpus service."""
        if self._corpus_service is None:
            self._corpus_service = CorpusService()
        return self._corpus_service

    @property
    def input_schema(self) -> dict[str, Any]:
        """Return the JSON schema for tool input parameters.

        Returns:
            JSON Schema dictionary describing the input format.
        """
        return {
            "type": "object",
            "properties": {
                "cursor": {
                    "type": "string",
                    "description": "Pagination cursor from a previous request",
                },
                "include_stats": {
                    "type": "boolean",
                    "description": "Include document count and last updated timestamp",
                    "default": False,
                },
                "limit": {
                    "type": "integer",
                    "description": f"Maximum number of corpora to return (1-{self.MAX_LIMIT})",
                    "minimum": 1,
                    "maximum": self.MAX_LIMIT,
                    "default": self.DEFAULT_LIMIT,
                },
            },
            "required": [],
        }

    def _encode_cursor(self, offset: int) -> str:
        """Encode pagination state into a cursor string.

        Args:
            offset: The offset position for the next page.

        Returns:
            Base64-encoded cursor string.
        """
        cursor_data = {"offset": offset}
        return base64.urlsafe_b64encode(json.dumps(cursor_data).encode()).decode()

    def _decode_cursor(self, cursor: str) -> int:
        """Decode a cursor string to get pagination state.

        Args:
            cursor: The base64-encoded cursor string.

        Returns:
            The offset value from the cursor.

        Raises:
            ValueError: If the cursor is invalid.
        """
        try:
            cursor_data = json.loads(base64.urlsafe_b64decode(cursor.encode()))
            return cursor_data.get("offset", 0)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise ValueError(f"Invalid cursor format: {cursor}") from e

    def _get_cached_stats(self, corpus_id: str) -> Optional[dict[str, Any]]:
        """Get cached statistics for a corpus.

        Args:
            corpus_id: The corpus ID to get stats for.

        Returns:
            Cached stats dict or None if not cached.
        """
        return self._stats_cache.get(corpus_id)

    def _cache_stats(self, corpus_id: str, stats: dict[str, Any]) -> None:
        """Cache statistics for a corpus.

        Args:
            corpus_id: The corpus ID.
            stats: The stats dict to cache.
        """
        self._stats_cache[corpus_id] = stats

    def __call__(
        self,
        cursor: Optional[str] = None,
        include_stats: bool = False,
        limit: int = 20,
    ) -> dict[str, Any]:
        """List available corpora with optional statistics.

        Args:
            cursor: Optional pagination cursor from a previous request.
            include_stats: If True, include document_count and last_updated.
            limit: Maximum number of corpora to return (1-100).

        Returns:
            Dictionary containing corpora list, total count, and next cursor.

        Raises:
            ValueError: If cursor is invalid or limit is out of range.
        """
        # Validate limit
        if limit < 1 or limit > self.MAX_LIMIT:
            raise ValueError(
                f"limit must be between 1 and {self.MAX_LIMIT}, got {limit}"
            )

        # Parse cursor to get offset
        offset = 0
        if cursor:
            offset = self._decode_cursor(cursor)

        # Get all corpora from service
        all_corpora = self.corpus_service.list_all()
        total_count = len(all_corpora)

        # Apply pagination
        paginated = all_corpora[offset : offset + limit]

        # Build output list
        corpora_list = []
        for corpus in paginated:
            corpus_info: dict[str, Any] = {
                "id": corpus.id,
                "name": corpus.name,
                "description": corpus.description,
            }

            if include_stats:
                # Check cache first
                cached = self._get_cached_stats(corpus.id)
                if cached:
                    corpus_info["document_count"] = cached["document_count"]
                    corpus_info["last_updated"] = cached["last_updated"]
                else:
                    # Get from corpus and cache
                    doc_count = corpus.document_count
                    last_updated = corpus.updated_at.isoformat()
                    corpus_info["document_count"] = doc_count
                    corpus_info["last_updated"] = last_updated
                    self._cache_stats(
                        corpus.id,
                        {"document_count": doc_count, "last_updated": last_updated},
                    )

            corpora_list.append(corpus_info)

        # Determine next cursor
        next_offset = offset + limit
        next_cursor = None
        if next_offset < total_count:
            next_cursor = self._encode_cursor(next_offset)

        return {
            "corpora": corpora_list,
            "total_count": total_count,
            "next_cursor": next_cursor,
        }


# Module-level instance for convenient access
list_corpora_tool = ListCorporaTool()
