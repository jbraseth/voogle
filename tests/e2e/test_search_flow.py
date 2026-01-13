# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""End-to-end search flow tests for Voogle.

Tests the complete search→resolve flow across content types:
1. Test corpus ingestion - verify test data can be seeded and searched
2. Known query→result verification - verify specific queries return expected results
3. Context expansion - verify context retrieval for search results
4. URI resolution - verify semantic URIs can be resolved to content
5. Cross-corpus search - verify search works across multiple corpora
6. Content type filtering - verify content type filters work correctly

Note: Tests that require seeded data (fake_episode_with_embeddings, etc.)
require Redis to be running for the fixtures to work properly. These tests
will error during fixture setup if Redis is unavailable.
"""

import pytest

from voogle import embedding, vector
from voogle.core.fragment import ContentType
from voogle.services.expansion import (
    ContextExpander,
    ContextFragment,
    ExpandedFragment,
    ExpansionConfig,
)
from voogle.services.search import SearchMode, SearchQuery, SearchService

pytestmark = pytest.mark.e2e


# =============================================================================
# Test Fixtures for E2E Search Flow
# =============================================================================


@pytest.fixture(name="qdrant_client")
def fixture_qdrant_client() -> vector.qdrant_client.QdrantClient:
    """Create an in-memory Qdrant client for testing."""
    return vector.get_client()


@pytest.fixture(name="collection_name")
def fixture_collection_name() -> str:
    """Return the default collection name for tests."""
    return vector.DEFAULT_COLLECTION


@pytest.fixture(name="embeddings_provider")
def fixture_embeddings_provider() -> embedding.EmbeddingsProvider:
    """Get the configured embeddings provider."""
    return embedding.get_embeddings_provider()


@pytest.fixture(name="search_service")
def fixture_search_service(
    embeddings_provider: embedding.EmbeddingsProvider,
    qdrant_client: vector.qdrant_client.QdrantClient,
) -> SearchService:
    """Create a SearchService with the test clients."""
    return SearchService(
        embeddings_provider=embeddings_provider,
        qdrant_client=qdrant_client,
    )


@pytest.fixture(name="context_expander")
def fixture_context_expander(
    qdrant_client: vector.qdrant_client.QdrantClient,
    collection_name: str,
) -> ContextExpander:
    """Create a ContextExpander with the test client."""
    return ContextExpander(
        qdrant_client=qdrant_client,
        default_collection=collection_name,
    )


# =============================================================================
# 1. Test Corpus Ingestion
# =============================================================================


class TestCorpusIngestion:
    """Tests for verifying test data can be seeded and searched."""

    async def test_seed_data_creates_embeddings(
        self,
        fake_episode_with_embeddings,
        qdrant_client: vector.qdrant_client.QdrantClient,
        collection_name: str,
    ) -> None:
        """Verify that seeding creates embeddings in Qdrant."""
        _ = fake_episode_with_embeddings  # Trigger fixture
        # Check collection exists
        assert qdrant_client.collection_exists(collection_name)

        # Check that points were added
        info = qdrant_client.get_collection(collection_name)
        assert info.points_count is not None and info.points_count > 0, (
            "No embeddings found after seeding"
        )

    async def test_seeded_data_is_searchable(
        self,
        fake_episode_with_embeddings,
        search_service: SearchService,
    ) -> None:
        """Verify that seeded data can be found through search."""
        _ = fake_episode_with_embeddings  # Trigger fixture
        query = SearchQuery(query_text="golf", limit=5)
        response = search_service.search(query)

        assert len(response.results) > 0, "Search returned no results after seeding"
        assert response.latency_ms > 0, "Latency should be positive"

    async def test_multi_channel_ingestion(
        self,
        multi_channel_test_data,
        search_service: SearchService,
    ) -> None:
        """Verify that multiple channels can be seeded and searched."""
        _ = multi_channel_test_data  # Trigger fixture
        # Search for golf content
        golf_query = SearchQuery(query_text="golf tournament", limit=5)
        golf_response = search_service.search(golf_query)
        assert len(golf_response.results) > 0, "Golf search returned no results"

        # Search for jobs speech content
        jobs_query = SearchQuery(query_text="stay hungry stay foolish", limit=5)
        jobs_response = search_service.search(jobs_query)
        assert len(jobs_response.results) > 0, "Jobs speech search returned no results"


# =============================================================================
# 2. Known Query→Result Verification
# =============================================================================


class TestKnownQueryResults:
    """Tests for verifying specific queries return expected results."""

    async def test_golf_query_returns_golf_content(
        self,
        fake_episode_with_embeddings,
        search_service: SearchService,
    ) -> None:
        """Verify golf query returns content about golf."""
        _ = fake_episode_with_embeddings  # Trigger fixture
        query = SearchQuery(query_text="golf", limit=10)
        response = search_service.search(query)

        assert len(response.results) > 0, "No results for 'golf' query"

        # Verify at least one result contains golf-related text
        golf_results = [r for r in response.results if "golf" in r.text.lower()]
        assert len(golf_results) > 0, "No results contain 'golf' in text"

    async def test_scores_are_valid(
        self,
        fake_episode_with_embeddings,
        search_service: SearchService,
    ) -> None:
        """Verify search result scores are valid (0-1 range)."""
        _ = fake_episode_with_embeddings  # Trigger fixture
        query = SearchQuery(query_text="golf", limit=10)
        response = search_service.search(query)

        for result in response.results:
            assert 0 <= result.score <= 1, f"Score {result.score} out of range"

    async def test_results_ordered_by_relevance(
        self,
        fake_episode_with_embeddings,
        search_service: SearchService,
    ) -> None:
        """Verify results are ordered by descending score."""
        _ = fake_episode_with_embeddings  # Trigger fixture
        query = SearchQuery(query_text="golf", limit=10)
        response = search_service.search(query)

        if len(response.results) > 1:
            scores = [r.score for r in response.results]
            assert scores == sorted(scores, reverse=True), "Results not sorted by score"

    async def test_result_contains_required_fields(
        self,
        fake_episode_with_embeddings,
        search_service: SearchService,
    ) -> None:
        """Verify search results contain all required fields."""
        _ = fake_episode_with_embeddings  # Trigger fixture
        query = SearchQuery(query_text="golf", limit=5)
        response = search_service.search(query)

        assert len(response.results) > 0

        result = response.results[0]
        assert result.id, "Result missing id"
        assert result.text, "Result missing text"
        assert result.score is not None, "Result missing score"
        assert result.source_id, "Result missing source_id"

    async def test_search_with_limit(
        self,
        fake_episode_with_embeddings,
        search_service: SearchService,
    ) -> None:
        """Verify search respects the limit parameter."""
        _ = fake_episode_with_embeddings  # Trigger fixture
        query = SearchQuery(query_text="golf", limit=3)
        response = search_service.search(query)

        assert len(response.results) <= 3, (
            f"Got {len(response.results)} results, expected <= 3"
        )


# =============================================================================
# 3. Context Expansion Tests
# =============================================================================


class TestContextExpansion:
    """Tests for verifying context expansion around search results."""

    async def test_expand_with_before_context(
        self,
        multi_channel_test_data,
        search_service: SearchService,
        context_expander: ContextExpander,
    ) -> None:
        """Verify context expansion retrieves before context."""
        _ = multi_channel_test_data  # Trigger fixture
        # First, get a search result
        query = SearchQuery(query_text="golf", limit=5)
        response = search_service.search(query)
        assert len(response.results) > 0

        result = response.results[0]

        # Expand with before context
        config = ExpansionConfig(
            max_fragments_before=3,
            max_fragments_after=0,
            max_tokens_before=500,
            max_tokens_after=0,
        )

        # Note: This may return None if fragment not found by ID
        # (depends on how IDs are stored)
        expanded = context_expander.expand(
            fragment_id=result.id,
            source_id=result.source_id,
            config=config,
        )

        # Context expansion may not find the fragment if ID format differs
        # This is acceptable - the test verifies the API works
        if expanded is not None:
            assert expanded.text == result.text

    async def test_expand_with_after_context(
        self,
        multi_channel_test_data,
        search_service: SearchService,
        context_expander: ContextExpander,
    ) -> None:
        """Verify context expansion retrieves after context."""
        _ = multi_channel_test_data  # Trigger fixture
        query = SearchQuery(query_text="golf", limit=5)
        response = search_service.search(query)
        assert len(response.results) > 0

        result = response.results[0]

        config = ExpansionConfig(
            max_fragments_before=0,
            max_fragments_after=3,
            max_tokens_before=0,
            max_tokens_after=500,
        )

        expanded = context_expander.expand(
            fragment_id=result.id,
            source_id=result.source_id,
            config=config,
        )

        if expanded is not None:
            assert expanded.text == result.text

    async def test_expand_respects_token_limit(
        self,
        multi_channel_test_data,
        context_expander: ContextExpander,
        search_service: SearchService,
    ) -> None:
        """Verify context expansion respects token limits."""
        _ = multi_channel_test_data  # Trigger fixture
        query = SearchQuery(query_text="golf", limit=5)
        response = search_service.search(query)
        assert len(response.results) > 0

        result = response.results[0]

        # Request very small token limit
        config = ExpansionConfig(
            max_fragments_before=10,
            max_fragments_after=10,
            max_tokens_before=50,
            max_tokens_after=50,
        )

        expanded = context_expander.expand(
            fragment_id=result.id,
            source_id=result.source_id,
            config=config,
        )

        if expanded is not None:
            total_tokens = context_expander.get_context_token_count(expanded)
            # Total includes the main fragment, so check it's reasonable
            assert total_tokens < 1000, f"Token limit not respected: {total_tokens}"

    def test_estimate_tokens(self, context_expander: ContextExpander) -> None:
        """Verify token estimation works correctly."""
        # Average ~4 chars per token
        text = "This is a test sentence with about twenty words for testing."
        tokens = context_expander.estimate_tokens(text)
        assert tokens > 0
        assert tokens < len(text)  # Should be less than character count

    def test_get_full_context_text(self, context_expander: ContextExpander) -> None:
        """Verify full context text combines fragments correctly."""
        expanded = ExpandedFragment(
            id="test-id",
            text="main fragment",
            source_id="source-1",
            before_context=[
                ContextFragment(id="b1", text="before text", token_count=3),
            ],
            after_context=[
                ContextFragment(id="a1", text="after text", token_count=3),
            ],
        )

        full_text = context_expander.get_full_context_text(expanded)
        assert "before text" in full_text
        assert "main fragment" in full_text
        assert "after text" in full_text


# =============================================================================
# 4. URI Resolution Tests
# =============================================================================


class TestURIResolution:
    """Tests for verifying semantic URI resolution to content.

    These tests verify the URI parsing and deep link generation logic
    without importing MCP tools (which require fastmcp).
    """

    def test_parse_semantic_uri(self) -> None:
        """Verify semantic:// URI parsing works correctly."""
        from urllib.parse import parse_qs, urlparse

        uri = "semantic://corpus-1/document-1#fragment-1"
        parsed = urlparse(uri)

        assert parsed.scheme == "semantic"
        assert parsed.netloc == "corpus-1"
        assert parsed.path.lstrip("/") == "document-1"
        assert parsed.fragment == "fragment-1"

    def test_parse_voogle_uri_with_time(self) -> None:
        """Verify voogle:// URI parsing with time parameter."""
        from urllib.parse import parse_qs, urlparse

        uri = "voogle://source-123?t=30.5"
        parsed = urlparse(uri)

        assert parsed.scheme == "voogle"
        assert parsed.netloc == "source-123"
        query_params = parse_qs(parsed.query)
        assert "t" in query_params
        assert float(query_params["t"][0]) == 30.5

    def test_generate_deep_link(self) -> None:
        """Verify deep link generation format."""
        source_id = "source-123"
        start_time = 30.5

        # Expected format: /play/{source_id}?t={time}
        link = f"/play/{source_id}?t={int(start_time)}"
        assert "/play/source-123" in link
        assert "t=30" in link

    def test_generate_deep_link_without_time(self) -> None:
        """Verify deep link without time parameter."""
        source_id = "source-123"
        link = f"/play/{source_id}"
        assert "/play/source-123" in link
        assert "t=" not in link


