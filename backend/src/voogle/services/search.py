# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Search service with corpus filtering, hybrid search, and RRF fusion.

Provides the SearchService class for performing semantic and hybrid searches
across the Voogle corpus with support for:
- Query embedding generation
- Corpus and content type filtering
- Date range filtering
- Hybrid search with dense and sparse vectors
- Reciprocal Rank Fusion (RRF) for combining multiple ranking signals
- Cursor-based pagination
- Latency tracking
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

from qdrant_client import models

from voogle import embedding as emb
from voogle import vector
from voogle.core.fragment import ContentType, LocationConfidence
from voogle.embedding.sparse import SparseEncoder, get_sparse_encoder
from voogle.vector_schema import VectorName

logger = logging.getLogger(__name__)


class SearchMode(str, Enum):
    """Search mode for query execution.

    DENSE: Use only dense vector embeddings (semantic search)
    SPARSE: Use only sparse vector embeddings (keyword/BM25-style)
    HYBRID: Combine dense and sparse results using RRF fusion
    """

    DENSE = "dense"
    SPARSE = "sparse"
    HYBRID = "hybrid"


@dataclass(frozen=True)
class SearchQuery:
    """Parameters for a search query.

    Attributes:
        query_text: The search query string.
        corpus_ids: Optional list of corpus IDs to filter by.
        content_types: Optional list of content types to filter by.
        date_from: Optional start date for date range filtering.
        date_to: Optional end date for date range filtering.
        mode: Search mode (dense, sparse, or hybrid).
        limit: Maximum number of results to return.
        cursor: Optional cursor for pagination (offset-based).
        collection_name: Optional collection name override.
    """

    query_text: str
    corpus_ids: Optional[list[str]] = None
    content_types: Optional[list[ContentType]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    mode: SearchMode = SearchMode.DENSE
    limit: int = 10
    cursor: Optional[str] = None
    collection_name: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate query parameters after initialization."""
        if not self.query_text or not self.query_text.strip():
            raise ValueError("query_text cannot be empty")
        if self.limit < 1:
            raise ValueError(f"limit must be >= 1, got {self.limit}")
        if self.limit > 100:
            raise ValueError(f"limit must be <= 100, got {self.limit}")
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from must be <= date_to")


@dataclass
class SearchResult:
    """A single search result with score and metadata.

    Attributes:
        id: Unique identifier of the fragment.
        score: Relevance score (0.0 to 1.0, higher is better).
        text: The text content of the fragment.
        source_id: Identifier of the source document.
        source_type: Content type of the source.
        start_time: Start time in seconds (for audio/video).
        end_time: End time in seconds (for audio/video).
        corpus_id: Corpus this result belongs to.
        metadata: Additional metadata fields.
        location_confidence: Confidence level for location availability.
            Clients should use this to gracefully degrade UI when
            location may be unavailable.
        fallback_url: Alternative URL if primary location is unavailable.
        archive_url: Archive.org URL for broken sources.
        last_known_good: ISO timestamp when location was last verified.
    """

    id: str
    score: float
    text: str
    source_id: str
    source_type: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    corpus_id: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    location_confidence: LocationConfidence = LocationConfidence.HIGH
    fallback_url: Optional[str] = None
    archive_url: Optional[str] = None
    last_known_good: Optional[str] = None


@dataclass
class SearchResponse:
    """Response from a search query.

    Attributes:
        results: List of search results.
        total_count: Total number of matching results (may be approximate).
        next_cursor: Cursor for fetching next page, None if no more results.
        latency_ms: Query latency in milliseconds.
        query: The original query that produced these results.
    """

    results: list[SearchResult]
    total_count: int
    next_cursor: Optional[str]
    latency_ms: float
    query: SearchQuery


class SearchService:
    """Service for executing semantic and hybrid searches.

    Provides methods for searching the Qdrant vector database with support
    for multiple filtering options and hybrid search with RRF fusion.

    Hybrid search combines dense embeddings (semantic) with sparse embeddings
    (keyword-based BM25/SPLADE) using Reciprocal Rank Fusion (RRF).
    """

    # RRF constant (k parameter) - higher values weight all ranks more equally
    RRF_K: int = 60

    def __init__(
        self,
        embeddings_provider: Optional[emb.EmbeddingsProvider] = None,
        qdrant_client: Optional[vector.qdrant_client.QdrantClient] = None,
        sparse_encoder: Optional[SparseEncoder] = None,
    ) -> None:
        """Initialize the search service.

        Args:
            embeddings_provider: Provider for generating query embeddings.
                If None, uses the default provider from settings.
            qdrant_client: Qdrant client for vector database operations.
                If None, uses the configured client from settings.
            sparse_encoder: Encoder for generating sparse vectors.
                If None, uses the default BM25 encoder.
        """
        self._embeddings_provider = embeddings_provider
        self._qdrant_client = qdrant_client
        self._sparse_encoder = sparse_encoder

    @property
    def embeddings_provider(self) -> emb.EmbeddingsProvider:
        """Get or lazily initialize the embeddings provider."""
        if self._embeddings_provider is None:
            self._embeddings_provider = emb.get_embeddings_provider()
        return self._embeddings_provider

    @property
    def qdrant_client(self) -> vector.qdrant_client.QdrantClient:
        """Get or lazily initialize the Qdrant client."""
        if self._qdrant_client is None:
            self._qdrant_client = vector.get_configured_client()
        return self._qdrant_client

    @property
    def sparse_encoder(self) -> SparseEncoder:
        """Get or lazily initialize the sparse encoder."""
        if self._sparse_encoder is None:
            self._sparse_encoder = get_sparse_encoder()
        return self._sparse_encoder

    def __str__(self) -> str:
        """Return string representation of the service."""
        return f"SearchService(provider={type(self._embeddings_provider).__name__})"

    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (
            f"SearchService("
            f"embeddings_provider={self._embeddings_provider!r}, "
            f"qdrant_client={self._qdrant_client!r}, "
            f"sparse_encoder={self._sparse_encoder!r})"
        )

    def search(self, query: SearchQuery) -> SearchResponse:
        """Execute a search query and return results.

        Args:
            query: The search query parameters.

        Returns:
            SearchResponse with results and metadata.
        """
        start_time = time.perf_counter()

        # Get collection name
        collection_name = query.collection_name or vector.get_collection_name(
            self.embeddings_provider.provider_name
        )

        # Build filters
        query_filter = self._build_filter(query)

        # Calculate offset from cursor
        offset = self._parse_cursor(query.cursor)

        # Execute search based on mode
        if query.mode == SearchMode.DENSE:
            results = self._search_dense(
                query.query_text,
                collection_name,
                query.limit,
                offset,
                query_filter,
            )
        elif query.mode == SearchMode.SPARSE:
            results = self._search_sparse(
                query.query_text,
                collection_name,
                query.limit,
                offset,
                query_filter,
            )
        else:  # HYBRID
            results = self._search_hybrid(
                query.query_text,
                collection_name,
                query.limit,
                offset,
                query_filter,
            )

        # Calculate latency
        latency_ms = (time.perf_counter() - start_time) * 1000

        # Generate next cursor
        next_cursor = None
        if len(results) == query.limit:
            next_cursor = str(offset + query.limit)

        logger.info(
            "search_completed",
            extra={
                "query_text": query.query_text[:50],
                "mode": query.mode.value,
                "results_count": len(results),
                "latency_ms": latency_ms,
                "collection": collection_name,
            },
        )

        return SearchResponse(
            results=results,
            total_count=len(results),  # Approximate, could query for exact count
            next_cursor=next_cursor,
            latency_ms=latency_ms,
            query=query,
        )

    def _build_filter(self, query: SearchQuery) -> Optional[models.Filter]:
        """Build Qdrant filter from query parameters.

        Args:
            query: Search query with filter parameters.

        Returns:
            Qdrant Filter object or None if no filters specified.
        """
        conditions: list[models.Condition] = []

        # Corpus filter
        if query.corpus_ids:
            conditions.append(
                models.FieldCondition(
                    key="corpus_id",
                    match=models.MatchAny(any=query.corpus_ids),
                )
            )

        # Content type filter
        if query.content_types:
            type_values = [ct.value for ct in query.content_types]
            conditions.append(
                models.FieldCondition(
                    key="source_type",
                    match=models.MatchAny(any=type_values),
                )
            )

        # Date range filter (using embedded_at field)
        if query.date_from:
            conditions.append(
                models.FieldCondition(
                    key="embedded_at",
                    range=models.DatetimeRange(
                        gte=query.date_from,
                    ),
                )
            )

        if query.date_to:
            conditions.append(
                models.FieldCondition(
                    key="embedded_at",
                    range=models.DatetimeRange(
                        lte=query.date_to,
                    ),
                )
            )

        if not conditions:
            return None

        return models.Filter(must=conditions)

    def _parse_cursor(self, cursor: Optional[str]) -> int:
        """Parse cursor string into offset value.

        Args:
            cursor: Cursor string (currently offset-based).

        Returns:
            Offset integer value.
        """
        if cursor is None:
            return 0

        try:
            offset = int(cursor)
            if offset < 0:
                return 0
            return offset
        except ValueError:
            return 0

    def _search_dense(
        self,
        query_text: str,
        collection_name: str,
        limit: int,
        offset: int,
        query_filter: Optional[models.Filter],
    ) -> list[SearchResult]:
        """Execute dense vector search.

        Args:
            query_text: Query text to embed.
            collection_name: Qdrant collection name.
            limit: Maximum results to return.
            offset: Offset for pagination.
            query_filter: Optional Qdrant filter.

        Returns:
            List of SearchResult objects.
        """
        # Generate query embedding
        query_embedding = emb.text2embedding(query_text, self.embeddings_provider)

        # Check if collection uses named vectors
        try:
            collection_info = self.qdrant_client.get_collection(collection_name)
            # Check for named vectors by looking at vectors_config type
            vectors_config = collection_info.config.params.vectors
            use_named_vectors = isinstance(vectors_config, dict)
        except Exception:
            use_named_vectors = False

        if use_named_vectors:
            # Use named vector query for multimodal collections
            results = self.qdrant_client.query_points(
                collection_name=collection_name,
                query=query_embedding[0].tolist(),
                using=VectorName.TEXT_DENSE.value,
                query_filter=query_filter,
                limit=limit,
                offset=offset,
            ).points
        else:
            # Use legacy single vector query
            results = self.qdrant_client.query_points(
                collection_name=collection_name,
                query=query_embedding[0].tolist(),
                query_filter=query_filter,
                limit=limit,
                offset=offset,
            ).points

        return self._convert_results(results)

    def _search_sparse(
        self,
        query_text: str,
        collection_name: str,
        limit: int,
        offset: int,
        query_filter: Optional[models.Filter],
    ) -> list[SearchResult]:
        """Execute sparse vector search using BM25/SPLADE.

        Sparse search provides keyword-based matching that complements
        dense semantic search.

        Args:
            query_text: Query text.
            collection_name: Qdrant collection name.
            limit: Maximum results to return.
            offset: Offset for pagination.
            query_filter: Optional Qdrant filter.

        Returns:
            List of SearchResult objects.
        """
        # Check if sparse vectors are available
        try:
            collection_info = self.qdrant_client.get_collection(collection_name)
            has_sparse = (
                collection_info.config.params.sparse_vectors is not None
                and VectorName.TEXT_SPARSE.value
                in collection_info.config.params.sparse_vectors
            )
        except Exception:
            has_sparse = False

        if not has_sparse:
            logger.warning(
                f"Sparse vectors not configured for {collection_name}, "
                "falling back to dense search"
            )
            return self._search_dense(
                query_text, collection_name, limit, offset, query_filter
            )

        # Generate sparse embedding
        sparse_vector = self.sparse_encoder.encode(query_text)

        if not sparse_vector.indices:
            logger.warning("Empty sparse vector, falling back to dense search")
            return self._search_dense(
                query_text, collection_name, limit, offset, query_filter
            )

        # Execute sparse vector search
        results = self.qdrant_client.query_points(
            collection_name=collection_name,
            query=models.SparseVector(
                indices=sparse_vector.indices,
                values=sparse_vector.values,
            ),
            using=VectorName.TEXT_SPARSE.value,
            query_filter=query_filter,
            limit=limit,
            offset=offset,
        ).points

        return self._convert_results(results)

    def _search_hybrid(
        self,
        query_text: str,
        collection_name: str,
        limit: int,
        offset: int,
        query_filter: Optional[models.Filter],
    ) -> list[SearchResult]:
        """Execute hybrid search with RRF fusion using prefetch pattern.

        Combines dense and sparse search results using Reciprocal Rank Fusion.
        Uses Qdrant's prefetch mechanism for efficient hybrid search when
        sparse vectors are available, otherwise falls back to separate queries.

        Args:
            query_text: Query text.
            collection_name: Qdrant collection name.
            limit: Maximum results to return.
            offset: Offset for pagination.
            query_filter: Optional Qdrant filter.

        Returns:
            List of SearchResult objects fused with RRF.
        """
        # Check if sparse vectors are available for prefetch optimization
        try:
            collection_info = self.qdrant_client.get_collection(collection_name)
            vectors_config = collection_info.config.params.vectors
            use_named_vectors = isinstance(vectors_config, dict)
            has_sparse = (
                collection_info.config.params.sparse_vectors is not None
                and VectorName.TEXT_SPARSE.value
                in collection_info.config.params.sparse_vectors
            )
        except Exception:
            use_named_vectors = False
            has_sparse = False

        # If we have named vectors and sparse support, use optimized prefetch
        if use_named_vectors and has_sparse:
            return self._search_hybrid_prefetch(
                query_text, collection_name, limit, offset, query_filter
            )

        # Fallback: separate queries with manual RRF fusion
        fetch_limit = min(limit * 3, 100)

        dense_results = self._search_dense(
            query_text, collection_name, fetch_limit, 0, query_filter
        )
        sparse_results = self._search_sparse(
            query_text, collection_name, fetch_limit, 0, query_filter
        )

        # Apply RRF fusion
        fused_results = self._rrf_fusion(dense_results, sparse_results)

        # Apply pagination
        start_idx = offset
        end_idx = offset + limit

        return fused_results[start_idx:end_idx]

    def _search_hybrid_prefetch(
        self,
        query_text: str,
        collection_name: str,
        limit: int,
        offset: int,
        query_filter: Optional[models.Filter],
    ) -> list[SearchResult]:
        """Execute hybrid search using Qdrant's prefetch pattern.

        Uses Qdrant's native prefetch mechanism to efficiently combine
        dense and sparse results with RRF fusion in a single query.

        Args:
            query_text: Query text.
            collection_name: Qdrant collection name.
            limit: Maximum results to return.
            offset: Offset for pagination.
            query_filter: Optional Qdrant filter.

        Returns:
            List of SearchResult objects.
        """
        # Generate embeddings
        query_embedding = emb.text2embedding(query_text, self.embeddings_provider)
        sparse_vector = self.sparse_encoder.encode(query_text)

        # If sparse vector is empty, fall back to dense-only search
        if not sparse_vector.indices:
            logger.warning("Empty sparse vector in hybrid search, using dense only")
            return self._search_dense(
                query_text, collection_name, limit, offset, query_filter
            )

        # Prefetch limit should be higher than final limit for better fusion
        prefetch_limit = min(limit * 3, 100)

        # Use Qdrant's query with prefetch for optimized hybrid search
        # The prefetch pattern fetches candidates from multiple vectors
        # and fuses them using RRF
        results = self.qdrant_client.query_points(
            collection_name=collection_name,
            prefetch=[
                # Dense vector prefetch
                models.Prefetch(
                    query=query_embedding[0].tolist(),
                    using=VectorName.TEXT_DENSE.value,
                    limit=prefetch_limit,
                ),
                # Sparse vector prefetch
                models.Prefetch(
                    query=models.SparseVector(
                        indices=sparse_vector.indices,
                        values=sparse_vector.values,
                    ),
                    using=VectorName.TEXT_SPARSE.value,
                    limit=prefetch_limit,
                ),
            ],
            # Final query uses RRF fusion
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            query_filter=query_filter,
            limit=limit,
            offset=offset,
        ).points

        return self._convert_results(results)

    def _rrf_fusion(
        self,
        dense_results: list[SearchResult],
        sparse_results: list[SearchResult],
    ) -> list[SearchResult]:
        """Combine ranked results using Reciprocal Rank Fusion.

        RRF score = sum(1 / (k + rank_i)) for each ranking

        Args:
            dense_results: Results from dense vector search.
            sparse_results: Results from sparse vector search.

        Returns:
            Combined and re-ranked results.
        """
        # Build RRF scores
        rrf_scores: dict[str, float] = {}
        result_map: dict[str, SearchResult] = {}

        # Add dense results
        for rank, result in enumerate(dense_results):
            rrf_score = 1.0 / (self.RRF_K + rank + 1)
            rrf_scores[result.id] = rrf_scores.get(result.id, 0) + rrf_score
            result_map[result.id] = result

        # Add sparse results
        for rank, result in enumerate(sparse_results):
            rrf_score = 1.0 / (self.RRF_K + rank + 1)
            rrf_scores[result.id] = rrf_scores.get(result.id, 0) + rrf_score
            if result.id not in result_map:
                result_map[result.id] = result

        # Sort by RRF score
        sorted_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)

        # Build result list with updated scores
        fused_results = []
        for result_id in sorted_ids:
            original = result_map[result_id]
            # Create new result with RRF score
            fused_results.append(
                SearchResult(
                    id=original.id,
                    score=rrf_scores[result_id],
                    text=original.text,
                    source_id=original.source_id,
                    source_type=original.source_type,
                    start_time=original.start_time,
                    end_time=original.end_time,
                    corpus_id=original.corpus_id,
                    metadata=original.metadata,
                    location_confidence=original.location_confidence,
                    fallback_url=original.fallback_url,
                    archive_url=original.archive_url,
                    last_known_good=original.last_known_good,
                )
            )

        return fused_results

    def _convert_results(
        self, points: list[models.ScoredPoint]
    ) -> list[SearchResult]:
        """Convert Qdrant scored points to SearchResult objects.

        Args:
            points: List of Qdrant scored points.

        Returns:
            List of SearchResult objects.
        """
        results = []
        for point in points:
            payload = point.payload or {}

            # Extract fields with backward compatibility for legacy schema
            source_id = str(payload.get("source_id") or payload.get("episode", ""))
            text = str(payload.get("text", ""))

            # Handle both new and legacy time fields
            start_time = payload.get("start_time") or payload.get("start_secs")
            end_time = payload.get("end_time") or payload.get("end_secs")

            # Extract graceful degradation fields
            location_confidence_str = payload.get("location_confidence", "high")
            try:
                location_confidence = LocationConfidence(location_confidence_str)
            except ValueError:
                location_confidence = LocationConfidence.HIGH

            results.append(
                SearchResult(
                    id=str(point.id),
                    score=point.score,
                    text=text,
                    source_id=source_id,
                    source_type=payload.get("source_type"),
                    start_time=float(start_time) if start_time is not None else None,
                    end_time=float(end_time) if end_time is not None else None,
                    corpus_id=payload.get("corpus_id"),
                    metadata={
                        k: v
                        for k, v in payload.items()
                        if k
                        not in {
                            "source_id",
                            "episode",
                            "text",
                            "start_time",
                            "start_secs",
                            "end_time",
                            "end_secs",
                            "source_type",
                            "corpus_id",
                            "location_confidence",
                            "fallback_url",
                            "archive_url",
                            "last_known_good",
                        }
                    },
                    location_confidence=location_confidence,
                    fallback_url=payload.get("fallback_url"),
                    archive_url=payload.get("archive_url"),
                    last_known_good=payload.get("last_known_good"),
                )
            )

        return results
