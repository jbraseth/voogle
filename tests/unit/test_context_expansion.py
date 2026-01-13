# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for ContextExpander and related dataclasses."""
from unittest.mock import MagicMock, patch

import pytest
from voogle.services.expansion import (
    CHARS_PER_TOKEN,
    ContextExpander,
    ContextFragment,
    ExpandedFragment,
    ExpansionConfig,
)

pytestmark = pytest.mark.unit


class TestContextFragment:
    """Tests for ContextFragment dataclass."""

    @pytest.mark.description("ContextFragment with required fields creates successfully")
    def test_create_with_required_fields(self) -> None:
        fragment = ContextFragment(id="frag-1", text="Sample text")
        assert fragment.id == "frag-1"
        assert fragment.text == "Sample text"
        assert fragment.start_time is None
        assert fragment.end_time is None
        assert fragment.token_count == 0

    @pytest.mark.description("ContextFragment with all fields creates successfully")
    def test_create_with_all_fields(self) -> None:
        fragment = ContextFragment(
            id="frag-2",
            text="Another fragment",
            start_time=10.5,
            end_time=25.0,
            token_count=4,
        )
        assert fragment.id == "frag-2"
        assert fragment.text == "Another fragment"
        assert fragment.start_time == 10.5
        assert fragment.end_time == 25.0
        assert fragment.token_count == 4


class TestExpandedFragment:
    """Tests for ExpandedFragment dataclass."""

    @pytest.mark.description("ExpandedFragment with required fields creates successfully")
    def test_create_with_required_fields(self) -> None:
        expanded = ExpandedFragment(
            id="exp-1",
            text="Main fragment text",
            source_id="episode-123",
        )
        assert expanded.id == "exp-1"
        assert expanded.text == "Main fragment text"
        assert expanded.source_id == "episode-123"
        assert expanded.start_time is None
        assert expanded.end_time is None
        assert expanded.before_context == []
        assert expanded.after_context == []
        assert expanded.parent_id is None

    @pytest.mark.description("ExpandedFragment with context creates successfully")
    def test_create_with_context(self) -> None:
        before = [
            ContextFragment(id="b1", text="Before 1"),
            ContextFragment(id="b2", text="Before 2"),
        ]
        after = [
            ContextFragment(id="a1", text="After 1"),
        ]
        expanded = ExpandedFragment(
            id="exp-2",
            text="Main text",
            source_id="doc-456",
            start_time=100.0,
            end_time=120.0,
            before_context=before,
            after_context=after,
            parent_id="parent-789",
        )
        assert len(expanded.before_context) == 2
        assert len(expanded.after_context) == 1
        assert expanded.parent_id == "parent-789"
        assert expanded.start_time == 100.0
        assert expanded.end_time == 120.0


class TestExpansionConfig:
    """Tests for ExpansionConfig dataclass."""

    @pytest.mark.description("ExpansionConfig has sensible defaults")
    def test_default_values(self) -> None:
        config = ExpansionConfig()
        assert config.max_tokens_before == 500
        assert config.max_tokens_after == 500
        assert config.max_fragments_before == 5
        assert config.max_fragments_after == 5
        assert config.respect_boundaries is True
        assert config.include_parent is False
        assert config.collection_name is None

    @pytest.mark.description("ExpansionConfig can be customized")
    def test_custom_values(self) -> None:
        config = ExpansionConfig(
            max_tokens_before=1000,
            max_tokens_after=200,
            max_fragments_before=10,
            max_fragments_after=3,
            respect_boundaries=False,
            include_parent=True,
            collection_name="custom_collection",
        )
        assert config.max_tokens_before == 1000
        assert config.max_tokens_after == 200
        assert config.max_fragments_before == 10
        assert config.max_fragments_after == 3
        assert config.respect_boundaries is False
        assert config.include_parent is True
        assert config.collection_name == "custom_collection"


