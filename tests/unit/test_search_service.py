# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for SearchService and related dataclasses."""
from datetime import datetime
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from voogle.core.fragment import ContentType
from voogle.services.search import (
    SearchMode,
    SearchQuery,
    SearchResponse,
    SearchResult,
    SearchService,
)

pytestmark = pytest.mark.unit


class TestSearchQuery:
    """Tests for SearchQuery dataclass."""

    @pytest.mark.description("SearchQuery with valid query_text creates successfully")
    def test_create_with_query_text(self) -> None:
        query = SearchQuery(query_text="test query")
        assert query.query_text == "test query"
        assert query.corpus_ids is None
        assert query.content_types is None
        assert query.date_from is None
        assert query.date_to is None
        assert query.mode == SearchMode.DENSE
        assert query.limit == 10
        assert query.cursor is None
        assert query.collection_name is None

    @pytest.mark.description("SearchQuery with all parameters creates successfully")
    def test_create_with_all_parameters(self) -> None:
        now = datetime.now()
        query = SearchQuery(
            query_text="semantic search",
            corpus_ids=["corpus1", "corpus2"],
            content_types=[ContentType.AUDIO, ContentType.VIDEO],
            date_from=now,
            date_to=now,
            mode=SearchMode.HYBRID,
            limit=20,
            cursor="10",
            collection_name="custom_collection",
        )
        assert query.query_text == "semantic search"
        assert query.corpus_ids == ["corpus1", "corpus2"]
        assert query.content_types == [ContentType.AUDIO, ContentType.VIDEO]
        assert query.date_from == now
        assert query.date_to == now
        assert query.mode == SearchMode.HYBRID
        assert query.limit == 20
        assert query.cursor == "10"
        assert query.collection_name == "custom_collection"

    @pytest.mark.description("SearchQuery with empty query_text raises ValueError")
    def test_empty_query_text_raises(self) -> None:
        with pytest.raises(ValueError, match="query_text cannot be empty"):
            SearchQuery(query_text="")

    @pytest.mark.description("SearchQuery with whitespace query_text raises ValueError")
    def test_whitespace_query_text_raises(self) -> None:
        with pytest.raises(ValueError, match="query_text cannot be empty"):
            SearchQuery(query_text="   ")

    @pytest.mark.description("SearchQuery with limit < 1 raises ValueError")
    def test_limit_too_low_raises(self) -> None:
        with pytest.raises(ValueError, match="limit must be >= 1"):
            SearchQuery(query_text="test", limit=0)

    @pytest.mark.description("SearchQuery with limit > 100 raises ValueError")
    def test_limit_too_high_raises(self) -> None:
        with pytest.raises(ValueError, match="limit must be <= 100"):
            SearchQuery(query_text="test", limit=101)

    @pytest.mark.description("SearchQuery with date_from > date_to raises ValueError")
    def test_invalid_date_range_raises(self) -> None:
        with pytest.raises(ValueError, match="date_from must be <= date_to"):
            SearchQuery(
                query_text="test",
                date_from=datetime(2025, 1, 2),
                date_to=datetime(2025, 1, 1),
            )


class TestSearchResult:
    """Tests for SearchResult dataclass."""

    @pytest.mark.description("SearchResult with required fields creates successfully")
    def test_create_with_required_fields(self) -> None:
        result = SearchResult(
            id="result-1",
            score=0.95,
            text="This is a test fragment",
            source_id="episode-123",
        )
        assert result.id == "result-1"
        assert result.score == 0.95
        assert result.text == "This is a test fragment"
        assert result.source_id == "episode-123"
        assert result.source_type is None
        assert result.start_time is None
        assert result.end_time is None
        assert result.corpus_id is None
        assert result.metadata == {}

    @pytest.mark.description("SearchResult with all fields creates successfully")
    def test_create_with_all_fields(self) -> None:
        result = SearchResult(
            id="result-2",
            score=0.87,
            text="Audio fragment",
            source_id="episode-456",
            source_type="audio",
            start_time=120.5,
            end_time=140.0,
            corpus_id="podcast-corpus",
            metadata={"channel": "Tech Talk", "duration": 19.5},
        )
        assert result.id == "result-2"
        assert result.score == 0.87
        assert result.text == "Audio fragment"
        assert result.source_id == "episode-456"
        assert result.source_type == "audio"
        assert result.start_time == 120.5
        assert result.end_time == 140.0
        assert result.corpus_id == "podcast-corpus"
        assert result.metadata == {"channel": "Tech Talk", "duration": 19.5}


