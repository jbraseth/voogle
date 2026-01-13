# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for MCP search tool."""
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from voogle.mcp.tools.search import (
    SearchFilters,
    SearchResultItem,
    SearchTool,
    SearchToolInput,
    SearchToolOutput,
    search_tool,
)
from voogle.services.search import SearchResponse, SearchResult

pytestmark = pytest.mark.unit


class TestSearchFilters:
    """Tests for SearchFilters dataclass."""

    @pytest.mark.description("SearchFilters has default None values")
    def test_default_values(self) -> None:
        filters = SearchFilters()
        assert filters.content_types is None
        assert filters.date_from is None
        assert filters.date_to is None

    @pytest.mark.description("SearchFilters accepts all parameters")
    def test_with_all_parameters(self) -> None:
        filters = SearchFilters(
            content_types=["audio", "video"],
            date_from="2025-01-01",
            date_to="2025-12-31",
        )
        assert filters.content_types == ["audio", "video"]
        assert filters.date_from == "2025-01-01"
        assert filters.date_to == "2025-12-31"


class TestSearchResultItem:
    """Tests for SearchResultItem dataclass."""

    @pytest.mark.description("SearchResultItem with required fields")
    def test_required_fields(self) -> None:
        item = SearchResultItem(
            id="result-1",
            score=0.95,
            snippet="Test snippet",
        )
        assert item.id == "result-1"
        assert item.score == 0.95
        assert item.snippet == "Test snippet"
        assert item.uri is None
        assert item.metadata == {}

    @pytest.mark.description("SearchResultItem with all fields")
    def test_all_fields(self) -> None:
        item = SearchResultItem(
            id="result-2",
            score=0.87,
            snippet="Full snippet",
            uri="voogle://episode-123?t=45",
            metadata={"source_type": "audio", "channel": "Test"},
        )
        assert item.id == "result-2"
        assert item.score == 0.87
        assert item.snippet == "Full snippet"
        assert item.uri == "voogle://episode-123?t=45"
        assert item.metadata == {"source_type": "audio", "channel": "Test"}


class TestSearchToolInput:
    """Tests for SearchToolInput dataclass."""

    @pytest.mark.description("SearchToolInput with query only")
    def test_query_only(self) -> None:
        input_data = SearchToolInput(query="semantic search")
        assert input_data.query == "semantic search"
        assert input_data.corpus_ids is None
        assert input_data.limit == 10
        assert input_data.min_score == 0.0
        assert input_data.filters is None
        assert input_data.cursor is None

    @pytest.mark.description("SearchToolInput with all parameters")
    def test_all_parameters(self) -> None:
        filters = SearchFilters(content_types=["audio"])
        input_data = SearchToolInput(
            query="test query",
            corpus_ids=["corpus1", "corpus2"],
            limit=20,
            min_score=0.5,
            filters=filters,
            cursor="10",
        )
        assert input_data.query == "test query"
        assert input_data.corpus_ids == ["corpus1", "corpus2"]
        assert input_data.limit == 20
        assert input_data.min_score == 0.5
        assert input_data.filters == filters
        assert input_data.cursor == "10"


class TestSearchToolOutput:
    """Tests for SearchToolOutput dataclass."""

    @pytest.mark.description("SearchToolOutput structure")
    def test_output_structure(self) -> None:
        results = [
            SearchResultItem(id="1", score=0.9, snippet="Result 1"),
            SearchResultItem(id="2", score=0.8, snippet="Result 2"),
        ]
        output = SearchToolOutput(
            results=results,
            total_count=2,
            next_cursor="10",
            latency_ms=45.5,
        )
        assert len(output.results) == 2
        assert output.total_count == 2
        assert output.next_cursor == "10"
        assert output.latency_ms == 45.5