class TestContextExpander:
    """Tests for ContextExpander class."""

    @pytest.mark.description("ContextExpander initializes with defaults")
    def test_init_default(self) -> None:
        expander = ContextExpander()
        assert expander._qdrant_client is None
        assert expander._default_collection == "vectordb"

    @pytest.mark.description("ContextExpander initializes with custom values")
    def test_init_custom(self) -> None:
        mock_client = MagicMock()
        expander = ContextExpander(
            qdrant_client=mock_client,
            default_collection="my_collection",
        )
        assert expander._qdrant_client == mock_client
        assert expander._default_collection == "my_collection"

    @pytest.mark.description("ContextExpander __str__ returns string representation")
    def test_str(self) -> None:
        expander = ContextExpander()
        result = str(expander)
        assert "ContextExpander" in result
        assert "vectordb" in result

    @pytest.mark.description("ContextExpander __repr__ returns detailed representation")
    def test_repr(self) -> None:
        expander = ContextExpander()
        result = repr(expander)
        assert "ContextExpander" in result
        assert "qdrant_client" in result
        assert "default_collection" in result


class TestTokenEstimation:
    """Tests for token estimation functionality."""

    @pytest.mark.description("estimate_tokens uses character-based heuristic")
    def test_estimate_tokens_basic(self) -> None:
        expander = ContextExpander()
        # 4 chars per token is the default
        assert expander.estimate_tokens("abcd") == 1
        assert expander.estimate_tokens("abcdefgh") == 2
        assert expander.estimate_tokens("abcdefghijkl") == 3

    @pytest.mark.description("estimate_tokens returns at least 1")
    def test_estimate_tokens_minimum(self) -> None:
        expander = ContextExpander()
        assert expander.estimate_tokens("") == 1
        assert expander.estimate_tokens("a") == 1
        assert expander.estimate_tokens("ab") == 1

    @pytest.mark.description("estimate_tokens handles long text")
    def test_estimate_tokens_long_text(self) -> None:
        expander = ContextExpander()
        long_text = "word " * 100  # 500 chars
        expected = 500 // CHARS_PER_TOKEN
        assert expander.estimate_tokens(long_text) == expected


class TestExpandBatch:
    """Tests for batch expansion functionality."""

    @pytest.mark.description("expand_batch validates input lengths")
    def test_expand_batch_length_mismatch(self) -> None:
        expander = ContextExpander()
        with pytest.raises(ValueError, match="same length"):
            expander.expand_batch(
                fragment_ids=["f1", "f2"],
                source_ids=["s1"],
            )

    @pytest.mark.description("expand_batch calls expand for each pair")
    def test_expand_batch_calls_expand(self) -> None:
        mock_client = MagicMock()
        expander = ContextExpander(qdrant_client=mock_client)

        # Mock _get_fragment to return None (simulating not found)
        with patch.object(expander, "_get_fragment", return_value=None):
            results = expander.expand_batch(
                fragment_ids=["f1", "f2"],
                source_ids=["s1", "s2"],
            )
            assert len(results) == 2
            assert results[0] is None
            assert results[1] is None