class TestSearchResponse:
    """Tests for SearchResponse dataclass."""

    @pytest.mark.description("SearchResponse contains query metadata")
    def test_response_structure(self) -> None:
        query = SearchQuery(query_text="test")
        results = [
            SearchResult(id="1", score=0.9, text="result 1", source_id="src-1"),
            SearchResult(id="2", score=0.8, text="result 2", source_id="src-2"),
        ]
        response = SearchResponse(
            results=results,
            total_count=2,
            next_cursor="10",
            latency_ms=45.5,
            query=query,
        )
        assert len(response.results) == 2
        assert response.total_count == 2
        assert response.next_cursor == "10"
        assert response.latency_ms == 45.5
        assert response.query == query


class TestSearchMode:
    """Tests for SearchMode enum."""

    @pytest.mark.description("SearchMode has three modes")
    def test_search_modes(self) -> None:
        assert SearchMode.DENSE.value == "dense"
        assert SearchMode.SPARSE.value == "sparse"
        assert SearchMode.HYBRID.value == "hybrid"


class TestSearchService:
    """Tests for SearchService class."""

    @pytest.mark.description("SearchService initializes with default providers")
    def test_init_default(self) -> None:
        service = SearchService()
        assert service._embeddings_provider is None
        assert service._qdrant_client is None

    @pytest.mark.description("SearchService initializes with custom providers")
    def test_init_custom_providers(self) -> None:
        mock_provider = MagicMock()
        mock_client = MagicMock()
        service = SearchService(
            embeddings_provider=mock_provider,
            qdrant_client=mock_client,
        )
        assert service._embeddings_provider == mock_provider
        assert service._qdrant_client == mock_client

    @pytest.mark.description("SearchService __str__ returns string representation")
    def test_str(self) -> None:
        service = SearchService()
        result = str(service)
        assert "SearchService" in result

    @pytest.mark.description("SearchService __repr__ returns detailed representation")
    def test_repr(self) -> None:
        service = SearchService()
        result = repr(service)
        assert "SearchService" in result
        assert "embeddings_provider" in result
        assert "qdrant_client" in result

    @pytest.mark.description("SearchService builds filter for corpus_ids")
    def test_build_filter_corpus_ids(self) -> None:
        service = SearchService()
        query = SearchQuery(
            query_text="test",
            corpus_ids=["corpus1", "corpus2"],
        )
        filter_obj = service._build_filter(query)
        assert filter_obj is not None
        assert len(filter_obj.must) == 1
        condition = filter_obj.must[0]
        assert condition.key == "corpus_id"

    @pytest.mark.description("SearchService builds filter for content_types")
    def test_build_filter_content_types(self) -> None:
        service = SearchService()
        query = SearchQuery(
            query_text="test",
            content_types=[ContentType.AUDIO, ContentType.VIDEO],
        )
        filter_obj = service._build_filter(query)
        assert filter_obj is not None
        assert len(filter_obj.must) == 1
        condition = filter_obj.must[0]
        assert condition.key == "source_type"

    @pytest.mark.description("SearchService builds filter for date range")
    def test_build_filter_date_range(self) -> None:
        service = SearchService()
        date_from = datetime(2025, 1, 1)
        date_to = datetime(2025, 12, 31)
        query = SearchQuery(
            query_text="test",
            date_from=date_from,
            date_to=date_to,
        )
        filter_obj = service._build_filter(query)
        assert filter_obj is not None
        assert len(filter_obj.must) == 2

    @pytest.mark.description("SearchService builds combined filter")
    def test_build_filter_combined(self) -> None:
        service = SearchService()
        query = SearchQuery(
            query_text="test",
            corpus_ids=["corpus1"],
            content_types=[ContentType.AUDIO],
            date_from=datetime(2025, 1, 1),
        )
        filter_obj = service._build_filter(query)
        assert filter_obj is not None
        assert len(filter_obj.must) == 3

    @pytest.mark.description("SearchService returns None filter when no filters specified")
    def test_build_filter_empty(self) -> None:
        service = SearchService()
        query = SearchQuery(query_text="test")
        filter_obj = service._build_filter(query)
        assert filter_obj is None

    @pytest.mark.description("SearchService parses cursor correctly")
    def test_parse_cursor_valid(self) -> None:
        service = SearchService()
        assert service._parse_cursor("10") == 10
        assert service._parse_cursor("0") == 0
        assert service._parse_cursor("100") == 100

    @pytest.mark.description("SearchService parses None cursor as 0")
    def test_parse_cursor_none(self) -> None:
        service = SearchService()
        assert service._parse_cursor(None) == 0

    @pytest.mark.description("SearchService parses invalid cursor as 0")
    def test_parse_cursor_invalid(self) -> None:
        service = SearchService()
        assert service._parse_cursor("invalid") == 0
        assert service._parse_cursor("-5") == 0

    @pytest.mark.description("SearchService RRF fusion combines results correctly")
    def test_rrf_fusion(self) -> None:
        service = SearchService()

        dense_results = [
            SearchResult(id="a", score=0.9, text="A", source_id="1"),
            SearchResult(id="b", score=0.8, text="B", source_id="2"),
            SearchResult(id="c", score=0.7, text="C", source_id="3"),
        ]
        sparse_results = [
            SearchResult(id="b", score=0.95, text="B", source_id="2"),
            SearchResult(id="d", score=0.85, text="D", source_id="4"),
            SearchResult(id="a", score=0.75, text="A", source_id="1"),
        ]

        fused = service._rrf_fusion(dense_results, sparse_results)

        # Both 'a' and 'b' appear in both lists, should have higher scores
        ids = [r.id for r in fused]
        # 'a' appears at rank 0 in dense and rank 2 in sparse
        # 'b' appears at rank 1 in dense and rank 0 in sparse
        # Both should be near the top
        assert "a" in ids[:3]
        assert "b" in ids[:3]
        # All 4 unique results should be present
        assert len(fused) == 4
        assert set(ids) == {"a", "b", "c", "d"}

    @pytest.mark.description("SearchService RRF fusion with empty results")
    def test_rrf_fusion_empty(self) -> None:
        service = SearchService()
        fused = service._rrf_fusion([], [])
        assert fused == []

    @pytest.mark.description("SearchService RRF fusion with one empty list")
    def test_rrf_fusion_one_empty(self) -> None:
        service = SearchService()
        dense_results = [
            SearchResult(id="a", score=0.9, text="A", source_id="1"),
        ]
        fused = service._rrf_fusion(dense_results, [])
        assert len(fused) == 1
        assert fused[0].id == "a"

    @pytest.mark.description("SearchService converts Qdrant points to SearchResult")
    def test_convert_results(self) -> None:
        service = SearchService()

        mock_points = [
            MagicMock(
                id="point-1",
                score=0.95,
                payload={
                    "text": "Fragment text",
                    "episode": 123,
                    "start_secs": 10.5,
                    "end_secs": 25.0,
                    "channel": "Test Channel",
                },
            ),
        ]

        results = service._convert_results(mock_points)

        assert len(results) == 1
        result = results[0]
        assert result.id == "point-1"
        assert result.score == 0.95
        assert result.text == "Fragment text"
        assert result.source_id == "123"
        assert result.start_time == 10.5
        assert result.end_time == 25.0
        assert "channel" in result.metadata

    @pytest.mark.description("SearchService converts results with new schema fields")
    def test_convert_results_new_schema(self) -> None:
        service = SearchService()

        mock_points = [
            MagicMock(
                id="point-2",
                score=0.88,
                payload={
                    "text": "New schema fragment",
                    "source_id": "doc-456",
                    "source_type": "audio",
                    "start_time": 30.0,
                    "end_time": 45.0,
                    "corpus_id": "my-corpus",
                },
            ),
        ]

        results = service._convert_results(mock_points)

        assert len(results) == 1
        result = results[0]
        assert result.id == "point-2"
        assert result.source_id == "doc-456"
        assert result.source_type == "audio"
        assert result.start_time == 30.0
        assert result.end_time == 45.0
        assert result.corpus_id == "my-corpus"

    @pytest.mark.description("SearchService handles empty payload")
    def test_convert_results_empty_payload(self) -> None:
        service = SearchService()

        mock_points = [
            MagicMock(
                id="point-3",
                score=0.5,
                payload=None,
            ),
        ]

        results = service._convert_results(mock_points)

        assert len(results) == 1
        result = results[0]
        assert result.id == "point-3"
        assert result.text == ""
        assert result.source_id == ""