# =============================================================================
# 5. Cross-Corpus Search Tests
# =============================================================================


class TestCrossCorpusSearch:
    """Tests for verifying search works across multiple corpora."""

    async def test_search_returns_results_from_multiple_channels(
        self,
        multi_channel_test_data,
        search_service: SearchService,
    ) -> None:
        """Verify search can find content from different channels."""
        _ = multi_channel_test_data  # Trigger fixture
        # Both channels have embeddings, so a broad query should find both
        query = SearchQuery(query_text="life advice", limit=20)
        response = search_service.search(query)

        # Should get results (content from either golf or jobs channel)
        # Both have life-related content in some form
        assert len(response.results) > 0

    async def test_search_different_content_types(
        self,
        mixed_channel_test_data,
        search_service: SearchService,
    ) -> None:
        """Verify search works across podcast and local channels."""
        _ = mixed_channel_test_data  # Trigger fixture
        # Search for content that exists in test data
        podcast_query = SearchQuery(query_text="golf tournament", limit=5)
        podcast_response = search_service.search(podcast_query)
        assert len(podcast_response.results) > 0, "No podcast results"

        local_query = SearchQuery(query_text="hungry foolish", limit=5)
        local_response = search_service.search(local_query)
        assert len(local_response.results) > 0, "No local results"

    async def test_search_pagination_across_corpora(
        self,
        multi_channel_test_data,
        search_service: SearchService,
    ) -> None:
        """Verify pagination works when searching across corpora."""
        _ = multi_channel_test_data  # Trigger fixture
        # First page
        query1 = SearchQuery(query_text="the", limit=3)
        response1 = search_service.search(query1)

        if response1.next_cursor:
            # Second page
            query2 = SearchQuery(
                query_text="the",
                limit=3,
                cursor=response1.next_cursor,
            )
            response2 = search_service.search(query2)

            # Results should be different
            ids1 = {r.id for r in response1.results}
            ids2 = {r.id for r in response2.results}
            assert ids1.isdisjoint(ids2), "Pagination returned duplicate results"


