# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for MCP resolve tool."""
from unittest.mock import MagicMock

import pytest

from voogle.mcp.tools.resolve import (
    OutputFormat,
    ParsedURI,
    ResolveOutput,
    ResolveTool,
    resolve_tool,
)

pytestmark = pytest.mark.unit


class TestOutputFormat:
    """Tests for OutputFormat enum."""

    @pytest.mark.description("OutputFormat has expected values")
    def test_output_format_values(self) -> None:
        assert OutputFormat.TEXT.value == "text"
        assert OutputFormat.MARKDOWN.value == "markdown"
        assert OutputFormat.HTML.value == "html"

    @pytest.mark.description("OutputFormat can be created from string")
    def test_output_format_from_string(self) -> None:
        assert OutputFormat("text") == OutputFormat.TEXT
        assert OutputFormat("markdown") == OutputFormat.MARKDOWN
        assert OutputFormat("html") == OutputFormat.HTML


class TestParsedURI:
    """Tests for ParsedURI dataclass."""

    @pytest.mark.description("ParsedURI has default None values")
    def test_default_values(self) -> None:
        uri = ParsedURI(scheme="semantic")
        assert uri.scheme == "semantic"
        assert uri.corpus is None
        assert uri.document is None
        assert uri.fragment is None
        assert uri.time is None

    @pytest.mark.description("ParsedURI accepts all parameters")
    def test_with_all_parameters(self) -> None:
        uri = ParsedURI(
            scheme="semantic",
            corpus="podcast-corpus",
            document="episode-123",
            fragment="frag-456",
            time=45.5,
        )
        assert uri.scheme == "semantic"
        assert uri.corpus == "podcast-corpus"
        assert uri.document == "episode-123"
        assert uri.fragment == "frag-456"
        assert uri.time == 45.5


class TestResolveOutput:
    """Tests for ResolveOutput dataclass."""

    @pytest.mark.description("ResolveOutput with required fields")
    def test_required_fields(self) -> None:
        output = ResolveOutput(
            content="Test content",
            format=OutputFormat.TEXT,
            uri="semantic://corpus/doc",
        )
        assert output.content == "Test content"
        assert output.format == OutputFormat.TEXT
        assert output.uri == "semantic://corpus/doc"
        assert output.deep_link is None
        assert output.metadata == {}

    @pytest.mark.description("ResolveOutput with all fields")
    def test_all_fields(self) -> None:
        output = ResolveOutput(
            content="Full content",
            format=OutputFormat.MARKDOWN,
            uri="semantic://corpus/doc#frag",
            deep_link="https://voogle.local/play/doc?t=45",
            metadata={"source_type": "audio"},
        )
        assert output.content == "Full content"
        assert output.format == OutputFormat.MARKDOWN
        assert output.uri == "semantic://corpus/doc#frag"
        assert output.deep_link == "https://voogle.local/play/doc?t=45"
        assert output.metadata == {"source_type": "audio"}


class TestResolveTool:
    """Tests for ResolveTool class."""

    @pytest.mark.description("ResolveTool has correct name and description")
    def test_name_and_description(self) -> None:
        tool = ResolveTool()
        assert tool.name == "resolve"
        assert "uri" in tool.description.lower()
        assert "resolve" in tool.description.lower()

    @pytest.mark.description("ResolveTool input_schema is valid JSON Schema")
    def test_input_schema_structure(self) -> None:
        tool = ResolveTool()
        schema = tool.input_schema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema
        assert "uri" in schema["required"]

    @pytest.mark.description("ResolveTool input_schema has uri property")
    def test_input_schema_uri(self) -> None:
        tool = ResolveTool()
        schema = tool.input_schema
        uri_prop = schema["properties"]["uri"]
        assert uri_prop["type"] == "string"
        assert uri_prop["minLength"] == 1

    @pytest.mark.description("ResolveTool input_schema has format property")
    def test_input_schema_format(self) -> None:
        tool = ResolveTool()
        schema = tool.input_schema
        format_prop = schema["properties"]["format"]
        assert format_prop["type"] == "string"
        assert format_prop["enum"] == ["text", "markdown", "html"]
        assert format_prop["default"] == "text"

    @pytest.mark.description("ResolveTool initializes with custom qdrant client")
    def test_custom_qdrant_client(self) -> None:
        mock_client = MagicMock()
        tool = ResolveTool(qdrant_client=mock_client)
        assert tool._qdrant_client == mock_client

    @pytest.mark.description("ResolveTool lazily initializes qdrant client")
    def test_lazy_client_init(self) -> None:
        tool = ResolveTool()
        assert tool._qdrant_client is None


