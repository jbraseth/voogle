# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for MCP list_corpora tool."""

import pytest

from voogle.core import ContentType, Corpus
from voogle.mcp.tools.corpora import ListCorporaTool, list_corpora_tool
from voogle.services.corpus_service import CorpusService

pytestmark = pytest.mark.unit


class TestListCorporaToolBasic:
    """Basic tests for ListCorporaTool."""

    @pytest.mark.description("list_corpora_tool has correct name and description")
    def test_tool_metadata(self) -> None:
        tool = ListCorporaTool()
        assert tool.name == "list_corpora"
        assert "corpus" in tool.description.lower()
        assert "list" in tool.description.lower()

    @pytest.mark.description("list_corpora_tool has valid input schema")
    def test_input_schema(self) -> None:
        tool = ListCorporaTool()
        schema = tool.input_schema
        assert schema["type"] == "object"
        assert "cursor" in schema["properties"]
        assert "include_stats" in schema["properties"]
        assert "limit" in schema["properties"]
        assert schema["required"] == []

    @pytest.mark.description("list_corpora_tool input_schema has correct types")
    def test_input_schema_types(self) -> None:
        schema = list_corpora_tool.input_schema
        assert schema["properties"]["cursor"]["type"] == "string"
        assert schema["properties"]["include_stats"]["type"] == "boolean"
        assert schema["properties"]["limit"]["type"] == "integer"

    @pytest.mark.description("module-level list_corpora_tool is ListCorporaTool instance")
    def test_module_level_instance(self) -> None:
        assert isinstance(list_corpora_tool, ListCorporaTool)


class TestListCorporaToolEmpty:
    """Tests for ListCorporaTool with empty corpus service."""

    @pytest.mark.description("list_corpora returns empty list when no corpora exist")
    def test_empty_list(self) -> None:
        service = CorpusService()
        tool = ListCorporaTool(corpus_service=service)
        result = tool()
        assert result["corpora"] == []
        assert result["total_count"] == 0
        assert result["next_cursor"] is None


class TestListCorporaToolWithData:
    """Tests for ListCorporaTool with corpus data."""

    @pytest.fixture
    def corpus_service(self) -> CorpusService:
        """Create a corpus service with test data."""
        service = CorpusService()
        service.create(
            id="corpus-1",
            name="Podcasts",
            description="Audio podcast episodes",
            content_types=[ContentType.AUDIO],
        )
        service.create(
            id="corpus-2",
            name="Videos",
            description="Video content collection",
            content_types=[ContentType.VIDEO],
        )
        service.create(
            id="corpus-3",
            name="Documents",
            description="Text documents",
            content_types=[ContentType.DOCUMENT],
        )
        return service

    @pytest.mark.description("list_corpora returns all corpora without stats")
    def test_list_without_stats(self, corpus_service: CorpusService) -> None:
        tool = ListCorporaTool(corpus_service=corpus_service)
        result = tool()
        assert result["total_count"] == 3
        assert len(result["corpora"]) == 3
        assert result["next_cursor"] is None

        # Check basic fields are present
        corpus = result["corpora"][0]
        assert "id" in corpus
        assert "name" in corpus
        assert "description" in corpus
        # Stats should not be present
        assert "document_count" not in corpus
        assert "last_updated" not in corpus

    @pytest.mark.description("list_corpora returns corpora with stats when requested")
    def test_list_with_stats(self, corpus_service: CorpusService) -> None:
        tool = ListCorporaTool(corpus_service=corpus_service)
        result = tool(include_stats=True)
        assert result["total_count"] == 3

        # Check stats are present
        corpus = result["corpora"][0]
        assert "document_count" in corpus
        assert "last_updated" in corpus
        assert isinstance(corpus["document_count"], int)
        assert isinstance(corpus["last_updated"], str)

    @pytest.mark.description("list_corpora returns correct corpus data")
    def test_corpus_data(self, corpus_service: CorpusService) -> None:
        tool = ListCorporaTool(corpus_service=corpus_service)
        result = tool()

        ids = [c["id"] for c in result["corpora"]]
        assert "corpus-1" in ids
        assert "corpus-2" in ids
        assert "corpus-3" in ids

        # Find podcasts corpus
        podcasts = next(c for c in result["corpora"] if c["id"] == "corpus-1")
        assert podcasts["name"] == "Podcasts"
        assert podcasts["description"] == "Audio podcast episodes"