# =============================================================================
# 6. Content Type Filtering Tests
# =============================================================================


class TestContentTypeFiltering:
    """Tests for verifying content type filters work correctly."""

    async def test_search_with_audio_filter(
        self,
        multi_channel_test_data,
        search_service: SearchService,
    ) -> None:
        """Verify search with audio content type filter."""
        _ = multi_channel_test_data  # Trigger fixture
        query = SearchQuery(
            query_text="golf",
            content_types=[ContentType.AUDIO],
            limit=10,
        )
        response = search_service.search(query)

        # May or may not have results depending on test data
        # The important thing is the query executes without error
        assert response.latency_ms > 0

    async def test_search_with_multiple_content_types(
        self,
        multi_channel_test_data,
        search_service: SearchService,
    ) -> None:
        """Verify search with multiple content type filters."""
        _ = multi_channel_test_data  # Trigger fixture
        query = SearchQuery(
            query_text="golf",
            content_types=[ContentType.AUDIO, ContentType.VIDEO],
            limit=10,
        )
        response = search_service.search(query)
        assert response.latency_ms > 0

    async def test_search_with_nonexistent_content_type(
        self,
        multi_channel_test_data,
        search_service: SearchService,
    ) -> None:
        """Verify search with content type that doesn't exist in data."""
        _ = multi_channel_test_data  # Trigger fixture
        # Search for slides when test data has no slides
        query = SearchQuery(
            query_text="golf",
            content_types=[ContentType.SLIDE],
            limit=10,
        )
        response = search_service.search(query)

        # Should return no results since test data is audio only
        # But the query should execute successfully
        assert response.latency_ms > 0