class TestResolveToolURIParsing:
    """Tests for ResolveTool URI parsing."""

    @pytest.fixture
    def tool(self) -> ResolveTool:
        """Create a ResolveTool instance."""
        return ResolveTool()

    @pytest.mark.description("parse_uri parses semantic:// URI with corpus and doc")
    def test_parse_semantic_uri_full(self, tool: ResolveTool) -> None:
        parsed = tool.parse_uri("semantic://podcast-corpus/episode-123")
        assert parsed.scheme == "semantic"
        assert parsed.corpus == "podcast-corpus"
        assert parsed.document == "episode-123"
        assert parsed.fragment is None
        assert parsed.time is None

    @pytest.mark.description("parse_uri parses semantic:// URI with fragment")
    def test_parse_semantic_uri_with_fragment(self, tool: ResolveTool) -> None:
        parsed = tool.parse_uri("semantic://corpus/doc#frag-456")
        assert parsed.scheme == "semantic"
        assert parsed.corpus == "corpus"
        assert parsed.document == "doc"
        assert parsed.fragment == "frag-456"

    @pytest.mark.description("parse_uri parses voogle:// URI with source")
    def test_parse_voogle_uri(self, tool: ResolveTool) -> None:
        parsed = tool.parse_uri("voogle://episode-123")
        assert parsed.scheme == "voogle"
        assert parsed.corpus is None
        assert parsed.document == "episode-123"
        assert parsed.fragment is None

    @pytest.mark.description("parse_uri parses voogle:// URI with time")
    def test_parse_voogle_uri_with_time(self, tool: ResolveTool) -> None:
        parsed = tool.parse_uri("voogle://episode-123?t=45")
        assert parsed.scheme == "voogle"
        assert parsed.document == "episode-123"
        assert parsed.time == 45.0

    @pytest.mark.description("parse_uri parses voogle:// URI with float time")
    def test_parse_voogle_uri_with_float_time(self, tool: ResolveTool) -> None:
        parsed = tool.parse_uri("voogle://episode-123?t=45.5")
        assert parsed.scheme == "voogle"
        assert parsed.document == "episode-123"
        assert parsed.time == 45.5

    @pytest.mark.description("parse_uri raises ValueError for empty URI")
    def test_parse_empty_uri_raises(self, tool: ResolveTool) -> None:
        with pytest.raises(ValueError, match="uri cannot be empty"):
            tool.parse_uri("")

    @pytest.mark.description("parse_uri raises ValueError for whitespace URI")
    def test_parse_whitespace_uri_raises(self, tool: ResolveTool) -> None:
        with pytest.raises(ValueError, match="uri cannot be empty"):
            tool.parse_uri("   ")

    @pytest.mark.description("parse_uri raises ValueError for unsupported scheme")
    def test_parse_unsupported_scheme_raises(self, tool: ResolveTool) -> None:
        with pytest.raises(ValueError, match="Unsupported URI scheme"):
            tool.parse_uri("https://example.com/doc")

    @pytest.mark.description("parse_uri handles invalid time gracefully")
    def test_parse_invalid_time(self, tool: ResolveTool) -> None:
        parsed = tool.parse_uri("voogle://episode-123?t=invalid")
        assert parsed.scheme == "voogle"
        assert parsed.document == "episode-123"
        assert parsed.time is None


