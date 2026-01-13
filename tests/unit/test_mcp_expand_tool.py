# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for MCP expand tool."""
from unittest.mock import MagicMock

import pytest

from voogle.mcp.tools.expand import (
    ExpandContextFragment,
    ExpandDirection,
    ExpandTool,
    ExpandToolError,
    ExpandToolOutput,
    expand_tool,
)
from voogle.services.expansion import ContextFragment, ExpandedFragment

pytestmark = pytest.mark.unit


class TestExpandDirection:
    """Tests for ExpandDirection enum."""

    @pytest.mark.description("ExpandDirection has expected values")
    def test_direction_values(self) -> None:
        assert ExpandDirection.BEFORE.value == "before"
        assert ExpandDirection.AFTER.value == "after"
        assert ExpandDirection.BOTH.value == "both"


class TestExpandContextFragment:
    """Tests for ExpandContextFragment dataclass."""

    @pytest.mark.description("ExpandContextFragment with required fields")
    def test_required_fields(self) -> None:
        fragment = ExpandContextFragment(
            id="frag-1",
            text="Test text",
        )
        assert fragment.id == "frag-1"
        assert fragment.text == "Test text"
        assert fragment.start_time is None
        assert fragment.end_time is None
        assert fragment.token_count == 0

    @pytest.mark.description("ExpandContextFragment with all fields")
    def test_all_fields(self) -> None:
        fragment = ExpandContextFragment(
            id="frag-2",
            text="Full fragment",
            start_time=10.5,
            end_time=25.0,
            token_count=15,
        )
        assert fragment.id == "frag-2"
        assert fragment.text == "Full fragment"
        assert fragment.start_time == 10.5
        assert fragment.end_time == 25.0
        assert fragment.token_count == 15


class TestExpandToolOutput:
    """Tests for ExpandToolOutput dataclass."""

    @pytest.mark.description("ExpandToolOutput structure")
    def test_output_structure(self) -> None:
        before = [ExpandContextFragment(id="b1", text="Before text")]
        after = [ExpandContextFragment(id="a1", text="After text")]

        output = ExpandToolOutput(
            fragment_id="main-frag",
            original_text="Original text",
            before_context=before,
            after_context=after,
            combined_text="Before text Original text After text",
            total_tokens=25,
            at_document_start=False,
            at_document_end=False,
            source_id="source-123",
        )

        assert output.fragment_id == "main-frag"
        assert output.original_text == "Original text"
        assert len(output.before_context) == 1
        assert len(output.after_context) == 1
        assert output.combined_text == "Before text Original text After text"
        assert output.total_tokens == 25
        assert output.at_document_start is False
        assert output.at_document_end is False
        assert output.source_id == "source-123"


class TestExpandToolError:
    """Tests for ExpandToolError exception."""

    @pytest.mark.description("ExpandToolError has message and error_code")
    def test_error_attributes(self) -> None:
        error = ExpandToolError(
            message="Fragment not found",
            error_code="FRAGMENT_NOT_FOUND",
        )
        assert str(error) == "Fragment not found"
        assert error.message == "Fragment not found"
        assert error.error_code == "FRAGMENT_NOT_FOUND"