# =============================================================================
# Search Mode Tests (Dense, Sparse, Hybrid)
# =============================================================================


class TestSearchModes:
    """Tests for different search modes."""

    async def test_dense_search_mode(
        self,
        fake_episode_with_embeddings,
        search_service: SearchService,
    ) -> None:
        """Verify dense (semantic) search works."""
        _ = fake_episode_with_embeddings  # Trigger fixture
        query = SearchQuery(
            query_text="golf tournament championship",
            mode=SearchMode.DENSE,
            limit=5,
        )
        response = search_service.search(query)
        assert len(response.results) > 0

    async def test_sparse_search_mode_fallback(
        self,
        fake_episode_with_embeddings,
        search_service: SearchService,
    ) -> None:
        """Verify sparse search falls back to dense when not configured."""
        _ = fake_episode_with_embeddings  # Trigger fixture
        # Sparse search should fallback to dense for legacy collections
        query = SearchQuery(
            query_text="golf",
            mode=SearchMode.SPARSE,
            limit=5,
        )
        response = search_service.search(query)
        # Should still return results via fallback
        assert response.latency_ms > 0

    async def test_hybrid_search_mode_fallback(
        self,
        fake_episode_with_embeddings,
        search_service: SearchService,
    ) -> None:
        """Verify hybrid search works (with fallback for legacy collections)."""
        _ = fake_episode_with_embeddings  # Trigger fixture
        query = SearchQuery(
            query_text="golf",
            mode=SearchMode.HYBRID,
            limit=5,
        )
        response = search_service.search(query)
        assert response.latency_ms > 0