class TestResolveToolFormatContent:
    """Tests for ResolveTool content formatting."""

    @pytest.fixture
    def tool(self) -> ResolveTool:
        """Create a ResolveTool instance."""
        return ResolveTool()

    @pytest.mark.description("_format_content returns plain text for TEXT format")
    def test_format_text(self, tool: ResolveTool) -> None:
        text = "Hello world"
        metadata = {"source_id": "ep-123", "source_type": "audio"}
        result = tool._format_content(text, OutputFormat.TEXT, metadata)
        assert result == "Hello world"

    @pytest.mark.description("_format_content returns markdown for MARKDOWN format")
    def test_format_markdown(self, tool: ResolveTool) -> None:
        text = "Hello world"
        metadata = {
            "source_id": "ep-123",
            "source_type": "audio",
            "start_time": 45.0,
        }
        result = tool._format_content(text, OutputFormat.MARKDOWN, metadata)
        assert "**Source:** ep-123" in result
        assert "**Type:** audio" in result
        assert "**Time:** 45.0s" in result
        assert "Hello world" in result

    @pytest.mark.description("_format_content returns html for HTML format")
    def test_format_html(self, tool: ResolveTool) -> None:
        text = "Hello world"
        metadata = {
            "source_id": "ep-123",
            "source_type": "audio",
            "start_time": 45.0,
        }
        result = tool._format_content(text, OutputFormat.HTML, metadata)
        assert '<div class="voogle-content">' in result
        assert '<span class="source">ep-123</span>' in result
        assert '<span class="type">audio</span>' in result
        assert '<span class="time">45.0s</span>' in result
        assert '<p class="content">Hello world</p>' in result


class TestResolveToolDeepLink:
    """Tests for ResolveTool deep link generation."""

    @pytest.fixture
    def tool(self) -> ResolveTool:
        """Create a ResolveTool instance."""
        return ResolveTool()

    @pytest.mark.description("_generate_deep_link creates URL without time")
    def test_deep_link_without_time(self, tool: ResolveTool) -> None:
        result = tool._generate_deep_link("episode-123")
        assert result.endswith("/play/episode-123")

    @pytest.mark.description("_generate_deep_link creates URL with time")
    def test_deep_link_with_time(self, tool: ResolveTool) -> None:
        result = tool._generate_deep_link("episode-123", start_time=45.5)
        assert "/play/episode-123?t=45" in result