class TestExpandTool:
    """Tests for ExpandTool class."""

    @pytest.mark.description("ExpandTool has correct name and description")
    def test_name_and_description(self) -> None:
        tool = ExpandTool()
        assert tool.name == "expand"
        assert "expand" in tool.description.lower()
        assert "context" in tool.description.lower()

    @pytest.mark.description("ExpandTool input_schema is valid JSON Schema")
    def test_input_schema_structure(self) -> None:
        tool = ExpandTool()
        schema = tool.input_schema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema
        assert "fragment_id" in schema["required"]
        assert "source_id" in schema["required"]

    @pytest.mark.description("ExpandTool input_schema has fragment_id property")
    def test_input_schema_fragment_id(self) -> None:
        tool = ExpandTool()
        schema = tool.input_schema
        prop = schema["properties"]["fragment_id"]
        assert prop["type"] == "string"
        assert prop["minLength"] == 1

    @pytest.mark.description("ExpandTool input_schema has source_id property")
    def test_input_schema_source_id(self) -> None:
        tool = ExpandTool()
        schema = tool.input_schema
        prop = schema["properties"]["source_id"]
        assert prop["type"] == "string"
        assert prop["minLength"] == 1

    @pytest.mark.description("ExpandTool input_schema has direction property")
    def test_input_schema_direction(self) -> None:
        tool = ExpandTool()
        schema = tool.input_schema
        prop = schema["properties"]["direction"]
        assert prop["type"] == "string"
        assert prop["enum"] == ["before", "after", "both"]
        assert prop["default"] == "both"

    @pytest.mark.description("ExpandTool input_schema has tokens property")
    def test_input_schema_tokens(self) -> None:
        tool = ExpandTool()
        schema = tool.input_schema
        prop = schema["properties"]["tokens"]
        assert prop["type"] == "integer"
        assert prop["minimum"] == 1
        assert prop["maximum"] == 2000
        assert prop["default"] == 500

    @pytest.mark.description("ExpandTool input_schema has max_fragments property")
    def test_input_schema_max_fragments(self) -> None:
        tool = ExpandTool()
        schema = tool.input_schema
        prop = schema["properties"]["max_fragments"]
        assert prop["type"] == "integer"
        assert prop["minimum"] == 1
        assert prop["maximum"] == 20
        assert prop["default"] == 5

    @pytest.mark.description("ExpandTool raises ExpandToolError for empty fragment_id")
    def test_empty_fragment_id_raises(self) -> None:
        tool = ExpandTool()
        with pytest.raises(ExpandToolError) as exc_info:
            tool(fragment_id="", source_id="source-1")
        assert exc_info.value.error_code == "INVALID_FRAGMENT_ID"

    @pytest.mark.description("ExpandTool raises ExpandToolError for whitespace fragment_id")
    def test_whitespace_fragment_id_raises(self) -> None:
        tool = ExpandTool()
        with pytest.raises(ExpandToolError) as exc_info:
            tool(fragment_id="   ", source_id="source-1")
        assert exc_info.value.error_code == "INVALID_FRAGMENT_ID"

    @pytest.mark.description("ExpandTool raises ExpandToolError for empty source_id")
    def test_empty_source_id_raises(self) -> None:
        tool = ExpandTool()
        with pytest.raises(ExpandToolError) as exc_info:
            tool(fragment_id="frag-1", source_id="")
        assert exc_info.value.error_code == "INVALID_SOURCE_ID"

    @pytest.mark.description("ExpandTool raises ValueError for invalid direction")
    def test_invalid_direction_raises(self) -> None:
        tool = ExpandTool()
        with pytest.raises(ValueError, match="direction must be"):
            tool(fragment_id="frag-1", source_id="source-1", direction="invalid")

    @pytest.mark.description("ExpandTool raises ValueError for tokens < 1")
    def test_tokens_too_low_raises(self) -> None:
        tool = ExpandTool()
        with pytest.raises(ValueError, match="tokens must be between 1 and 2000"):
            tool(fragment_id="frag-1", source_id="source-1", tokens=0)

    @pytest.mark.description("ExpandTool raises ValueError for tokens > 2000")
    def test_tokens_too_high_raises(self) -> None:
        tool = ExpandTool()
        with pytest.raises(ValueError, match="tokens must be between 1 and 2000"):
            tool(fragment_id="frag-1", source_id="source-1", tokens=2001)

    @pytest.mark.description("ExpandTool raises ValueError for max_fragments < 1")
    def test_max_fragments_too_low_raises(self) -> None:
        tool = ExpandTool()
        with pytest.raises(ValueError, match="max_fragments must be between 1 and 20"):
            tool(fragment_id="frag-1", source_id="source-1", max_fragments=0)

    @pytest.mark.description("ExpandTool raises ValueError for max_fragments > 20")
    def test_max_fragments_too_high_raises(self) -> None:
        tool = ExpandTool()
        with pytest.raises(ValueError, match="max_fragments must be between 1 and 20"):
            tool(fragment_id="frag-1", source_id="source-1", max_fragments=21)

    @pytest.mark.description("ExpandTool initializes with custom context expander")
    def test_custom_context_expander(self) -> None:
        mock_expander = MagicMock()
        tool = ExpandTool(context_expander=mock_expander)
        assert tool._context_expander == mock_expander

    @pytest.mark.description("ExpandTool lazily initializes context expander")
    def test_lazy_expander_init(self) -> None:
        tool = ExpandTool()
        assert tool._context_expander is None