class TestContextRetrieval:
    """Tests for context retrieval methods."""

    @pytest.mark.description("expand returns None when fragment not found")
    def test_expand_fragment_not_found(self) -> None:
        mock_client = MagicMock()
        mock_client.retrieve.return_value = []

        expander = ContextExpander(qdrant_client=mock_client)
        result = expander.expand("nonexistent", "source-1")
        assert result is None

    @pytest.mark.description("expand returns ExpandedFragment with context")
    def test_expand_with_context(self) -> None:
        mock_client = MagicMock()

        # Mock retrieve for the main fragment
        mock_client.retrieve.return_value = [
            MagicMock(
                payload={
                    "text": "Main fragment",
                    "start_time": 50.0,
                    "end_time": 60.0,
                }
            )
        ]

        # Mock scroll for before/after context
        mock_client.scroll.return_value = (
            [
                MagicMock(
                    id="ctx-1",
                    payload={
                        "text": "Context fragment",
                        "start_time": 40.0,
                        "end_time": 49.0,
                    },
                )
            ],
            None,
        )

        expander = ContextExpander(qdrant_client=mock_client)
        result = expander.expand("frag-1", "source-1")

        assert result is not None
        assert result.id == "frag-1"
        assert result.text == "Main fragment"
        assert result.source_id == "source-1"
        assert result.start_time == 50.0
        assert result.end_time == 60.0

    @pytest.mark.description("get_full_context_text combines all parts")
    def test_get_full_context_text(self) -> None:
        expander = ContextExpander()

        before = [
            ContextFragment(id="b1", text="Before 1"),
            ContextFragment(id="b2", text="Before 2"),
        ]
        after = [
            ContextFragment(id="a1", text="After 1"),
        ]
        expanded = ExpandedFragment(
            id="main",
            text="Main content",
            source_id="src",
            before_context=before,
            after_context=after,
        )

        result = expander.get_full_context_text(expanded)
        assert result == "Before 1 Before 2 Main content After 1"

    @pytest.mark.description("get_full_context_text uses custom separator")
    def test_get_full_context_text_custom_separator(self) -> None:
        expander = ContextExpander()

        expanded = ExpandedFragment(
            id="main",
            text="Main",
            source_id="src",
            before_context=[ContextFragment(id="b", text="Before")],
            after_context=[ContextFragment(id="a", text="After")],
        )

        result = expander.get_full_context_text(expanded, separator="\n\n")
        assert result == "Before\n\nMain\n\nAfter"

    @pytest.mark.description("get_context_token_count sums all tokens")
    def test_get_context_token_count(self) -> None:
        expander = ContextExpander()

        before = [
            ContextFragment(id="b1", text="word", token_count=1),
            ContextFragment(id="b2", text="words", token_count=2),
        ]
        after = [
            ContextFragment(id="a1", text="more", token_count=1),
        ]
        expanded = ExpandedFragment(
            id="main",
            text="main text here",  # 14 chars / 4 = 3 tokens
            source_id="src",
            before_context=before,
            after_context=after,
        )

        result = expander.get_context_token_count(expanded)
        # Main = 3 (14/4), Before = 1+2 = 3, After = 1
        assert result == 3 + 3 + 1


class TestBuildSourceFilter:
    """Tests for source filter building."""

    @pytest.mark.description("_build_source_filter returns empty when not respecting boundaries")
    def test_no_boundary_respect(self) -> None:
        expander = ContextExpander()
        result = expander._build_source_filter("source-1", respect_boundaries=False)
        assert result == []

    @pytest.mark.description("_build_source_filter uses episode for numeric source_id")
    def test_numeric_source_id(self) -> None:
        expander = ContextExpander()
        result = expander._build_source_filter("123", respect_boundaries=True)
        assert len(result) == 1
        assert result[0].key == "episode"

    @pytest.mark.description("_build_source_filter uses source_id for non-numeric")
    def test_string_source_id(self) -> None:
        expander = ContextExpander()
        result = expander._build_source_filter("doc-abc", respect_boundaries=True)
        assert len(result) == 1
        assert result[0].key == "source_id"