class TestListCorporaToolPagination:
    """Tests for cursor-based pagination."""

    @pytest.fixture
    def corpus_service(self) -> CorpusService:
        """Create a corpus service with many corpora for pagination testing."""
        service = CorpusService()
        for i in range(25):
            service.create(
                id=f"corpus-{i:02d}",
                name=f"Corpus {i}",
                description=f"Test corpus number {i}",
            )
        return service

    @pytest.mark.description("list_corpora paginates with limit")
    def test_pagination_limit(self, corpus_service: CorpusService) -> None:
        tool = ListCorporaTool(corpus_service=corpus_service)
        result = tool(limit=10)
        assert len(result["corpora"]) == 10
        assert result["total_count"] == 25
        assert result["next_cursor"] is not None

    @pytest.mark.description("list_corpora cursor returns next page")
    def test_pagination_cursor(self, corpus_service: CorpusService) -> None:
        tool = ListCorporaTool(corpus_service=corpus_service)

        # Get first page
        page1 = tool(limit=10)
        assert len(page1["corpora"]) == 10
        first_page_ids = [c["id"] for c in page1["corpora"]]

        # Get second page
        page2 = tool(limit=10, cursor=page1["next_cursor"])
        assert len(page2["corpora"]) == 10
        second_page_ids = [c["id"] for c in page2["corpora"]]

        # Pages should have different corpora
        assert set(first_page_ids).isdisjoint(set(second_page_ids))

    @pytest.mark.description("list_corpora last page has no next_cursor")
    def test_pagination_last_page(self, corpus_service: CorpusService) -> None:
        tool = ListCorporaTool(corpus_service=corpus_service)

        # Get first page
        page1 = tool(limit=20)
        assert page1["next_cursor"] is not None

        # Get last page
        page2 = tool(limit=20, cursor=page1["next_cursor"])
        assert len(page2["corpora"]) == 5  # 25 - 20 = 5
        assert page2["next_cursor"] is None

    @pytest.mark.description("list_corpora invalid cursor raises ValueError")
    def test_invalid_cursor(self, corpus_service: CorpusService) -> None:
        tool = ListCorporaTool(corpus_service=corpus_service)
        with pytest.raises(ValueError, match="Invalid cursor"):
            tool(cursor="invalid-cursor-data")


class TestListCorporaToolValidation:
    """Tests for input validation."""

    @pytest.mark.description("list_corpora rejects limit below minimum")
    def test_limit_too_low(self) -> None:
        tool = ListCorporaTool()
        with pytest.raises(ValueError, match="limit must be between"):
            tool(limit=0)

    @pytest.mark.description("list_corpora rejects limit above maximum")
    def test_limit_too_high(self) -> None:
        tool = ListCorporaTool()
        with pytest.raises(ValueError, match="limit must be between"):
            tool(limit=101)

    @pytest.mark.description("list_corpora accepts valid limit")
    def test_valid_limit(self) -> None:
        service = CorpusService()
        tool = ListCorporaTool(corpus_service=service)
        result = tool(limit=50)
        assert result["total_count"] == 0


class TestListCorporaToolCaching:
    """Tests for statistics caching."""

    @pytest.mark.description("list_corpora caches stats between calls")
    def test_stats_caching(self) -> None:
        service = CorpusService()
        service.create(id="corpus-1", name="Test Corpus", description="Test")
        tool = ListCorporaTool(corpus_service=service)

        # First call populates cache
        result1 = tool(include_stats=True)
        assert "corpus-1" in tool._stats_cache

        # Verify cached values
        cached = tool._get_cached_stats("corpus-1")
        assert cached is not None
        assert "document_count" in cached
        assert "last_updated" in cached

    @pytest.mark.description("list_corpora uses cached stats on subsequent calls")
    def test_uses_cached_stats(self) -> None:
        service = CorpusService()
        service.create(id="corpus-1", name="Test Corpus", description="Test")
        tool = ListCorporaTool(corpus_service=service)

        # First call
        result1 = tool(include_stats=True)
        last_updated1 = result1["corpora"][0]["last_updated"]

        # Update corpus
        service.update("corpus-1", document_count=100)

        # Second call should use cached value
        result2 = tool(include_stats=True)
        last_updated2 = result2["corpora"][0]["last_updated"]

        # Should be same because of caching
        assert last_updated1 == last_updated2