class TestExpandToolExecution:
    """Tests for ExpandTool execution with mocked ContextExpander."""

    @pytest.fixture
    def mock_context_expander(self) -> MagicMock:
        """Create a mock ContextExpander."""
        mock_expander = MagicMock()

        # Create mock ExpandedFragment
        mock_expanded = ExpandedFragment(
            id="frag-123",
            text="This is the original fragment text",
            source_id="source-456",
            start_time=30.0,
            end_time=45.0,
            before_context=[
                ContextFragment(
                    id="before-1",
                    text="Text before the fragment",
                    start_time=15.0,
                    end_time=30.0,
                    token_count=6,
                ),
            ],
            after_context=[
                ContextFragment(
                    id="after-1",
                    text="Text after the fragment",
                    start_time=45.0,
                    end_time=60.0,
                    token_count=5,
                ),
            ],
        )

        mock_expander.expand.return_value = mock_expanded
        mock_expander.get_full_context_text.return_value = (
            "Text before the fragment This is the original fragment text "
            "Text after the fragment"
        )
        mock_expander.get_context_token_count.return_value = 20

        return mock_expander

    @pytest.mark.description("ExpandTool returns expected output structure")
    def test_output_structure(self, mock_context_expander: MagicMock) -> None:
        tool = ExpandTool(context_expander=mock_context_expander)
        result = tool(fragment_id="frag-123", source_id="source-456")

        assert "fragment_id" in result
        assert "original_text" in result
        assert "before_context" in result
        assert "after_context" in result
        assert "combined_text" in result
        assert "total_tokens" in result
        assert "at_document_start" in result
        assert "at_document_end" in result
        assert "source_id" in result

    @pytest.mark.description("ExpandTool returns correct fragment data")
    def test_fragment_data(self, mock_context_expander: MagicMock) -> None:
        tool = ExpandTool(context_expander=mock_context_expander)
        result = tool(fragment_id="frag-123", source_id="source-456")

        assert result["fragment_id"] == "frag-123"
        assert result["original_text"] == "This is the original fragment text"
        assert result["source_id"] == "source-456"
        assert result["total_tokens"] == 20

    @pytest.mark.description("ExpandTool returns before_context with correct fields")
    def test_before_context_fields(self, mock_context_expander: MagicMock) -> None:
        tool = ExpandTool(context_expander=mock_context_expander)
        result = tool(fragment_id="frag-123", source_id="source-456")

        assert len(result["before_context"]) == 1
        before = result["before_context"][0]
        assert before["id"] == "before-1"
        assert before["text"] == "Text before the fragment"
        assert before["start_time"] == 15.0
        assert before["end_time"] == 30.0
        assert before["token_count"] == 6

    @pytest.mark.description("ExpandTool returns after_context with correct fields")
    def test_after_context_fields(self, mock_context_expander: MagicMock) -> None:
        tool = ExpandTool(context_expander=mock_context_expander)
        result = tool(fragment_id="frag-123", source_id="source-456")

        assert len(result["after_context"]) == 1
        after = result["after_context"][0]
        assert after["id"] == "after-1"
        assert after["text"] == "Text after the fragment"
        assert after["start_time"] == 45.0
        assert after["end_time"] == 60.0
        assert after["token_count"] == 5

    @pytest.mark.description("ExpandTool returns combined text")
    def test_combined_text(self, mock_context_expander: MagicMock) -> None:
        tool = ExpandTool(context_expander=mock_context_expander)
        result = tool(fragment_id="frag-123", source_id="source-456")

        assert "Text before" in result["combined_text"]
        assert "original fragment" in result["combined_text"]
        assert "Text after" in result["combined_text"]

    @pytest.mark.description("ExpandTool raises ExpandToolError when fragment not found")
    def test_fragment_not_found(self, mock_context_expander: MagicMock) -> None:
        mock_context_expander.expand.return_value = None
        tool = ExpandTool(context_expander=mock_context_expander)

        with pytest.raises(ExpandToolError) as exc_info:
            tool(fragment_id="nonexistent", source_id="source-1")

        assert exc_info.value.error_code == "FRAGMENT_NOT_FOUND"
        assert "nonexistent" in exc_info.value.message

    @pytest.mark.description("ExpandTool passes direction='before' to config")
    def test_direction_before(self, mock_context_expander: MagicMock) -> None:
        tool = ExpandTool(context_expander=mock_context_expander)
        tool(fragment_id="frag-123", source_id="source-456", direction="before")

        mock_context_expander.expand.assert_called_once()
        call_kwargs = mock_context_expander.expand.call_args[1]
        config = call_kwargs["config"]
        assert config.max_tokens_before > 0
        assert config.max_tokens_after == 0
        assert config.max_fragments_before > 0
        assert config.max_fragments_after == 0

    @pytest.mark.description("ExpandTool passes direction='after' to config")
    def test_direction_after(self, mock_context_expander: MagicMock) -> None:
        tool = ExpandTool(context_expander=mock_context_expander)
        tool(fragment_id="frag-123", source_id="source-456", direction="after")

        mock_context_expander.expand.assert_called_once()
        call_kwargs = mock_context_expander.expand.call_args[1]
        config = call_kwargs["config"]
        assert config.max_tokens_before == 0
        assert config.max_tokens_after > 0
        assert config.max_fragments_before == 0
        assert config.max_fragments_after > 0

    @pytest.mark.description("ExpandTool passes direction='both' to config")
    def test_direction_both(self, mock_context_expander: MagicMock) -> None:
        tool = ExpandTool(context_expander=mock_context_expander)
        tool(fragment_id="frag-123", source_id="source-456", direction="both")

        mock_context_expander.expand.assert_called_once()
        call_kwargs = mock_context_expander.expand.call_args[1]
        config = call_kwargs["config"]
        assert config.max_tokens_before > 0
        assert config.max_tokens_after > 0
        assert config.max_fragments_before > 0
        assert config.max_fragments_after > 0

    @pytest.mark.description("ExpandTool passes tokens to config")
    def test_tokens_passed(self, mock_context_expander: MagicMock) -> None:
        tool = ExpandTool(context_expander=mock_context_expander)
        tool(fragment_id="frag-123", source_id="source-456", tokens=1000)

        mock_context_expander.expand.assert_called_once()
        call_kwargs = mock_context_expander.expand.call_args[1]
        config = call_kwargs["config"]
        assert config.max_tokens_before == 1000
        assert config.max_tokens_after == 1000

    @pytest.mark.description("ExpandTool passes max_fragments to config")
    def test_max_fragments_passed(self, mock_context_expander: MagicMock) -> None:
        tool = ExpandTool(context_expander=mock_context_expander)
        tool(fragment_id="frag-123", source_id="source-456", max_fragments=10)

        mock_context_expander.expand.assert_called_once()
        call_kwargs = mock_context_expander.expand.call_args[1]
        config = call_kwargs["config"]
        assert config.max_fragments_before == 10
        assert config.max_fragments_after == 10

    @pytest.mark.description("ExpandTool strips whitespace from fragment_id")
    def test_fragment_id_stripped(self, mock_context_expander: MagicMock) -> None:
        tool = ExpandTool(context_expander=mock_context_expander)
        tool(fragment_id="  frag-123  ", source_id="source-456")

        mock_context_expander.expand.assert_called_once()
        call_kwargs = mock_context_expander.expand.call_args[1]
        assert call_kwargs["fragment_id"] == "frag-123"

    @pytest.mark.description("ExpandTool strips whitespace from source_id")
    def test_source_id_stripped(self, mock_context_expander: MagicMock) -> None:
        tool = ExpandTool(context_expander=mock_context_expander)
        tool(fragment_id="frag-123", source_id="  source-456  ")

        mock_context_expander.expand.assert_called_once()
        call_kwargs = mock_context_expander.expand.call_args[1]
        assert call_kwargs["source_id"] == "source-456"

    @pytest.mark.description("ExpandTool accepts uppercase direction")
    def test_uppercase_direction(self, mock_context_expander: MagicMock) -> None:
        tool = ExpandTool(context_expander=mock_context_expander)
        # Should not raise
        tool(fragment_id="frag-123", source_id="source-456", direction="BEFORE")
        mock_context_expander.expand.assert_called_once()

    @pytest.mark.description("ExpandTool sets respect_boundaries to True")
    def test_respect_boundaries(self, mock_context_expander: MagicMock) -> None:
        tool = ExpandTool(context_expander=mock_context_expander)
        tool(fragment_id="frag-123", source_id="source-456")

        mock_context_expander.expand.assert_called_once()
        call_kwargs = mock_context_expander.expand.call_args[1]
        config = call_kwargs["config"]
        assert config.respect_boundaries is True