class TestSearchServiceIntegration:
    """Integration tests for SearchService with mocked dependencies."""

    @pytest.mark.description("SearchService search returns response with latency")
    def test_search_returns_response_with_latency(self) -> None:
        # Setup mocks
        mock_provider = MagicMock()
        mock_provider.provider_name = "local"
        mock_provider.encode_single = MagicMock(
            return_value=np.array([[0.1] * 384])
        )

        mock_client = MagicMock()
        mock_client.get_collection.return_value = MagicMock(
            config=MagicMock(
                params=MagicMock(
                    vectors=MagicMock(),  # Not a dict, so not named vectors
                    sparse_vectors=None,
                )
            )
        )
        mock_client.query_points.return_value = MagicMock(
            points=[
                MagicMock(
                    id="result-1",
                    score=0.9,
                    payload={"text": "Result text", "episode": 1},
                ),
            ]
        )

        service = SearchService(
            embeddings_provider=mock_provider,
            qdrant_client=mock_client,
        )

        # Patch text2embedding to use our mock
        with patch("voogle.services.search.emb.text2embedding") as mock_embed:
            mock_embed.return_value = np.array([[0.1] * 384])

            query = SearchQuery(query_text="test query")
            response = service.search(query)

        assert isinstance(response, SearchResponse)
        assert response.latency_ms > 0
        assert len(response.results) == 1
        assert response.query == query

    @pytest.mark.description("SearchService search with pagination returns cursor")
    def test_search_pagination(self) -> None:
        mock_provider = MagicMock()
        mock_provider.provider_name = "local"

        # Return exactly 'limit' results to trigger next_cursor
        mock_client = MagicMock()
        mock_client.get_collection.return_value = MagicMock(
            config=MagicMock(
                params=MagicMock(
                    vectors=MagicMock(),
                    sparse_vectors=None,
                )
            )
        )
        mock_client.query_points.return_value = MagicMock(
            points=[
                MagicMock(id=f"result-{i}", score=0.9 - i * 0.1, payload={"text": f"Text {i}", "episode": i})
                for i in range(5)
            ]
        )

        service = SearchService(
            embeddings_provider=mock_provider,
            qdrant_client=mock_client,
        )

        with patch("voogle.services.search.emb.text2embedding") as mock_embed:
            mock_embed.return_value = np.array([[0.1] * 384])

            query = SearchQuery(query_text="test", limit=5)
            response = service.search(query)

        assert response.next_cursor == "5"
        assert len(response.results) == 5