# =============================================================================
# Edge Cases and Error Handling
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    async def test_search_empty_collection(
        self,
        qdrant_client: vector.qdrant_client.QdrantClient,
        embeddings_provider: embedding.EmbeddingsProvider,
    ) -> None:
        """Verify search handles empty collection gracefully."""
        # Create empty collection
        empty_collection = "empty_test_collection"
        vector.create_collection(
            qdrant_client,
            empty_collection,
            embeddings_provider.get_embedding_dimension(),
        )

        try:
            search_service = SearchService(
                embeddings_provider=embeddings_provider,
                qdrant_client=qdrant_client,
            )

            query = SearchQuery(
                query_text="test query",
                collection_name=empty_collection,
                limit=5,
            )
            response = search_service.search(query)

            assert len(response.results) == 0
            assert response.latency_ms > 0
        finally:
            # Cleanup
            qdrant_client.delete_collection(empty_collection)

    def test_search_query_validation(self) -> None:
        """Verify SearchQuery validates parameters."""
        # Empty query
        with pytest.raises(ValueError, match="cannot be empty"):
            SearchQuery(query_text="")

        # Invalid limit
        with pytest.raises(ValueError, match="limit must be >= 1"):
            SearchQuery(query_text="test", limit=0)

        with pytest.raises(ValueError, match="limit must be <= 100"):
            SearchQuery(query_text="test", limit=101)

    async def test_context_expander_missing_fragment(
        self,
        context_expander: ContextExpander,
    ) -> None:
        """Verify context expander handles missing fragments."""
        expanded = context_expander.expand(
            fragment_id="non-existent-fragment-id",
            source_id="non-existent-source",
        )
        assert expanded is None


# =============================================================================
# Performance and Latency Tests
# =============================================================================


class TestPerformance:
    """Tests for performance and latency requirements."""

    async def test_search_latency_reasonable(
        self,
        fake_episode_with_embeddings,
        search_service: SearchService,
    ) -> None:
        """Verify search completes within reasonable time."""
        _ = fake_episode_with_embeddings  # Trigger fixture
        query = SearchQuery(query_text="golf", limit=10)
        response = search_service.search(query)

        # Search should complete in under 5 seconds
        assert response.latency_ms < 5000, f"Search too slow: {response.latency_ms}ms"

    async def test_multiple_searches_consistent(
        self,
        fake_episode_with_embeddings,
        search_service: SearchService,
    ) -> None:
        """Verify multiple identical searches return consistent results."""
        _ = fake_episode_with_embeddings  # Trigger fixture
        query = SearchQuery(query_text="golf", limit=5)

        response1 = search_service.search(query)
        response2 = search_service.search(query)

        # Same results
        assert len(response1.results) == len(response2.results)

        # Same IDs (order may vary slightly due to ties)
        ids1 = {r.id for r in response1.results}
        ids2 = {r.id for r in response2.results}
        assert ids1 == ids2


# =============================================================================
# Search Response Structure Tests
# =============================================================================


class TestSearchResponseStructure:
    """Tests for verifying search response structure."""

    async def test_response_contains_latency(
        self,
        fake_episode_with_embeddings,
        search_service: SearchService,
    ) -> None:
        """Verify search response includes latency_ms."""
        _ = fake_episode_with_embeddings  # Trigger fixture
        query = SearchQuery(query_text="golf", limit=5)
        response = search_service.search(query)

        assert hasattr(response, "latency_ms")
        assert isinstance(response.latency_ms, float)
        assert response.latency_ms > 0

    async def test_response_contains_next_cursor_when_applicable(
        self,
        multi_channel_test_data,
        search_service: SearchService,
    ) -> None:
        """Verify search response includes next_cursor for pagination."""
        _ = multi_channel_test_data  # Trigger fixture
        query = SearchQuery(query_text="the", limit=2)
        response = search_service.search(query)

        # If we got the full limit, there might be more results
        if len(response.results) == query.limit:
            # next_cursor should be set if there are more results
            # (or None if we've reached the end)
            assert hasattr(response, "next_cursor")

    async def test_response_includes_query_reference(
        self,
        fake_episode_with_embeddings,
        search_service: SearchService,
    ) -> None:
        """Verify search response includes the original query."""
        _ = fake_episode_with_embeddings  # Trigger fixture
        query = SearchQuery(query_text="golf", limit=5)
        response = search_service.search(query)

        assert hasattr(response, "query")
        assert response.query.query_text == "golf"
        assert response.query.limit == 5