class TestCollectFragmentsWithTokenLimit:
    """Tests for token-limited fragment collection."""

    @pytest.mark.description("collects fragments within token limit")
    def test_within_token_limit(self) -> None:
        expander = ContextExpander()

        points = [
            MagicMock(id="p1", payload={"text": "Short"}),  # 5 chars = 1 token
            MagicMock(id="p2", payload={"text": "Also short"}),  # 10 chars = 2 tokens
        ]

        result = expander._collect_fragments_with_token_limit(
            points, max_tokens=100, max_fragments=10, reverse=False
        )

        assert len(result) == 2
        assert result[0].id == "p1"
        assert result[1].id == "p2"

    @pytest.mark.description("stops at token limit")
    def test_token_limit_exceeded(self) -> None:
        expander = ContextExpander()

        points = [
            MagicMock(id="p1", payload={"text": "12345678"}),  # 8 chars = 2 tokens
            MagicMock(id="p2", payload={"text": "12345678901234567890"}),  # 20 chars = 5 tokens
        ]

        result = expander._collect_fragments_with_token_limit(
            points, max_tokens=3, max_fragments=10, reverse=False
        )

        assert len(result) == 1
        assert result[0].id == "p1"

    @pytest.mark.description("stops at fragment limit")
    def test_fragment_limit(self) -> None:
        expander = ContextExpander()

        points = [
            MagicMock(id=f"p{i}", payload={"text": "text"})
            for i in range(10)
        ]

        result = expander._collect_fragments_with_token_limit(
            points, max_tokens=1000, max_fragments=3, reverse=False
        )

        assert len(result) == 3

    @pytest.mark.description("reverses result when requested")
    def test_reverse_order(self) -> None:
        expander = ContextExpander()

        points = [
            MagicMock(id="p1", payload={"text": "First"}),
            MagicMock(id="p2", payload={"text": "Second"}),
        ]

        result = expander._collect_fragments_with_token_limit(
            points, max_tokens=100, max_fragments=10, reverse=True
        )

        assert len(result) == 2
        assert result[0].id == "p2"
        assert result[1].id == "p1"


class TestParentChildTraversal:
    """Tests for parent-child fragment traversal."""

    @pytest.mark.description("get_parent returns None when fragment not found")
    def test_get_parent_fragment_not_found(self) -> None:
        mock_client = MagicMock()
        mock_client.retrieve.return_value = []

        expander = ContextExpander(qdrant_client=mock_client)
        result = expander.get_parent("child-1")
        assert result is None

    @pytest.mark.description("get_parent returns None when no parent_id")
    def test_get_parent_no_parent_id(self) -> None:
        mock_client = MagicMock()
        mock_client.retrieve.return_value = [
            MagicMock(payload={"text": "No parent"})
        ]

        expander = ContextExpander(qdrant_client=mock_client)
        result = expander.get_parent("child-1")
        assert result is None

    @pytest.mark.description("get_parent returns parent ContextFragment")
    def test_get_parent_success(self) -> None:
        mock_client = MagicMock()

        # First call returns child with parent_id
        # Second call returns parent
        mock_client.retrieve.side_effect = [
            [MagicMock(payload={"text": "Child", "parent_id": "parent-1"})],
            [MagicMock(payload={"text": "Parent text", "start_time": 0.0, "end_time": 100.0})],
        ]

        expander = ContextExpander(qdrant_client=mock_client)
        result = expander.get_parent("child-1")

        assert result is not None
        assert result.id == "parent-1"
        assert result.text == "Parent text"

    @pytest.mark.description("get_children returns empty list when no children")
    def test_get_children_empty(self) -> None:
        mock_client = MagicMock()
        mock_client.scroll.return_value = ([], None)

        expander = ContextExpander(qdrant_client=mock_client)
        result = expander.get_children("parent-1")
        assert result == []

    @pytest.mark.description("get_children returns children sorted by start_time")
    def test_get_children_sorted(self) -> None:
        mock_client = MagicMock()
        mock_client.scroll.return_value = (
            [
                MagicMock(id="c2", payload={"text": "Second", "start_time": 20.0}),
                MagicMock(id="c1", payload={"text": "First", "start_time": 10.0}),
                MagicMock(id="c3", payload={"text": "Third", "start_time": 30.0}),
            ],
            None,
        )

        expander = ContextExpander(qdrant_client=mock_client)
        result = expander.get_children("parent-1")

        assert len(result) == 3
        assert result[0].id == "c1"
        assert result[1].id == "c2"
        assert result[2].id == "c3"