class TestResolveToolExecution:
    """Tests for ResolveTool execution with mocked Qdrant client."""

    @pytest.fixture
    def mock_qdrant_client(self) -> MagicMock:
        """Create a mock Qdrant client."""
        mock_client = MagicMock()
        # Mock retrieve for fragment lookup
        mock_point = MagicMock()
        mock_point.payload = {
            "text": "This is test content",
            "source_id": "episode-123",
            "source_type": "audio",
            "start_time": 45.0,
            "end_time": 60.0,
            "corpus_id": "podcast-corpus",
        }
        mock_client.retrieve.return_value = [mock_point]
        return mock_client

    @pytest.mark.description("ResolveTool returns expected output structure")
    def test_output_structure(self, mock_qdrant_client: MagicMock) -> None:
        tool = ResolveTool(qdrant_client=mock_qdrant_client)
        result = tool(uri="semantic://corpus/doc#frag-123")

        assert "content" in result
        assert "format" in result
        assert "uri" in result
        assert "deep_link" in result
        assert "metadata" in result

    @pytest.mark.description("ResolveTool returns text format by default")
    def test_default_text_format(self, mock_qdrant_client: MagicMock) -> None:
        tool = ResolveTool(qdrant_client=mock_qdrant_client)
        result = tool(uri="semantic://corpus/doc#frag-123")

        assert result["format"] == "text"
        assert result["content"] == "This is test content"

    @pytest.mark.description("ResolveTool returns markdown format when requested")
    def test_markdown_format(self, mock_qdrant_client: MagicMock) -> None:
        tool = ResolveTool(qdrant_client=mock_qdrant_client)
        result = tool(uri="semantic://corpus/doc#frag-123", format="markdown")

        assert result["format"] == "markdown"
        assert "**Source:**" in result["content"]

    @pytest.mark.description("ResolveTool returns html format when requested")
    def test_html_format(self, mock_qdrant_client: MagicMock) -> None:
        tool = ResolveTool(qdrant_client=mock_qdrant_client)
        result = tool(uri="semantic://corpus/doc#frag-123", format="html")

        assert result["format"] == "html"
        assert '<div class="voogle-content">' in result["content"]

    @pytest.mark.description("ResolveTool includes metadata in output")
    def test_includes_metadata(self, mock_qdrant_client: MagicMock) -> None:
        tool = ResolveTool(qdrant_client=mock_qdrant_client)
        result = tool(uri="semantic://corpus/doc#frag-123")

        assert result["metadata"]["source_id"] == "episode-123"
        assert result["metadata"]["source_type"] == "audio"
        assert result["metadata"]["start_time"] == 45.0
        assert result["metadata"]["end_time"] == 60.0
        assert result["metadata"]["corpus_id"] == "podcast-corpus"

    @pytest.mark.description("ResolveTool generates deep link")
    def test_generates_deep_link(self, mock_qdrant_client: MagicMock) -> None:
        tool = ResolveTool(qdrant_client=mock_qdrant_client)
        result = tool(uri="semantic://corpus/doc#frag-123")

        assert "deep_link" in result
        assert "/play/episode-123?t=45" in result["deep_link"]

    @pytest.mark.description("ResolveTool preserves original URI")
    def test_preserves_original_uri(self, mock_qdrant_client: MagicMock) -> None:
        original_uri = "semantic://corpus/doc#frag-123"
        tool = ResolveTool(qdrant_client=mock_qdrant_client)
        result = tool(uri=original_uri)

        assert result["uri"] == original_uri

    @pytest.mark.description("ResolveTool raises ValueError for invalid format")
    def test_invalid_format_raises(self, mock_qdrant_client: MagicMock) -> None:
        tool = ResolveTool(qdrant_client=mock_qdrant_client)
        with pytest.raises(ValueError, match="Unsupported format"):
            tool(uri="semantic://corpus/doc#frag-123", format="invalid")

    @pytest.mark.description("ResolveTool raises ValueError when URI cannot be resolved")
    def test_unresolvable_uri_raises(self) -> None:
        mock_client = MagicMock()
        mock_client.retrieve.return_value = []
        mock_client.scroll.return_value = ([], None)

        tool = ResolveTool(qdrant_client=mock_client)
        with pytest.raises(ValueError, match="Unable to resolve URI"):
            tool(uri="semantic://corpus/doc#nonexistent")


class TestResolveToolFetchBySource:
    """Tests for ResolveTool fetch by source ID."""

    @pytest.fixture
    def mock_qdrant_with_scroll(self) -> MagicMock:
        """Create a mock Qdrant client for scroll-based lookup."""
        mock_client = MagicMock()
        mock_client.retrieve.return_value = []  # Fragment lookup fails

        mock_point = MagicMock()
        mock_point.payload = {
            "text": "Content from source",
            "source_id": "episode-456",
            "source_type": "video",
            "start_time": 30.0,
            "end_time": 45.0,
        }
        mock_client.scroll.return_value = ([mock_point], None)
        return mock_client

    @pytest.mark.description("ResolveTool falls back to source lookup when fragment not found")
    def test_fallback_to_source_lookup(
        self, mock_qdrant_with_scroll: MagicMock
    ) -> None:
        tool = ResolveTool(qdrant_client=mock_qdrant_with_scroll)
        result = tool(uri="voogle://episode-456?t=35")

        assert result["content"] == "Content from source"
        assert result["metadata"]["source_id"] == "episode-456"


class TestModuleLevelResolveTool:
    """Tests for the module-level resolve_tool instance."""

    @pytest.mark.description("resolve_tool is a ResolveTool instance")
    def test_is_resolve_tool_instance(self) -> None:
        assert isinstance(resolve_tool, ResolveTool)

    @pytest.mark.description("resolve_tool has expected name")
    def test_has_expected_name(self) -> None:
        assert resolve_tool.name == "resolve"

    @pytest.mark.description("resolve_tool input_schema is accessible")
    def test_input_schema_accessible(self) -> None:
        schema = resolve_tool.input_schema
        assert schema is not None
        assert "properties" in schema
        assert "uri" in schema["properties"]