class TestSearchTool:
    """Tests for SearchTool class."""

    @pytest.mark.description("SearchTool has correct name and description")
    def test_name_and_description(self) -> None:
        tool = SearchTool()
        assert tool.name == "search"
        assert "semantic" in tool.description.lower()
        assert "search" in tool.description.lower()

    @pytest.mark.description("SearchTool input_schema is valid JSON Schema")
    def test_input_schema_structure(self) -> None:
        tool = SearchTool()
        schema = tool.input_schema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema
        assert "query" in schema["required"]

    @pytest.mark.description("SearchTool input_schema has query property")
    def test_input_schema_query(self) -> None:
        tool = SearchTool()
        schema = tool.input_schema
        query_prop = schema["properties"]["query"]
        assert query_prop["type"] == "string"
        assert query_prop["minLength"] == 1

    @pytest.mark.description("SearchTool input_schema has corpus_ids property")
    def test_input_schema_corpus_ids(self) -> None:
        tool = SearchTool()
        schema = tool.input_schema
        corpus_ids_prop = schema["properties"]["corpus_ids"]
        assert corpus_ids_prop["type"] == "array"
        assert corpus_ids_prop["items"]["type"] == "string"

    @pytest.mark.description("SearchTool input_schema has limit property")
    def test_input_schema_limit(self) -> None:
        tool = SearchTool()
        schema = tool.input_schema
        limit_prop = schema["properties"]["limit"]
        assert limit_prop["type"] == "integer"
        assert limit_prop["minimum"] == 1
        assert limit_prop["maximum"] == 100
        assert limit_prop["default"] == 10

    @pytest.mark.description("SearchTool input_schema has min_score property")
    def test_input_schema_min_score(self) -> None:
        tool = SearchTool()
        schema = tool.input_schema
        min_score_prop = schema["properties"]["min_score"]
        assert min_score_prop["type"] == "number"
        assert min_score_prop["minimum"] == 0.0
        assert min_score_prop["maximum"] == 1.0

    @pytest.mark.description("SearchTool input_schema has filters property")
    def test_input_schema_filters(self) -> None:
        tool = SearchTool()
        schema = tool.input_schema
        filters_prop = schema["properties"]["filters"]
        assert filters_prop["type"] == "object"
        assert "content_types" in filters_prop["properties"]
        assert "date_from" in filters_prop["properties"]
        assert "date_to" in filters_prop["properties"]

    @pytest.mark.description("SearchTool input_schema has cursor property")
    def test_input_schema_cursor(self) -> None:
        tool = SearchTool()
        schema = tool.input_schema
        cursor_prop = schema["properties"]["cursor"]
        assert cursor_prop["type"] == "string"

    @pytest.mark.description("SearchTool raises ValueError for empty query")
    def test_empty_query_raises(self) -> None:
        tool = SearchTool()
        with pytest.raises(ValueError, match="query cannot be empty"):
            tool(query="")

    @pytest.mark.description("SearchTool raises ValueError for whitespace query")
    def test_whitespace_query_raises(self) -> None:
        tool = SearchTool()
        with pytest.raises(ValueError, match="query cannot be empty"):
            tool(query="   ")

    @pytest.mark.description("SearchTool raises ValueError for limit < 1")
    def test_limit_too_low_raises(self) -> None:
        tool = SearchTool()
        with pytest.raises(ValueError, match="limit must be between 1 and 100"):
            tool(query="test", limit=0)

    @pytest.mark.description("SearchTool raises ValueError for limit > 100")
    def test_limit_too_high_raises(self) -> None:
        tool = SearchTool()
        with pytest.raises(ValueError, match="limit must be between 1 and 100"):
            tool(query="test", limit=101)

    @pytest.mark.description("SearchTool raises ValueError for min_score < 0")
    def test_min_score_too_low_raises(self) -> None:
        tool = SearchTool()
        with pytest.raises(ValueError, match="min_score must be between 0.0 and 1.0"):
            tool(query="test", min_score=-0.1)

    @pytest.mark.description("SearchTool raises ValueError for min_score > 1")
    def test_min_score_too_high_raises(self) -> None:
        tool = SearchTool()
        with pytest.raises(ValueError, match="min_score must be between 0.0 and 1.0"):
            tool(query="test", min_score=1.1)

    @pytest.mark.description("SearchTool initializes with custom search service")
    def test_custom_search_service(self) -> None:
        mock_service = MagicMock()
        tool = SearchTool(search_service=mock_service)
        assert tool._search_service == mock_service

    @pytest.mark.description("SearchTool lazily initializes search service")
    def test_lazy_service_init(self) -> None:
        tool = SearchTool()
        assert tool._search_service is None


