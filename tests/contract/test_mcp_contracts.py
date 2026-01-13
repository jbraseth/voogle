# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Contract tests for MCP tool schema validation and error handling.

This module provides comprehensive contract tests covering:
- Schema validation for all MCP tools
- Valid input tests for each tool
- Invalid input error handling
- Pagination contract verification
- Long-running operation lifecycle tests
"""
from typing import Any
from unittest.mock import MagicMock

import pytest

from voogle.mcp.tools.corpora import ListCorporaTool, list_corpora_tool
from voogle.mcp.tools.expand import ExpandTool, ExpandToolError, expand_tool
from voogle.mcp.tools.ingest import (
    ChunkingStrategy,
    GetIngestionStatusTool,
    IngestTool,
    SourceType,
    get_ingestion_status_tool,
    ingest_tool,
)
from voogle.mcp.tools.resolve import OutputFormat, ResolveTool, resolve_tool
from voogle.mcp.tools.search import SearchTool, search_tool

pytestmark = pytest.mark.contract


# =============================================================================
# JSON Schema Contract Helpers
# =============================================================================


def validate_json_schema_structure(schema: dict[str, Any]) -> None:
    """Validate that a schema follows JSON Schema conventions."""
    assert isinstance(schema, dict), "Schema must be a dictionary"
    assert schema.get("type") == "object", "Root schema type must be 'object'"
    assert "properties" in schema, "Schema must have 'properties'"
    assert isinstance(schema["properties"], dict), "properties must be a dict"


def validate_property_has_type(prop: dict[str, Any], prop_name: str) -> None:
    """Validate that a property has a type definition."""
    # Properties can have "type" directly or use "oneOf"/"anyOf"
    has_type = (
        "type" in prop or "oneOf" in prop or "anyOf" in prop or "enum" in prop
    )
    assert has_type, f"Property '{prop_name}' must have a type definition"


def validate_required_is_list(schema: dict[str, Any]) -> None:
    """Validate that required is a list if present."""
    if "required" in schema:
        assert isinstance(
            schema["required"], list
        ), "required must be a list"


def validate_numeric_constraints(prop: dict[str, Any], prop_name: str) -> None:
    """Validate that numeric properties have sensible constraints."""
    if prop.get("type") in ("integer", "number"):
        # Check for reasonable bounds
        if "minimum" in prop or "maximum" in prop:
            if "minimum" in prop and "maximum" in prop:
                assert prop["minimum"] <= prop["maximum"], (
                    f"Property '{prop_name}' has minimum > maximum"
                )


# =============================================================================
# Schema Validation Tests for All Tools
# =============================================================================


class TestSearchToolSchema:
    """Contract tests for SearchTool schema validation."""

    @pytest.fixture
    def tool(self) -> SearchTool:
        return SearchTool()

    @pytest.mark.description("SearchTool schema follows JSON Schema structure")
    def test_schema_structure(self, tool: SearchTool) -> None:
        validate_json_schema_structure(tool.input_schema)

    @pytest.mark.description("SearchTool schema has required query field")
    def test_query_is_required(self, tool: SearchTool) -> None:
        assert "query" in tool.input_schema.get("required", [])

    @pytest.mark.description("SearchTool schema properties have types")
    def test_properties_have_types(self, tool: SearchTool) -> None:
        for prop_name, prop in tool.input_schema["properties"].items():
            validate_property_has_type(prop, prop_name)

    @pytest.mark.description("SearchTool limit has valid numeric constraints")
    def test_limit_constraints(self, tool: SearchTool) -> None:
        limit_prop = tool.input_schema["properties"]["limit"]
        assert limit_prop["minimum"] == 1
        assert limit_prop["maximum"] == 100
        validate_numeric_constraints(limit_prop, "limit")

    @pytest.mark.description("SearchTool min_score has valid range")
    def test_min_score_constraints(self, tool: SearchTool) -> None:
        min_score_prop = tool.input_schema["properties"]["min_score"]
        assert min_score_prop["minimum"] == 0.0
        assert min_score_prop["maximum"] == 1.0
        validate_numeric_constraints(min_score_prop, "min_score")

    @pytest.mark.description("SearchTool filters schema has nested properties")
    def test_filters_nested_schema(self, tool: SearchTool) -> None:
        filters_prop = tool.input_schema["properties"]["filters"]
        assert filters_prop["type"] == "object"
        assert "properties" in filters_prop
        assert "content_types" in filters_prop["properties"]
        assert "date_from" in filters_prop["properties"]
        assert "date_to" in filters_prop["properties"]

    @pytest.mark.description("SearchTool date filters have format hint")
    def test_date_filter_format(self, tool: SearchTool) -> None:
        filters_props = tool.input_schema["properties"]["filters"]["properties"]
        assert filters_props["date_from"].get("format") == "date"
        assert filters_props["date_to"].get("format") == "date"


class TestIngestToolSchema:
    """Contract tests for IngestTool schema validation."""

    @pytest.fixture
    def tool(self) -> IngestTool:
        return IngestTool()

    @pytest.mark.description("IngestTool schema follows JSON Schema structure")
    def test_schema_structure(self, tool: IngestTool) -> None:
        validate_json_schema_structure(tool.input_schema)

    @pytest.mark.description("IngestTool has required corpus_id and source")
    def test_required_fields(self, tool: IngestTool) -> None:
        required = tool.input_schema.get("required", [])
        assert "corpus_id" in required
        assert "source" in required

    @pytest.mark.description("IngestTool source has nested required fields")
    def test_source_nested_required(self, tool: IngestTool) -> None:
        source_prop = tool.input_schema["properties"]["source"]
        assert source_prop["type"] == "object"
        source_required = source_prop.get("required", [])
        assert "type" in source_required
        assert "value" in source_required

    @pytest.mark.description("IngestTool source type has valid enum")
    def test_source_type_enum(self, tool: IngestTool) -> None:
        source_type_prop = tool.input_schema["properties"]["source"]["properties"]["type"]
        assert "enum" in source_type_prop
        expected_values = [st.value for st in SourceType]
        assert set(source_type_prop["enum"]) == set(expected_values)

    @pytest.mark.description("IngestTool chunking_strategy has valid enum")
    def test_chunking_strategy_enum(self, tool: IngestTool) -> None:
        chunking_prop = tool.input_schema["properties"]["chunking_strategy"]
        assert "enum" in chunking_prop
        expected_values = [cs.value for cs in ChunkingStrategy]
        assert set(chunking_prop["enum"]) == set(expected_values)

    @pytest.mark.description("IngestTool source value supports oneOf")
    def test_source_value_oneOf(self, tool: IngestTool) -> None:
        source_value_prop = tool.input_schema["properties"]["source"]["properties"]["value"]
        assert "oneOf" in source_value_prop
        types = [schema.get("type") for schema in source_value_prop["oneOf"]]
        assert "string" in types
        assert "array" in types


class TestGetIngestionStatusToolSchema:
    """Contract tests for GetIngestionStatusTool schema validation."""

    @pytest.fixture
    def tool(self) -> GetIngestionStatusTool:
        return GetIngestionStatusTool()

    @pytest.mark.description("GetIngestionStatusTool schema follows JSON Schema structure")
    def test_schema_structure(self, tool: GetIngestionStatusTool) -> None:
        validate_json_schema_structure(tool.input_schema)

    @pytest.mark.description("GetIngestionStatusTool has required job_id")
    def test_job_id_required(self, tool: GetIngestionStatusTool) -> None:
        assert "job_id" in tool.input_schema.get("required", [])

    @pytest.mark.description("GetIngestionStatusTool job_id has minLength")
    def test_job_id_min_length(self, tool: GetIngestionStatusTool) -> None:
        job_id_prop = tool.input_schema["properties"]["job_id"]
        assert job_id_prop.get("minLength") == 1


class TestExpandToolSchema:
    """Contract tests for ExpandTool schema validation."""

    @pytest.fixture
    def tool(self) -> ExpandTool:
        return ExpandTool()

    @pytest.mark.description("ExpandTool schema follows JSON Schema structure")
    def test_schema_structure(self, tool: ExpandTool) -> None:
        validate_json_schema_structure(tool.input_schema)

    @pytest.mark.description("ExpandTool has required fragment_id and source_id")
    def test_required_fields(self, tool: ExpandTool) -> None:
        required = tool.input_schema.get("required", [])
        assert "fragment_id" in required
        assert "source_id" in required

    @pytest.mark.description("ExpandTool direction has valid enum")
    def test_direction_enum(self, tool: ExpandTool) -> None:
        direction_prop = tool.input_schema["properties"]["direction"]
        assert "enum" in direction_prop
        assert set(direction_prop["enum"]) == {"before", "after", "both"}

    @pytest.mark.description("ExpandTool tokens has valid constraints")
    def test_tokens_constraints(self, tool: ExpandTool) -> None:
        tokens_prop = tool.input_schema["properties"]["tokens"]
        assert tokens_prop["minimum"] == 1
        assert tokens_prop["maximum"] == 2000
        validate_numeric_constraints(tokens_prop, "tokens")

    @pytest.mark.description("ExpandTool max_fragments has valid constraints")
    def test_max_fragments_constraints(self, tool: ExpandTool) -> None:
        max_fragments_prop = tool.input_schema["properties"]["max_fragments"]
        assert max_fragments_prop["minimum"] == 1
        assert max_fragments_prop["maximum"] == 20
        validate_numeric_constraints(max_fragments_prop, "max_fragments")


class TestResolveToolSchema:
    """Contract tests for ResolveTool schema validation."""

    @pytest.fixture
    def tool(self) -> ResolveTool:
        return ResolveTool()

    @pytest.mark.description("ResolveTool schema follows JSON Schema structure")
    def test_schema_structure(self, tool: ResolveTool) -> None:
        validate_json_schema_structure(tool.input_schema)

    @pytest.mark.description("ResolveTool has required uri")
    def test_uri_required(self, tool: ResolveTool) -> None:
        assert "uri" in tool.input_schema.get("required", [])

    @pytest.mark.description("ResolveTool format has valid enum")
    def test_format_enum(self, tool: ResolveTool) -> None:
        format_prop = tool.input_schema["properties"]["format"]
        assert "enum" in format_prop
        expected_values = [of.value for of in OutputFormat]
        assert set(format_prop["enum"]) == set(expected_values)


class TestListCorporaToolSchema:
    """Contract tests for ListCorporaTool schema validation."""

    @pytest.fixture
    def tool(self) -> ListCorporaTool:
        return ListCorporaTool()

    @pytest.mark.description("ListCorporaTool schema follows JSON Schema structure")
    def test_schema_structure(self, tool: ListCorporaTool) -> None:
        validate_json_schema_structure(tool.input_schema)

    @pytest.mark.description("ListCorporaTool has no required fields")
    def test_no_required_fields(self, tool: ListCorporaTool) -> None:
        required = tool.input_schema.get("required", [])
        assert len(required) == 0

    @pytest.mark.description("ListCorporaTool limit has valid constraints")
    def test_limit_constraints(self, tool: ListCorporaTool) -> None:
        limit_prop = tool.input_schema["properties"]["limit"]
        assert limit_prop["minimum"] == 1
        assert limit_prop["maximum"] == tool.MAX_LIMIT
        validate_numeric_constraints(limit_prop, "limit")

    @pytest.mark.description("ListCorporaTool include_stats is boolean")
    def test_include_stats_type(self, tool: ListCorporaTool) -> None:
        include_stats_prop = tool.input_schema["properties"]["include_stats"]
        assert include_stats_prop["type"] == "boolean"


# =============================================================================
# Valid Input Tests
# =============================================================================


class TestSearchToolValidInput:
    """Contract tests for valid SearchTool inputs."""

    @pytest.fixture
    def mock_search_service(self) -> MagicMock:
        from voogle.services.search import SearchResponse

        mock = MagicMock()
        mock.search.return_value = SearchResponse(
            results=[],
            total_count=0,
            next_cursor=None,
            latency_ms=10.0,
            query=MagicMock(),
        )
        return mock

    @pytest.mark.description("SearchTool accepts minimal valid input")
    def test_minimal_input(self, mock_search_service: MagicMock) -> None:
        tool = SearchTool(search_service=mock_search_service)
        result = tool(query="test")
        assert "results" in result
        assert "total_count" in result
        assert "latency_ms" in result

    @pytest.mark.description("SearchTool accepts all optional parameters")
    def test_all_parameters(self, mock_search_service: MagicMock) -> None:
        tool = SearchTool(search_service=mock_search_service)
        result = tool(
            query="test query",
            corpus_ids=["corpus1", "corpus2"],
            limit=50,
            min_score=0.5,
            filters={"content_types": ["audio"], "date_from": "2025-01-01"},
            cursor="abc123",
        )
        assert "results" in result

    @pytest.mark.description("SearchTool output has required contract fields")
    def test_output_contract(self, mock_search_service: MagicMock) -> None:
        tool = SearchTool(search_service=mock_search_service)
        result = tool(query="test")

        # Required output fields per contract
        assert "results" in result
        assert isinstance(result["results"], list)
        assert "total_count" in result
        assert isinstance(result["total_count"], int)
        assert "next_cursor" in result
        assert "latency_ms" in result
        assert isinstance(result["latency_ms"], (int, float))


class TestIngestToolValidInput:
    """Contract tests for valid IngestTool inputs."""

    @pytest.fixture
    def mock_job_service(self) -> MagicMock:
        from voogle.pipeline.jobs import Job, JobStatus, JobProgress

        mock = MagicMock()
        mock_job = MagicMock(spec=Job)
        mock_job.status = JobStatus.PENDING
        mock.create.return_value = mock_job
        return mock

    @pytest.mark.description("IngestTool accepts URL source")
    def test_url_source(self, mock_job_service: MagicMock) -> None:
        tool = IngestTool(job_service=mock_job_service)
        result = tool(
            corpus_id="test-corpus",
            source={"type": "url", "value": "https://example.com/file.mp3"},
        )
        assert "job_id" in result
        assert "status" in result
        assert "message" in result

    @pytest.mark.description("IngestTool accepts file source")
    def test_file_source(self, mock_job_service: MagicMock) -> None:
        tool = IngestTool(job_service=mock_job_service)
        result = tool(
            corpus_id="test-corpus",
            source={"type": "file", "value": "/path/to/file.mp3"},
        )
        assert "job_id" in result
        assert result["status"] == "pending"

    @pytest.mark.description("IngestTool accepts batch source")
    def test_batch_source(self, mock_job_service: MagicMock) -> None:
        tool = IngestTool(job_service=mock_job_service)
        result = tool(
            corpus_id="test-corpus",
            source={
                "type": "batch",
                "value": ["https://example.com/1.mp3", "https://example.com/2.mp3"],
            },
        )
        assert "job_id" in result

    @pytest.mark.description("IngestTool accepts all chunking strategies")
    def test_chunking_strategies(self, mock_job_service: MagicMock) -> None:
        tool = IngestTool(job_service=mock_job_service)
        for strategy in ChunkingStrategy:
            result = tool(
                corpus_id="test-corpus",
                source={"type": "url", "value": "https://example.com/file.mp3"},
                chunking_strategy=strategy.value,
            )
            assert "job_id" in result

    @pytest.mark.description("IngestTool output has job_id format contract")
    def test_job_id_format(self, mock_job_service: MagicMock) -> None:
        tool = IngestTool(job_service=mock_job_service)
        result = tool(
            corpus_id="test-corpus",
            source={"type": "url", "value": "https://example.com/file.mp3"},
        )
        # Job ID should start with "ingest-" prefix
        assert result["job_id"].startswith("ingest-")


class TestExpandToolValidInput:
    """Contract tests for valid ExpandTool inputs."""

    @pytest.fixture
    def mock_expander(self) -> MagicMock:
        from voogle.services.expansion import ExpandedFragment, ContextFragment

        mock = MagicMock()
        mock_result = MagicMock(spec=ExpandedFragment)
        mock_result.id = "frag-123"
        mock_result.text = "Original text"
        mock_result.source_id = "source-123"
        mock_result.before_context = []
        mock_result.after_context = []
        mock.expand.return_value = mock_result
        mock.get_full_context_text.return_value = "Original text"
        mock.get_context_token_count.return_value = 10
        return mock

    @pytest.mark.description("ExpandTool accepts minimal valid input")
    def test_minimal_input(self, mock_expander: MagicMock) -> None:
        tool = ExpandTool(context_expander=mock_expander)
        result = tool(fragment_id="frag-123", source_id="source-123")
        assert "fragment_id" in result
        assert "original_text" in result
        assert "combined_text" in result

    @pytest.mark.description("ExpandTool accepts all direction values")
    def test_all_directions(self, mock_expander: MagicMock) -> None:
        tool = ExpandTool(context_expander=mock_expander)
        for direction in ["before", "after", "both"]:
            result = tool(
                fragment_id="frag-123",
                source_id="source-123",
                direction=direction,
            )
            assert "fragment_id" in result

    @pytest.mark.description("ExpandTool output has boundary indicators")
    def test_boundary_indicators(self, mock_expander: MagicMock) -> None:
        tool = ExpandTool(context_expander=mock_expander)
        result = tool(fragment_id="frag-123", source_id="source-123")
        assert "at_document_start" in result
        assert "at_document_end" in result
        assert isinstance(result["at_document_start"], bool)
        assert isinstance(result["at_document_end"], bool)


class TestResolveToolValidInput:
    """Contract tests for valid ResolveTool inputs."""

    @pytest.fixture
    def mock_qdrant_client(self) -> MagicMock:
        mock = MagicMock()
        mock_point = MagicMock()
        mock_point.payload = {
            "text": "Test content",
            "source_id": "source-123",
            "source_type": "audio",
            "start_time": 45.0,
            "end_time": 60.0,
        }
        mock.retrieve.return_value = [mock_point]
        mock.scroll.return_value = ([mock_point], None)
        return mock

    @pytest.mark.description("ResolveTool accepts semantic:// URI")
    def test_semantic_uri(self, mock_qdrant_client: MagicMock) -> None:
        tool = ResolveTool(qdrant_client=mock_qdrant_client)
        result = tool(uri="semantic://corpus/doc#fragment-123")
        assert "content" in result
        assert "format" in result
        assert "uri" in result

    @pytest.mark.description("ResolveTool accepts voogle:// URI")
    def test_voogle_uri(self, mock_qdrant_client: MagicMock) -> None:
        tool = ResolveTool(qdrant_client=mock_qdrant_client)
        result = tool(uri="voogle://source-123?t=45")
        assert "content" in result
        assert "deep_link" in result

    @pytest.mark.description("ResolveTool accepts all output formats")
    def test_all_formats(self, mock_qdrant_client: MagicMock) -> None:
        tool = ResolveTool(qdrant_client=mock_qdrant_client)
        for fmt in OutputFormat:
            result = tool(uri="semantic://corpus/doc#fragment", format=fmt.value)
            assert result["format"] == fmt.value

    @pytest.mark.description("ResolveTool output has metadata")
    def test_metadata_output(self, mock_qdrant_client: MagicMock) -> None:
        tool = ResolveTool(qdrant_client=mock_qdrant_client)
        result = tool(uri="semantic://corpus/doc#fragment")
        assert "metadata" in result
        assert isinstance(result["metadata"], dict)


class TestListCorporaToolValidInput:
    """Contract tests for valid ListCorporaTool inputs."""

    @pytest.fixture
    def mock_corpus_service(self) -> MagicMock:
        from datetime import datetime

        mock = MagicMock()
        mock_corpus = MagicMock()
        mock_corpus.id = "corpus-1"
        mock_corpus.name = "Test Corpus"
        mock_corpus.description = "A test corpus"
        mock_corpus.document_count = 100
        mock_corpus.updated_at = datetime(2025, 1, 15)
        mock.list_all.return_value = [mock_corpus]
        return mock

    @pytest.mark.description("ListCorporaTool accepts no parameters")
    def test_no_parameters(self, mock_corpus_service: MagicMock) -> None:
        tool = ListCorporaTool(corpus_service=mock_corpus_service)
        result = tool()
        assert "corpora" in result
        assert "total_count" in result
        assert "next_cursor" in result

    @pytest.mark.description("ListCorporaTool accepts include_stats")
    def test_with_stats(self, mock_corpus_service: MagicMock) -> None:
        tool = ListCorporaTool(corpus_service=mock_corpus_service)
        result = tool(include_stats=True)
        assert "corpora" in result
        if result["corpora"]:
            corpus = result["corpora"][0]
            assert "document_count" in corpus
            assert "last_updated" in corpus

    @pytest.mark.description("ListCorporaTool output corpus has required fields")
    def test_corpus_contract(self, mock_corpus_service: MagicMock) -> None:
        tool = ListCorporaTool(corpus_service=mock_corpus_service)
        result = tool()
        if result["corpora"]:
            corpus = result["corpora"][0]
            assert "id" in corpus
            assert "name" in corpus
            assert "description" in corpus


# =============================================================================
# Invalid Input Error Handling Tests
# =============================================================================


class TestSearchToolInvalidInput:
    """Contract tests for SearchTool error handling."""

    @pytest.fixture
    def tool(self) -> SearchTool:
        return SearchTool()

    @pytest.mark.description("SearchTool rejects empty query")
    def test_empty_query(self, tool: SearchTool) -> None:
        with pytest.raises(ValueError, match="query cannot be empty"):
            tool(query="")

    @pytest.mark.description("SearchTool rejects whitespace-only query")
    def test_whitespace_query(self, tool: SearchTool) -> None:
        with pytest.raises(ValueError, match="query cannot be empty"):
            tool(query="   ")

    @pytest.mark.description("SearchTool rejects limit below minimum")
    def test_limit_below_min(self, tool: SearchTool) -> None:
        with pytest.raises(ValueError, match="limit must be between"):
            tool(query="test", limit=0)

    @pytest.mark.description("SearchTool rejects limit above maximum")
    def test_limit_above_max(self, tool: SearchTool) -> None:
        with pytest.raises(ValueError, match="limit must be between"):
            tool(query="test", limit=101)

    @pytest.mark.description("SearchTool rejects min_score below 0")
    def test_min_score_below_zero(self, tool: SearchTool) -> None:
        with pytest.raises(ValueError, match="min_score must be between"):
            tool(query="test", min_score=-0.1)

    @pytest.mark.description("SearchTool rejects min_score above 1")
    def test_min_score_above_one(self, tool: SearchTool) -> None:
        with pytest.raises(ValueError, match="min_score must be between"):
            tool(query="test", min_score=1.5)


class TestIngestToolInvalidInput:
    """Contract tests for IngestTool error handling."""

    @pytest.fixture
    def tool(self) -> IngestTool:
        return IngestTool()

    @pytest.mark.description("IngestTool rejects empty corpus_id")
    def test_empty_corpus_id(self, tool: IngestTool) -> None:
        with pytest.raises(ValueError, match="corpus_id cannot be empty"):
            tool(
                corpus_id="",
                source={"type": "url", "value": "https://example.com"},
            )

    @pytest.mark.description("IngestTool rejects whitespace corpus_id")
    def test_whitespace_corpus_id(self, tool: IngestTool) -> None:
        with pytest.raises(ValueError, match="corpus_id cannot be empty"):
            tool(
                corpus_id="   ",
                source={"type": "url", "value": "https://example.com"},
            )

    @pytest.mark.description("IngestTool rejects empty source")
    def test_empty_source(self, tool: IngestTool) -> None:
        with pytest.raises(ValueError, match="source cannot be empty"):
            tool(corpus_id="test-corpus", source={})

    @pytest.mark.description("IngestTool rejects missing source type")
    def test_missing_source_type(self, tool: IngestTool) -> None:
        with pytest.raises(ValueError, match="source.type is required"):
            tool(
                corpus_id="test-corpus",
                source={"value": "https://example.com"},
            )

    @pytest.mark.description("IngestTool rejects invalid source type")
    def test_invalid_source_type(self, tool: IngestTool) -> None:
        with pytest.raises(ValueError, match="Invalid source type"):
            tool(
                corpus_id="test-corpus",
                source={"type": "invalid", "value": "https://example.com"},
            )

    @pytest.mark.description("IngestTool rejects missing source value")
    def test_missing_source_value(self, tool: IngestTool) -> None:
        with pytest.raises(ValueError, match="source.value is required"):
            tool(corpus_id="test-corpus", source={"type": "url"})

    @pytest.mark.description("IngestTool rejects non-list batch value")
    def test_batch_non_list_value(self, tool: IngestTool) -> None:
        with pytest.raises(ValueError, match="must be a list for batch"):
            tool(
                corpus_id="test-corpus",
                source={"type": "batch", "value": "single-url"},
            )

    @pytest.mark.description("IngestTool rejects empty batch value")
    def test_batch_empty_list(self, tool: IngestTool) -> None:
        with pytest.raises(ValueError, match="cannot be empty for batch"):
            tool(
                corpus_id="test-corpus",
                source={"type": "batch", "value": []},
            )

    @pytest.mark.description("IngestTool rejects non-string URL value")
    def test_url_non_string_value(self, tool: IngestTool) -> None:
        with pytest.raises(ValueError, match="must be a string for url"):
            tool(
                corpus_id="test-corpus",
                source={"type": "url", "value": ["list-value"]},
            )

    @pytest.mark.description("IngestTool rejects invalid chunking strategy")
    def test_invalid_chunking_strategy(self, tool: IngestTool) -> None:
        with pytest.raises(ValueError, match="Invalid chunking strategy"):
            tool(
                corpus_id="test-corpus",
                source={"type": "url", "value": "https://example.com"},
                chunking_strategy="invalid_strategy",
            )


class TestGetIngestionStatusInvalidInput:
    """Contract tests for GetIngestionStatusTool error handling."""

    @pytest.fixture
    def tool(self) -> GetIngestionStatusTool:
        return GetIngestionStatusTool()

    @pytest.mark.description("GetIngestionStatusTool rejects empty job_id")
    def test_empty_job_id(self, tool: GetIngestionStatusTool) -> None:
        with pytest.raises(ValueError, match="job_id cannot be empty"):
            tool(job_id="")

    @pytest.mark.description("GetIngestionStatusTool rejects whitespace job_id")
    def test_whitespace_job_id(self, tool: GetIngestionStatusTool) -> None:
        with pytest.raises(ValueError, match="job_id cannot be empty"):
            tool(job_id="   ")


class TestExpandToolInvalidInput:
    """Contract tests for ExpandTool error handling."""

    @pytest.fixture
    def tool(self) -> ExpandTool:
        return ExpandTool()

    @pytest.mark.description("ExpandTool raises ExpandToolError for empty fragment_id")
    def test_empty_fragment_id(self, tool: ExpandTool) -> None:
        with pytest.raises(ExpandToolError) as exc_info:
            tool(fragment_id="", source_id="source-123")
        assert exc_info.value.error_code == "INVALID_FRAGMENT_ID"

    @pytest.mark.description("ExpandTool raises ExpandToolError for empty source_id")
    def test_empty_source_id(self, tool: ExpandTool) -> None:
        with pytest.raises(ExpandToolError) as exc_info:
            tool(fragment_id="frag-123", source_id="")
        assert exc_info.value.error_code == "INVALID_SOURCE_ID"

    @pytest.mark.description("ExpandTool rejects invalid direction")
    def test_invalid_direction(self, tool: ExpandTool) -> None:
        with pytest.raises(ValueError, match="direction must be"):
            tool(
                fragment_id="frag-123",
                source_id="source-123",
                direction="invalid",
            )

    @pytest.mark.description("ExpandTool rejects tokens below minimum")
    def test_tokens_below_min(self, tool: ExpandTool) -> None:
        with pytest.raises(ValueError, match="tokens must be between"):
            tool(
                fragment_id="frag-123",
                source_id="source-123",
                tokens=0,
            )

    @pytest.mark.description("ExpandTool rejects tokens above maximum")
    def test_tokens_above_max(self, tool: ExpandTool) -> None:
        with pytest.raises(ValueError, match="tokens must be between"):
            tool(
                fragment_id="frag-123",
                source_id="source-123",
                tokens=3000,
            )

    @pytest.mark.description("ExpandTool rejects max_fragments below minimum")
    def test_max_fragments_below_min(self, tool: ExpandTool) -> None:
        with pytest.raises(ValueError, match="max_fragments must be between"):
            tool(
                fragment_id="frag-123",
                source_id="source-123",
                max_fragments=0,
            )

    @pytest.mark.description("ExpandTool rejects max_fragments above maximum")
    def test_max_fragments_above_max(self, tool: ExpandTool) -> None:
        with pytest.raises(ValueError, match="max_fragments must be between"):
            tool(
                fragment_id="frag-123",
                source_id="source-123",
                max_fragments=25,
            )


class TestResolveToolInvalidInput:
    """Contract tests for ResolveTool error handling."""

    @pytest.fixture
    def tool(self) -> ResolveTool:
        return ResolveTool()

    @pytest.mark.description("ResolveTool rejects empty URI")
    def test_empty_uri(self, tool: ResolveTool) -> None:
        with pytest.raises(ValueError, match="uri cannot be empty"):
            tool.parse_uri("")

    @pytest.mark.description("ResolveTool rejects unsupported URI scheme")
    def test_unsupported_scheme(self, tool: ResolveTool) -> None:
        with pytest.raises(ValueError, match="Unsupported URI scheme"):
            tool.parse_uri("http://example.com")

    @pytest.mark.description("ResolveTool rejects invalid format")
    def test_invalid_format(self, tool: ResolveTool) -> None:
        mock_client = MagicMock()
        mock_client.retrieve.return_value = []
        tool = ResolveTool(qdrant_client=mock_client)
        with pytest.raises(ValueError, match="Unsupported format"):
            tool(uri="semantic://corpus/doc#frag", format="invalid")


class TestListCorporaToolInvalidInput:
    """Contract tests for ListCorporaTool error handling."""

    @pytest.fixture
    def mock_corpus_service(self) -> MagicMock:
        mock = MagicMock()
        mock.list_all.return_value = []
        return mock

    @pytest.mark.description("ListCorporaTool rejects limit below minimum")
    def test_limit_below_min(self, mock_corpus_service: MagicMock) -> None:
        tool = ListCorporaTool(corpus_service=mock_corpus_service)
        with pytest.raises(ValueError, match="limit must be between"):
            tool(limit=0)

    @pytest.mark.description("ListCorporaTool rejects limit above maximum")
    def test_limit_above_max(self, mock_corpus_service: MagicMock) -> None:
        tool = ListCorporaTool(corpus_service=mock_corpus_service)
        with pytest.raises(ValueError, match="limit must be between"):
            tool(limit=101)

    @pytest.mark.description("ListCorporaTool rejects invalid cursor")
    def test_invalid_cursor(self, mock_corpus_service: MagicMock) -> None:
        tool = ListCorporaTool(corpus_service=mock_corpus_service)
        with pytest.raises(ValueError, match="Invalid cursor"):
            tool(cursor="not-valid-base64!")


# =============================================================================
# Pagination Contract Verification
# =============================================================================


class TestSearchToolPagination:
    """Contract tests for SearchTool pagination."""

    @pytest.mark.description("SearchTool cursor passes through to service")
    def test_cursor_passthrough(self) -> None:
        from voogle.services.search import SearchResponse

        mock_service = MagicMock()
        mock_service.search.return_value = SearchResponse(
            results=[],
            total_count=0,
            next_cursor="next-page",
            latency_ms=10.0,
            query=MagicMock(),
        )
        tool = SearchTool(search_service=mock_service)
        tool(query="test", cursor="page-1")

        call_args = mock_service.search.call_args[0][0]
        assert call_args.cursor == "page-1"

    @pytest.mark.description("SearchTool returns next_cursor when more results exist")
    def test_next_cursor_returned(self) -> None:
        from voogle.services.search import SearchResponse, SearchResult

        mock_service = MagicMock()
        mock_service.search.return_value = SearchResponse(
            results=[
                SearchResult(id=f"r{i}", score=0.9, text="t", source_id="s")
                for i in range(10)
            ],
            total_count=100,
            next_cursor="offset-10",
            latency_ms=10.0,
            query=MagicMock(),
        )
        tool = SearchTool(search_service=mock_service)
        result = tool(query="test", limit=10)

        assert result["next_cursor"] == "offset-10"

    @pytest.mark.description("SearchTool returns None cursor when no more results")
    def test_no_cursor_at_end(self) -> None:
        from voogle.services.search import SearchResponse, SearchResult

        mock_service = MagicMock()
        mock_service.search.return_value = SearchResponse(
            results=[
                SearchResult(id="r1", score=0.9, text="t", source_id="s")
            ],
            total_count=1,
            next_cursor=None,
            latency_ms=10.0,
            query=MagicMock(),
        )
        tool = SearchTool(search_service=mock_service)
        result = tool(query="test", limit=10)

        assert result["next_cursor"] is None


class TestListCorporaToolPagination:
    """Contract tests for ListCorporaTool pagination."""

    @pytest.fixture
    def corpus_list(self) -> list[MagicMock]:
        from datetime import datetime

        corpora = []
        for i in range(50):
            mock = MagicMock()
            mock.id = f"corpus-{i}"
            mock.name = f"Corpus {i}"
            mock.description = f"Description {i}"
            mock.document_count = i * 10
            mock.updated_at = datetime(2025, 1, 15)
            corpora.append(mock)
        return corpora

    @pytest.mark.description("ListCorporaTool cursor encodes/decodes correctly")
    def test_cursor_encoding(self) -> None:
        tool = ListCorporaTool()

        # Encode offset
        cursor = tool._encode_cursor(20)
        assert isinstance(cursor, str)

        # Decode back
        offset = tool._decode_cursor(cursor)
        assert offset == 20

    @pytest.mark.description("ListCorporaTool returns next_cursor for partial page")
    def test_pagination_with_more_results(self, corpus_list: list[MagicMock]) -> None:
        mock_service = MagicMock()
        mock_service.list_all.return_value = corpus_list
        tool = ListCorporaTool(corpus_service=mock_service)

        result = tool(limit=10)

        assert result["total_count"] == 50
        assert len(result["corpora"]) == 10
        assert result["next_cursor"] is not None

    @pytest.mark.description("ListCorporaTool second page uses cursor correctly")
    def test_pagination_second_page(self, corpus_list: list[MagicMock]) -> None:
        mock_service = MagicMock()
        mock_service.list_all.return_value = corpus_list
        tool = ListCorporaTool(corpus_service=mock_service)

        # Get first page
        page1 = tool(limit=10)

        # Get second page
        page2 = tool(cursor=page1["next_cursor"], limit=10)

        # Should have different corpora
        assert page1["corpora"][0]["id"] != page2["corpora"][0]["id"]
        assert page2["corpora"][0]["id"] == "corpus-10"

    @pytest.mark.description("ListCorporaTool returns None cursor at end")
    def test_no_cursor_at_end(self, corpus_list: list[MagicMock]) -> None:
        mock_service = MagicMock()
        mock_service.list_all.return_value = corpus_list[:5]  # Only 5 corpora
        tool = ListCorporaTool(corpus_service=mock_service)

        result = tool(limit=10)

        assert result["total_count"] == 5
        assert len(result["corpora"]) == 5
        assert result["next_cursor"] is None


# =============================================================================
# Long-Running Operation Lifecycle Tests
# =============================================================================


class TestIngestionLifecycle:
    """Contract tests for ingestion job lifecycle."""

    @pytest.fixture
    def mock_job_service(self) -> MagicMock:
        from voogle.pipeline.jobs import Job, JobStatus, JobProgress

        mock = MagicMock()
        return mock

    @pytest.mark.description("Ingestion job starts in pending status")
    def test_job_starts_pending(self, mock_job_service: MagicMock) -> None:
        from voogle.pipeline.jobs import JobStatus

        mock_job = MagicMock()
        mock_job.status = JobStatus.PENDING
        mock_job_service.create.return_value = mock_job

        tool = IngestTool(job_service=mock_job_service)
        result = tool(
            corpus_id="test-corpus",
            source={"type": "url", "value": "https://example.com"},
        )

        assert result["status"] == "pending"

    @pytest.mark.description("GetIngestionStatus returns running status")
    def test_job_running_status(self, mock_job_service: MagicMock) -> None:
        from voogle.pipeline.jobs import JobStatus, JobProgress

        mock_job = MagicMock()
        mock_job.status = JobStatus.RUNNING
        # JobProgress.percentage is a computed property, not a constructor arg
        mock_job.progress = JobProgress(current=5, total=10, stage="indexing")
        mock_job.error = None
        mock_job_service.get.return_value = mock_job

        tool = GetIngestionStatusTool(job_service=mock_job_service)
        result = tool(job_id="ingest-abc123")

        assert result["status"] == "running"
        assert result["progress_percentage"] == 50.0
        assert result["documents_processed"] == 5
        assert result["total_documents"] == 10

    @pytest.mark.description("GetIngestionStatus returns completed status")
    def test_job_completed_status(self, mock_job_service: MagicMock) -> None:
        from voogle.pipeline.jobs import JobStatus, JobProgress

        mock_job = MagicMock()
        mock_job.status = JobStatus.COMPLETED
        # JobProgress.percentage is a computed property
        mock_job.progress = JobProgress(current=10, total=10)
        mock_job.error = None
        mock_job_service.get.return_value = mock_job

        tool = GetIngestionStatusTool(job_service=mock_job_service)
        result = tool(job_id="ingest-abc123")

        assert result["status"] == "completed"
        assert result["progress_percentage"] == 100.0

    @pytest.mark.description("GetIngestionStatus returns failed status with errors")
    def test_job_failed_status(self, mock_job_service: MagicMock) -> None:
        from voogle.pipeline.jobs import JobStatus, JobProgress

        mock_job = MagicMock()
        mock_job.status = JobStatus.FAILED
        # JobProgress.percentage is a computed property
        mock_job.progress = JobProgress(current=3, total=10)
        mock_job.error = "Connection timeout"
        mock_job_service.get.return_value = mock_job

        tool = GetIngestionStatusTool(job_service=mock_job_service)
        result = tool(job_id="ingest-abc123")

        assert result["status"] == "failed"
        assert len(result["errors"]) > 0
        assert "Connection timeout" in result["errors"][0]

    @pytest.mark.description("GetIngestionStatus returns not_found for unknown job")
    def test_job_not_found(self, mock_job_service: MagicMock) -> None:
        mock_job_service.get.return_value = None

        tool = GetIngestionStatusTool(job_service=mock_job_service)
        result = tool(job_id="ingest-nonexistent")

        assert result["status"] == "not_found"
        assert len(result["errors"]) > 0

    @pytest.mark.description("Ingestion lifecycle contract: job_id is consistent")
    def test_job_id_consistency(self, mock_job_service: MagicMock) -> None:
        from voogle.pipeline.jobs import JobStatus, JobProgress

        # Create job
        mock_job = MagicMock()
        mock_job.status = JobStatus.PENDING
        mock_job_service.create.return_value = mock_job

        ingest = IngestTool(job_service=mock_job_service)
        create_result = ingest(
            corpus_id="test-corpus",
            source={"type": "url", "value": "https://example.com"},
        )
        job_id = create_result["job_id"]

        # Check status uses same ID
        mock_job.status = JobStatus.RUNNING
        # JobProgress.percentage is a computed property
        mock_job.progress = JobProgress(current=0, total=1)
        mock_job.error = None
        mock_job_service.get.return_value = mock_job

        status_tool = GetIngestionStatusTool(job_service=mock_job_service)
        status_result = status_tool(job_id=job_id)

        assert status_result["job_id"] == job_id


class TestExpandToolNotFound:
    """Contract tests for expand tool when fragment is not found."""

    @pytest.mark.description("ExpandTool raises FRAGMENT_NOT_FOUND error")
    def test_fragment_not_found(self) -> None:
        mock_expander = MagicMock()
        mock_expander.expand.return_value = None

        tool = ExpandTool(context_expander=mock_expander)

        with pytest.raises(ExpandToolError) as exc_info:
            tool(fragment_id="nonexistent", source_id="source-123")

        assert exc_info.value.error_code == "FRAGMENT_NOT_FOUND"
        assert "nonexistent" in str(exc_info.value.message)


class TestResolveToolNotFound:
    """Contract tests for resolve tool when URI cannot be resolved."""

    @pytest.mark.description("ResolveTool raises error for unresolvable URI")
    def test_uri_not_resolved(self) -> None:
        mock_client = MagicMock()
        mock_client.retrieve.return_value = []
        mock_client.scroll.return_value = ([], None)

        tool = ResolveTool(qdrant_client=mock_client)

        with pytest.raises(ValueError, match="Unable to resolve URI"):
            tool(uri="semantic://corpus/doc#nonexistent")


# =============================================================================
# Module-Level Instance Contract Tests
# =============================================================================


class TestModuleLevelInstances:
    """Contract tests verifying module-level tool instances."""

    @pytest.mark.description("search_tool is properly initialized")
    def test_search_tool_instance(self) -> None:
        assert isinstance(search_tool, SearchTool)
        assert search_tool.name == "search"
        assert search_tool.input_schema is not None

    @pytest.mark.description("ingest_tool is properly initialized")
    def test_ingest_tool_instance(self) -> None:
        assert isinstance(ingest_tool, IngestTool)
        assert ingest_tool.name == "ingest"
        assert ingest_tool.input_schema is not None

    @pytest.mark.description("get_ingestion_status_tool is properly initialized")
    def test_get_ingestion_status_tool_instance(self) -> None:
        assert isinstance(get_ingestion_status_tool, GetIngestionStatusTool)
        assert get_ingestion_status_tool.name == "get_ingestion_status"
        assert get_ingestion_status_tool.input_schema is not None

    @pytest.mark.description("expand_tool is properly initialized")
    def test_expand_tool_instance(self) -> None:
        assert isinstance(expand_tool, ExpandTool)
        assert expand_tool.name == "expand"
        assert expand_tool.input_schema is not None

    @pytest.mark.description("resolve_tool is properly initialized")
    def test_resolve_tool_instance(self) -> None:
        assert isinstance(resolve_tool, ResolveTool)
        assert resolve_tool.name == "resolve"
        assert resolve_tool.input_schema is not None

    @pytest.mark.description("list_corpora_tool is properly initialized")
    def test_list_corpora_tool_instance(self) -> None:
        assert isinstance(list_corpora_tool, ListCorporaTool)
        assert list_corpora_tool.name == "list_corpora"
        assert list_corpora_tool.input_schema is not None


# =============================================================================
# Cross-Tool Contract Consistency Tests
# =============================================================================


class TestCrossToolContracts:
    """Contract tests ensuring consistency across all tools."""

    ALL_TOOLS = [
        SearchTool(),
        IngestTool(),
        GetIngestionStatusTool(),
        ExpandTool(),
        ResolveTool(),
        ListCorporaTool(),
    ]

    @pytest.mark.description("All tools have name attribute")
    @pytest.mark.parametrize("tool", ALL_TOOLS)
    def test_all_tools_have_name(self, tool: Any) -> None:
        assert hasattr(tool, "name")
        assert isinstance(tool.name, str)
        assert len(tool.name) > 0

    @pytest.mark.description("All tools have description attribute")
    @pytest.mark.parametrize("tool", ALL_TOOLS)
    def test_all_tools_have_description(self, tool: Any) -> None:
        assert hasattr(tool, "description")
        assert isinstance(tool.description, str)
        assert len(tool.description) > 0

    @pytest.mark.description("All tools have input_schema property")
    @pytest.mark.parametrize("tool", ALL_TOOLS)
    def test_all_tools_have_input_schema(self, tool: Any) -> None:
        assert hasattr(tool, "input_schema")
        schema = tool.input_schema
        assert isinstance(schema, dict)
        assert schema.get("type") == "object"

    @pytest.mark.description("All tools are callable")
    @pytest.mark.parametrize("tool", ALL_TOOLS)
    def test_all_tools_callable(self, tool: Any) -> None:
        assert callable(tool)

    @pytest.mark.description("All schema string properties have type string")
    @pytest.mark.parametrize("tool", ALL_TOOLS)
    def test_string_properties_typed(self, tool: Any) -> None:
        for prop_name, prop in tool.input_schema.get("properties", {}).items():
            if "minLength" in prop:
                # If minLength is used, type should be string
                assert prop.get("type") == "string" or "oneOf" in prop
