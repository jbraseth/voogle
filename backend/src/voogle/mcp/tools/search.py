# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""MCP search tool for semantic fragment retrieval.

Provides the primary MCP search tool for performing semantic searches
across Voogle's indexed content with filtering, pagination, and
latency tracking.
"""
from dataclasses import dataclass, field
from typing import Any, Optional

from voogle.services.search import SearchMode, SearchQuery, SearchService


@dataclass
class SearchFilters:
    """Filters for narrowing search results.

    Attributes:
        content_types: Optional list of content types to include
            (e.g., ["audio", "video", "document"]).
        date_from: Optional ISO date string for start of date range.
        date_to: Optional ISO date string for end of date range.
    """

    content_types: Optional[list[str]] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None


@dataclass
class SearchResultItem:
    """A single search result with relevance score and metadata.

    Attributes:
        id: Unique identifier of the fragment.
        score: Relevance score (0.0 to 1.0, higher is better).
        snippet: Text content of the fragment.
        uri: URI or deep link to the source content.
        metadata: Additional metadata about the source.
    """

    id: str
    score: float
    snippet: str
    uri: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchToolOutput:
    """Output from the search tool.

    Attributes:
        results: List of search results ranked by relevance.
        total_count: Total number of matching results.
        next_cursor: Cursor for fetching the next page of results.
            None if no more results are available.
        latency_ms: Query execution time in milliseconds.
    """

    results: list[SearchResultItem]
    total_count: int
    next_cursor: Optional[str]
    latency_ms: float


@dataclass
class SearchToolInput:
    """Input schema for the MCP search tool.

    Attributes:
        query: The semantic search query string.
        corpus_ids: Optional list of corpus IDs to search within.
            If not specified, searches all available corpora.
        limit: Maximum number of results to return (1-100, default 10).
        min_score: Minimum relevance score threshold (0.0-1.0).
            Results below this score are filtered out.
        filters: Optional filters for content type and date range.
        cursor: Optional pagination cursor from a previous search.
    """

    query: str
    corpus_ids: Optional[list[str]] = None
    limit: int = 10
    min_score: float = 0.0
    filters: Optional[SearchFilters] = None
    cursor: Optional[str] = None


class SearchTool:
    """MCP tool for semantic fragment retrieval.

    Provides semantic search capabilities over Voogle's indexed content
    with support for:
    - Multi-corpus search with filtering
    - Relevance score thresholds
    - Content type and date filtering
    - Cursor-based pagination
    - Query latency tracking
    """

    name: str = "search"
    description: str = (
        "Search for semantically relevant content fragments across indexed corpora. "
        "Returns ranked results with relevance scores, snippets, and source metadata."
    )

    def __init__(self, search_service: Optional[SearchService] = None) -> None:
        """Initialize the search tool.

        Args:
            search_service: Optional SearchService instance for executing queries.
                If None, creates a new service with default configuration.
        """
        self._search_service = search_service

    @property
    def search_service(self) -> SearchService:
        """Get or lazily initialize the search service."""
        if self._search_service is None:
            self._search_service = SearchService()
        return self._search_service

    @property
    def input_schema(self) -> dict[str, Any]:
        """Return the JSON schema for tool input parameters.

        Returns:
            JSON Schema dictionary describing the input format.
        """
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The semantic search query string",
                    "minLength": 1,
                },
                "corpus_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional list of corpus IDs to search within",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results (1-100)",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 10,
                },
                "min_score": {
                    "type": "number",
                    "description": "Minimum relevance score threshold (0.0-1.0)",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.0,
                },
                "filters": {
                    "type": "object",
                    "properties": {
                        "content_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Content types to include (audio, video, document, etc.)",
                        },
                        "date_from": {
                            "type": "string",
                            "format": "date",
                            "description": "Start of date range (ISO format)",
                        },
                        "date_to": {
                            "type": "string",
                            "format": "date",
                            "description": "End of date range (ISO format)",
                        },
                    },
                    "description": "Optional filters for narrowing results",
                },
                "cursor": {
                    "type": "string",
                    "description": "Pagination cursor from previous search",
                },
            },
            "required": ["query"],
        }

    def __call__(
        self,
        query: str,
        corpus_ids: Optional[list[str]] = None,
        limit: int = 10,
        min_score: float = 0.0,
        filters: Optional[dict[str, Any]] = None,
        cursor: Optional[str] = None,
    ) -> dict[str, Any]:
        """Execute a semantic search query.

        Args:
            query: The semantic search query string.
            corpus_ids: Optional list of corpus IDs to search within.
            limit: Maximum number of results to return (1-100).
            min_score: Minimum relevance score threshold (0.0-1.0).
            filters: Optional filters dict with content_types, date_from, date_to.
            cursor: Optional pagination cursor from previous search.

        Returns:
            Dictionary containing search results, pagination info, and latency.

        Raises:
            ValueError: If query is empty or parameters are invalid.
        """
        # Validate inputs
        if not query or not query.strip():
            raise ValueError("query cannot be empty")
        if limit < 1 or limit > 100:
            raise ValueError(f"limit must be between 1 and 100, got {limit}")
        if min_score < 0.0 or min_score > 1.0:
            raise ValueError(f"min_score must be between 0.0 and 1.0, got {min_score}")

        # Parse filters
        content_types = None
        date_from = None
        date_to = None

        if filters:
            from datetime import datetime

            from voogle.core.fragment import ContentType

            # Parse content types
            if filters.get("content_types"):
                content_types = []
                for ct in filters["content_types"]:
                    try:
                        content_types.append(ContentType(ct))
                    except ValueError:
                        pass  # Ignore invalid content types

            # Parse dates
            if filters.get("date_from"):
                try:
                    date_from = datetime.fromisoformat(filters["date_from"])
                except ValueError:
                    pass  # Ignore invalid dates

            if filters.get("date_to"):
                try:
                    date_to = datetime.fromisoformat(filters["date_to"])
                except ValueError:
                    pass  # Ignore invalid dates

        # Build search query
        search_query = SearchQuery(
            query_text=query.strip(),
            corpus_ids=corpus_ids,
            content_types=content_types,
            date_from=date_from,
            date_to=date_to,
            mode=SearchMode.DENSE,
            limit=limit,
            cursor=cursor,
        )

        # Execute search
        response = self.search_service.search(search_query)

        # Filter by min_score and convert results
        results = []
        for result in response.results:
            if result.score >= min_score:
                # Build URI from source info
                uri = None
                if result.start_time is not None:
                    uri = f"voogle://{result.source_id}?t={int(result.start_time)}"
                elif result.source_id:
                    uri = f"voogle://{result.source_id}"

                results.append(
                    {
                        "id": result.id,
                        "score": result.score,
                        "snippet": result.text,
                        "uri": uri,
                        "metadata": {
                            "source_id": result.source_id,
                            "source_type": result.source_type,
                            "start_time": result.start_time,
                            "end_time": result.end_time,
                            "corpus_id": result.corpus_id,
                            **result.metadata,
                        },
                    }
                )

        return {
            "results": results,
            "total_count": len(results),
            "next_cursor": response.next_cursor if len(results) == limit else None,
            "latency_ms": response.latency_ms,
        }


# Module-level instance for convenient access
search_tool = SearchTool()