class TestExpandToolBoundaryIndicators:
    """Tests for expand tool boundary indicator logic."""

    @pytest.fixture
    def mock_expander_at_boundaries(self) -> MagicMock:
        """Create mock expander returning no context (at boundaries)."""
        mock_expander = MagicMock()
        mock_expanded = ExpandedFragment(
            id="frag-123",
            text="Fragment at document boundaries",
            source_id="source-456",
            start_time=0.0,
            end_time=10.0,
            before_context=[],  # Empty - at document start
            after_context=[],  # Empty - at document end
        )
        mock_expander.expand.return_value = mock_expanded
        mock_expander.get_full_context_text.return_value = "Fragment at document boundaries"
        mock_expander.get_context_token_count.return_value = 5
        return mock_expander

    @pytest.mark.description("ExpandTool indicates at_document_start when no before context")
    def test_at_document_start(self, mock_expander_at_boundaries: MagicMock) -> None:
        tool = ExpandTool(context_expander=mock_expander_at_boundaries)
        result = tool(fragment_id="frag-123", source_id="source-456")

        assert result["at_document_start"] is True

    @pytest.mark.description("ExpandTool indicates at_document_end when no after context")
    def test_at_document_end(self, mock_expander_at_boundaries: MagicMock) -> None:
        tool = ExpandTool(context_expander=mock_expander_at_boundaries)
        result = tool(fragment_id="frag-123", source_id="source-456")

        assert result["at_document_end"] is True

    @pytest.mark.description("ExpandTool at_document_start is False when direction=after")
    def test_not_at_start_when_after_only(
        self, mock_expander_at_boundaries: MagicMock
    ) -> None:
        tool = ExpandTool(context_expander=mock_expander_at_boundaries)
        result = tool(
            fragment_id="frag-123", source_id="source-456", direction="after"
        )

        # Should not indicate at_document_start when we didn't request before context
        assert result["at_document_start"] is False

    @pytest.mark.description("ExpandTool at_document_end is False when direction=before")
    def test_not_at_end_when_before_only(
        self, mock_expander_at_boundaries: MagicMock
    ) -> None:
        tool = ExpandTool(context_expander=mock_expander_at_boundaries)
        result = tool(
            fragment_id="frag-123", source_id="source-456", direction="before"
        )

        # Should not indicate at_document_end when we didn't request after context
        assert result["at_document_end"] is False


class TestModuleLevelExpandTool:
    """Tests for the module-level expand_tool instance."""

    @pytest.mark.description("expand_tool is an ExpandTool instance")
    def test_is_expand_tool_instance(self) -> None:
        assert isinstance(expand_tool, ExpandTool)

    @pytest.mark.description("expand_tool has expected name")
    def test_has_expected_name(self) -> None:
        assert expand_tool.name == "expand"

    @pytest.mark.description("expand_tool input_schema is accessible")
    def test_input_schema_accessible(self) -> None:
        schema = expand_tool.input_schema
        assert schema is not None
        assert "properties" in schema
        assert "fragment_id" in schema["properties"]
        assert "source_id" in schema["properties"]
        assert "direction" in schema["properties"]
        assert "tokens" in schema["properties"]