class TestSearchToolExecution:
    """Tests for SearchTool execution with mocked SearchService."""

    @pytest.fixture
    def mock_search_service(self) -> MagicMock:
        """Create a mock SearchService."""
        mock_service = MagicMock()
        mock_service.search.return_value = SearchResponse(
            results=[
                SearchResult(
                    id="result-1",
                    score=0.95,
                    text="This is a test fragment",
                    source_id="episode-123",
                    source_type="audio",
                    start_time=45.0,
                    end_time=60.0,
                    corpus_id="podcast-corpus",
                    metadata={"channel": "Test Channel"},
                ),
                SearchResult(
                    id="result-2",
                    score=0.85,
                    text="Another test fragment",
                    source_id="episode-456",
                    source_type="video",
                    start_time=None,
                    end_time=None,
                    corpus_id="video-corpus",
                    metadata={},
                ),
            ],
            total_count=2,
            next_cursor=None,
            latency_ms=25.5,
            query=MagicMock(),
        )
        return mock_service

    @pytest.mark.description("SearchTool returns expected output structure")
    def test_output_structure(self, mock_search_service: MagicMock) -> None:
        tool = SearchTool(search_service=mock_search_service)
        result = tool(query="test query")

        assert "results" in result
        assert "total_count" in result
        assert "next_cursor" in result
        assert "latency_ms" in result

    @pytest.mark.description("SearchTool returns results with correct fields")
    def test_result_fields(self, mock_search_service: MagicMock) -> None:
        tool = SearchTool(search_service=mock_search_service)
        result = tool(query="test query")

        assert len(result["results"]) == 2

        first_result = result["results"][0]
        assert first_result["id"] == "result-1"
        assert first_result["score"] == 0.95
        assert first_result["snippet"] == "This is a test fragment"
        assert first_result["uri"] == "voogle://episode-123?t=45"
        assert first_result["metadata"]["source_id"] == "episode-123"
        assert first_result["metadata"]["source_type"] == "audio"

    @pytest.mark.description("SearchTool builds URI without timestamp for non-audio")
    def test_uri_without_timestamp(self, mock_search_service: MagicMock) -> None:
        tool = SearchTool(search_service=mock_search_service)
        result = tool(query="test query")

        second_result = result["results"][1]
        assert second_result["uri"] == "voogle://episode-456"

    @pytest.mark.description("SearchTool tracks latency")
    def test_latency_tracking(self, mock_search_service: MagicMock) -> None:
        tool = SearchTool(search_service=mock_search_service)
        result = tool(query="test query")

        assert result["latency_ms"] == 25.5

    @pytest.mark.description("SearchTool filters by min_score")
    def test_min_score_filtering(self, mock_search_service: MagicMock) -> None:
        tool = SearchTool(search_service=mock_search_service)
        result = tool(query="test query", min_score=0.9)

        # Only result with score >= 0.9 should be included
        assert len(result["results"]) == 1
        assert result["results"][0]["score"] == 0.95

    @pytest.mark.description("SearchTool passes corpus_ids to search service")
    def test_corpus_ids_passed(self, mock_search_service: MagicMock) -> None:
        tool = SearchTool(search_service=mock_search_service)
        tool(query="test query", corpus_ids=["corpus1", "corpus2"])

        mock_search_service.search.assert_called_once()
        call_args = mock_search_service.search.call_args[0][0]
        assert call_args.corpus_ids == ["corpus1", "corpus2"]

    @pytest.mark.description("SearchTool passes limit to search service")
    def test_limit_passed(self, mock_search_service: MagicMock) -> None:
        tool = SearchTool(search_service=mock_search_service)
        tool(query="test query", limit=25)

        mock_search_service.search.assert_called_once()
        call_args = mock_search_service.search.call_args[0][0]
        assert call_args.limit == 25

    @pytest.mark.description("SearchTool passes cursor to search service")
    def test_cursor_passed(self, mock_search_service: MagicMock) -> None:
        tool = SearchTool(search_service=mock_search_service)
        tool(query="test query", cursor="10")

        mock_search_service.search.assert_called_once()
        call_args = mock_search_service.search.call_args[0][0]
        assert call_args.cursor == "10"

    @pytest.mark.description("SearchTool parses content_types filter")
    def test_content_types_filter(self, mock_search_service: MagicMock) -> None:
        tool = SearchTool(search_service=mock_search_service)
        tool(query="test query", filters={"content_types": ["audio", "video"]})

        mock_search_service.search.assert_called_once()
        call_args = mock_search_service.search.call_args[0][0]
        assert call_args.content_types is not None
        assert len(call_args.content_types) == 2

    @pytest.mark.description("SearchTool parses date_from filter")
    def test_date_from_filter(self, mock_search_service: MagicMock) -> None:
        tool = SearchTool(search_service=mock_search_service)
        tool(query="test query", filters={"date_from": "2025-01-01"})

        mock_search_service.search.assert_called_once()
        call_args = mock_search_service.search.call_args[0][0]
        assert call_args.date_from is not None
        assert call_args.date_from.year == 2025
        assert call_args.date_from.month == 1
        assert call_args.date_from.day == 1

    @pytest.mark.description("SearchTool parses date_to filter")
    def test_date_to_filter(self, mock_search_service: MagicMock) -> None:
        tool = SearchTool(search_service=mock_search_service)
        tool(query="test query", filters={"date_to": "2025-12-31"})

        mock_search_service.search.assert_called_once()
        call_args = mock_search_service.search.call_args[0][0]
        assert call_args.date_to is not None
        assert call_args.date_to.year == 2025
        assert call_args.date_to.month == 12
        assert call_args.date_to.day == 31

    @pytest.mark.description("SearchTool handles invalid content_types gracefully")
    def test_invalid_content_types(self, mock_search_service: MagicMock) -> None:
        tool = SearchTool(search_service=mock_search_service)
        # Should not raise, just ignore invalid types
        tool(query="test query", filters={"content_types": ["invalid_type"]})

        mock_search_service.search.assert_called_once()
        call_args = mock_search_service.search.call_args[0][0]
        assert call_args.content_types == []

    @pytest.mark.description("SearchTool handles invalid dates gracefully")
    def test_invalid_dates(self, mock_search_service: MagicMock) -> None:
        tool = SearchTool(search_service=mock_search_service)
        # Should not raise, just ignore invalid dates
        tool(query="test query", filters={"date_from": "not-a-date"})

        mock_search_service.search.assert_called_once()
        call_args = mock_search_service.search.call_args[0][0]
        assert call_args.date_from is None

    @pytest.mark.description("SearchTool strips whitespace from query")
    def test_query_whitespace_stripped(self, mock_search_service: MagicMock) -> None:
        tool = SearchTool(search_service=mock_search_service)
        tool(query="  test query  ")

        mock_search_service.search.assert_called_once()
        call_args = mock_search_service.search.call_args[0][0]
        assert call_args.query_text == "test query"

    @pytest.mark.description("SearchTool returns next_cursor when results match limit")
    def test_next_cursor_with_full_results(self) -> None:
        mock_service = MagicMock()
        mock_service.search.return_value = SearchResponse(
            results=[
                SearchResult(
                    id=f"result-{i}",
                    score=0.9 - i * 0.01,
                    text=f"Fragment {i}",
                    source_id=f"source-{i}",
                )
                for i in range(5)
            ],
            total_count=5,
            next_cursor="5",
            latency_ms=10.0,
            query=MagicMock(),
        )

        tool = SearchTool(search_service=mock_service)
        result = tool(query="test", limit=5)

        assert result["next_cursor"] == "5"

    @pytest.mark.description("SearchTool returns None next_cursor when results < limit")
    def test_no_next_cursor_with_partial_results(self) -> None:
        mock_service = MagicMock()
        mock_service.search.return_value = SearchResponse(
            results=[
                SearchResult(
                    id="result-1",
                    score=0.9,
                    text="Fragment 1",
                    source_id="source-1",
                )
            ],
            total_count=1,
            next_cursor=None,
            latency_ms=10.0,
            query=MagicMock(),
        )

        tool = SearchTool(search_service=mock_service)
        result = tool(query="test", limit=5)

        assert result["next_cursor"] is None


class TestModuleLevelSearchTool:
    """Tests for the module-level search_tool instance."""

    @pytest.mark.description("search_tool is a SearchTool instance")
    def test_is_search_tool_instance(self) -> None:
        assert isinstance(search_tool, SearchTool)

    @pytest.mark.description("search_tool has expected name")
    def test_has_expected_name(self) -> None:
        assert search_tool.name == "search"

    @pytest.mark.description("search_tool input_schema is accessible")
    def test_input_schema_accessible(self) -> None:
        schema = search_tool.input_schema
        assert schema is not None
        assert "properties" in schema
        assert "query" in schema["properties"]
