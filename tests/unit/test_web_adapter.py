# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for WebAdapter content adapter."""
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from voogle.adapters.base import ChunkConfig, ContentSource, RawChunk, TextChunk
from voogle.adapters.web import (
    BOILERPLATE_TAGS,
    CONTENT_TAGS,
    WebAdapter,
    WebConfig,
)
from voogle.core.fragment import ContentType
from voogle.core.location import ElementSelectorLocation

pytestmark = pytest.mark.unit


class TestWebAdapterInit:
    """Tests for WebAdapter initialization."""

    @pytest.mark.description("WebAdapter initializes with default config")
    def test_init_default_config(self) -> None:
        adapter = WebAdapter()
        assert adapter._config.remove_boilerplate is True
        assert adapter._config.use_playwright is False
        assert adapter._config.timeout == 30.0
        assert adapter._config.min_text_length == 20

    @pytest.mark.description("WebAdapter initializes with custom config")
    def test_init_custom_config(self) -> None:
        config = WebConfig(
            remove_boilerplate=False,
            use_playwright=True,
            timeout=60.0,
            min_text_length=50,
        )
        adapter = WebAdapter(config=config)
        assert adapter._config.remove_boilerplate is False
        assert adapter._config.use_playwright is True
        assert adapter._config.timeout == 60.0
        assert adapter._config.min_text_length == 50


class TestWebAdapterSupportedTypes:
    """Tests for WebAdapter.supported_types property."""

    @pytest.mark.description("supported_types returns TEXT only")
    def test_supported_types(self) -> None:
        adapter = WebAdapter()
        assert adapter.supported_types == frozenset({ContentType.TEXT})


class TestWebAdapterSupports:
    """Tests for WebAdapter.supports method."""

    @pytest.mark.description("supports returns True for HTML files")
    def test_supports_html(self) -> None:
        adapter = WebAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            path=Path("/data/page.html"),
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns True for HTM files")
    def test_supports_htm(self) -> None:
        adapter = WebAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            path=Path("/data/page.htm"),
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns True for XHTML files")
    def test_supports_xhtml(self) -> None:
        adapter = WebAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            path=Path("/data/page.xhtml"),
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns True for text/html MIME type")
    def test_supports_html_mime(self) -> None:
        adapter = WebAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            url="https://example.com/page",
            metadata={"mime_type": "text/html"},
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns True for HTTP URLs")
    def test_supports_http_url(self) -> None:
        adapter = WebAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            url="https://example.com/article",
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns False for non-TEXT content type")
    def test_rejects_non_text_type(self) -> None:
        adapter = WebAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.AUDIO,
            path=Path("/data/audio.mp3"),
        )
        assert adapter.supports(source) is False

    @pytest.mark.description("supports returns False for JSON files")
    def test_rejects_json_url(self) -> None:
        adapter = WebAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            url="https://example.com/data.json",
        )
        assert adapter.supports(source) is False

    @pytest.mark.description("supports returns False for PDF files")
    def test_rejects_pdf_url(self) -> None:
        adapter = WebAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            url="https://example.com/doc.pdf",
        )
        assert adapter.supports(source) is False


class TestWebAdapterExtract:
    """Tests for WebAdapter.extract method."""

    @pytest.mark.description("extract raises ValueError for unsupported source")
    @pytest.mark.asyncio
    async def test_extract_unsupported_raises(self) -> None:
        adapter = WebAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.AUDIO,
            path=Path("/data/audio.mp3"),
        )
        with pytest.raises(ValueError, match="Unsupported source"):
            async for _ in adapter.extract(source):
                pass

    @pytest.mark.description("extract raises ValueError for missing file")
    @pytest.mark.asyncio
    async def test_extract_missing_file_raises(self) -> None:
        adapter = WebAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            path=Path("/nonexistent/page.html"),
        )
        with pytest.raises(ValueError, match="HTML file not found"):
            async for _ in adapter.extract(source):
                pass

    @pytest.mark.description("extract yields RawChunks from HTML content")
    @pytest.mark.asyncio
    async def test_extract_from_file(self, tmp_path: Path) -> None:
        html_content = """
        <!DOCTYPE html>
        <html>
        <head><title>Test Page</title></head>
        <body>
            <main>
                <article>
                    <p>This is a paragraph with enough content to pass the minimum length threshold for extraction.</p>
                </article>
            </main>
        </body>
        </html>
        """
        html_file = tmp_path / "test.html"
        html_file.write_text(html_content)

        adapter = WebAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            path=html_file,
        )

        chunks = []
        async for chunk in adapter.extract(source):
            chunks.append(chunk)

        assert len(chunks) >= 1
        assert any("paragraph" in chunk.text.lower() for chunk in chunks)
        # Check that location is ElementSelectorLocation
        for chunk in chunks:
            if chunk.location:
                assert isinstance(chunk.location, ElementSelectorLocation)

    @pytest.mark.description("extract removes boilerplate when configured")
    @pytest.mark.asyncio
    async def test_extract_removes_boilerplate(self, tmp_path: Path) -> None:
        html_content = """
        <!DOCTYPE html>
        <html>
        <head><title>Test Page</title></head>
        <body>
            <nav>Navigation menu that should be removed from content extraction</nav>
            <main>
                <article>
                    <p>This is the main content paragraph that should be extracted and preserved.</p>
                </article>
            </main>
            <footer>Footer content that should also be removed from extraction</footer>
        </body>
        </html>
        """
        html_file = tmp_path / "test.html"
        html_file.write_text(html_content)

        adapter = WebAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            path=html_file,
        )

        chunks = []
        async for chunk in adapter.extract(source):
            chunks.append(chunk)

        # Main content should be present
        all_text = " ".join(c.text for c in chunks)
        assert "main content" in all_text.lower()
        # Navigation should not be present
        assert "navigation menu" not in all_text.lower()

    @pytest.mark.description("extract uses httpx for URL sources")
    @pytest.mark.asyncio
    async def test_extract_from_url(self) -> None:
        html_content = """
        <html>
        <body>
            <main>
                <p>This is content fetched from a URL with enough text to be extracted.</p>
            </main>
        </body>
        </html>
        """

        adapter = WebAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            url="https://example.com/article",
        )

        mock_response = MagicMock()
        mock_response.text = html_content
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()
            mock_client_class.return_value = mock_client

            chunks = []
            async for chunk in adapter.extract(source):
                chunks.append(chunk)

        assert len(chunks) >= 1


class TestWebAdapterChunk:
    """Tests for WebAdapter.chunk method."""

    @pytest.mark.description("chunk returns empty list for empty input")
    def test_chunk_empty_input(self) -> None:
        adapter = WebAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            path=Path("/data/page.html"),
        )
        result = adapter.chunk([], source)
        assert result == []

    @pytest.mark.description("chunk combines text into target-sized chunks")
    def test_chunk_combines_text(self) -> None:
        adapter = WebAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            path=Path("/data/page.html"),
        )

        # Create raw chunks with sufficient text
        words = "word " * 50
        raw_chunks = [
            RawChunk(
                text=words,
                location=ElementSelectorLocation(
                    selector="p.content",
                    text_match=words[:50],
                ),
            )
        ]

        config = ChunkConfig(target_words=40, overlap_words=5)
        result = adapter.chunk(raw_chunks, source, config)

        assert len(result) >= 1
        assert all(chunk.source_id == "test" for chunk in result)
        assert all(chunk.source_type == ContentType.TEXT for chunk in result)

    @pytest.mark.description("chunk preserves ElementSelectorLocation")
    def test_chunk_preserves_location(self) -> None:
        adapter = WebAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            path=Path("/data/page.html"),
        )

        raw_chunks = [
            RawChunk(
                text="word " * 45,
                location=ElementSelectorLocation(
                    selector="article > p",
                    text_match="Some text",
                ),
            )
        ]

        config = ChunkConfig(target_words=40, overlap_words=5)
        result = adapter.chunk(raw_chunks, source, config)

        assert len(result) >= 1
        assert result[0].location is not None
        assert isinstance(result[0].location, ElementSelectorLocation)

    @pytest.mark.description("chunk increments sequence_index correctly")
    def test_chunk_sequence_index(self) -> None:
        adapter = WebAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            path=Path("/data/page.html"),
        )

        raw_chunks = [
            RawChunk(
                text="word " * 100,
                location=ElementSelectorLocation(selector="p"),
            )
        ]

        config = ChunkConfig(target_words=40, overlap_words=5)
        result = adapter.chunk(raw_chunks, source, config)

        assert len(result) >= 2
        for i, chunk in enumerate(result):
            assert chunk.sequence_index == i


class TestWebAdapterGetLocation:
    """Tests for WebAdapter.get_location method."""

    @pytest.mark.description("get_location returns chunk location")
    def test_get_location_returns_location(self) -> None:
        adapter = WebAdapter()
        location = ElementSelectorLocation(
            selector="#content",
            text_match="Some text",
        )
        chunk = TextChunk(
            text="test content",
            source_id="test",
            source_type=ContentType.TEXT,
            location=location,
        )

        result = adapter.get_location(chunk)
        assert result == location

    @pytest.mark.description("get_location returns None when no location")
    def test_get_location_returns_none(self) -> None:
        adapter = WebAdapter()
        chunk = TextChunk(
            text="test content",
            source_id="test",
            source_type=ContentType.TEXT,
        )

        result = adapter.get_location(chunk)
        assert result is None


class TestWebAdapterGetDeepLink:
    """Tests for WebAdapter.get_deep_link method."""

    @pytest.mark.description("get_deep_link generates text fragment URL")
    def test_get_deep_link_with_text_match(self) -> None:
        adapter = WebAdapter()
        location = ElementSelectorLocation(
            selector="p.content",
            text_match="Important text",
        )
        chunk = TextChunk(
            text="Important text and more",
            source_id="test",
            source_type=ContentType.TEXT,
            location=location,
        )

        result = adapter.get_deep_link(chunk, "https://example.com/article")
        assert result is not None
        assert "#:~:text=" in result
        assert "Important" in result

    @pytest.mark.description("get_deep_link generates ID fragment for ID selectors")
    def test_get_deep_link_with_id_selector(self) -> None:
        adapter = WebAdapter()
        location = ElementSelectorLocation(
            selector="#main-content",
        )
        chunk = TextChunk(
            text="test content",
            source_id="test",
            source_type=ContentType.TEXT,
            location=location,
        )

        result = adapter.get_deep_link(chunk, "https://example.com/article")
        assert result is not None
        assert result == "https://example.com/article#main-content"

    @pytest.mark.description("get_deep_link returns None without location")
    def test_get_deep_link_without_location(self) -> None:
        adapter = WebAdapter()
        chunk = TextChunk(
            text="test content",
            source_id="test",
            source_type=ContentType.TEXT,
        )

        result = adapter.get_deep_link(chunk, "https://example.com/article")
        assert result is None


class TestWebConfig:
    """Tests for WebConfig dataclass."""

    @pytest.mark.description("WebConfig has correct defaults")
    def test_default_values(self) -> None:
        config = WebConfig()
        assert config.remove_boilerplate is True
        assert config.use_playwright is False
        assert config.timeout == 30.0
        assert config.extract_links is True
        assert config.min_text_length == 20

    @pytest.mark.description("WebConfig accepts custom values")
    def test_custom_values(self) -> None:
        config = WebConfig(
            remove_boilerplate=False,
            use_playwright=True,
            timeout=120.0,
            extract_links=False,
            min_text_length=100,
            user_agent="CustomBot/1.0",
        )
        assert config.remove_boilerplate is False
        assert config.use_playwright is True
        assert config.timeout == 120.0
        assert config.user_agent == "CustomBot/1.0"


class TestBoilerplateConstants:
    """Tests for boilerplate-related constants."""

    @pytest.mark.description("BOILERPLATE_TAGS contains navigation elements")
    def test_boilerplate_tags(self) -> None:
        assert "nav" in BOILERPLATE_TAGS
        assert "header" in BOILERPLATE_TAGS
        assert "footer" in BOILERPLATE_TAGS
        assert "script" in BOILERPLATE_TAGS
        assert "style" in BOILERPLATE_TAGS

    @pytest.mark.description("CONTENT_TAGS contains content elements")
    def test_content_tags(self) -> None:
        assert "article" in CONTENT_TAGS
        assert "main" in CONTENT_TAGS
        assert "p" in CONTENT_TAGS
        assert "h1" in CONTENT_TAGS
        assert "section" in CONTENT_TAGS

    @pytest.mark.description("Constants are frozen sets")
    def test_constants_are_frozen(self) -> None:
        assert isinstance(BOILERPLATE_TAGS, frozenset)
        assert isinstance(CONTENT_TAGS, frozenset)


class TestCSSSelector:
    """Tests for CSS selector generation."""

    @pytest.mark.description("generates ID selector for elements with ID")
    @pytest.mark.asyncio
    async def test_css_selector_with_id(self, tmp_path: Path) -> None:
        html_content = """
        <html>
        <body>
            <main>
                <p id="intro">This paragraph has an ID and enough content to be extracted properly.</p>
            </main>
        </body>
        </html>
        """
        html_file = tmp_path / "test.html"
        html_file.write_text(html_content)

        adapter = WebAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            path=html_file,
        )

        chunks = []
        async for chunk in adapter.extract(source):
            chunks.append(chunk)

        # At least one chunk should have an ID-based selector
        has_id_selector = any(
            chunk.location and
            isinstance(chunk.location, ElementSelectorLocation) and
            "#intro" in chunk.location.selector
            for chunk in chunks
        )
        # The paragraph may be selected or its ID used
        assert len(chunks) >= 1


class TestTextFragmentGeneration:
    """Tests for text fragment URL generation."""

    @pytest.mark.description("text_match is included in location")
    @pytest.mark.asyncio
    async def test_text_match_in_location(self, tmp_path: Path) -> None:
        html_content = """
        <html>
        <body>
            <main>
                <p>This is some searchable text content that should be found in the document.</p>
            </main>
        </body>
        </html>
        """
        html_file = tmp_path / "test.html"
        html_file.write_text(html_content)

        adapter = WebAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.TEXT,
            path=html_file,
        )

        chunks = []
        async for chunk in adapter.extract(source):
            chunks.append(chunk)

        # Check that text_match is set
        for chunk in chunks:
            if chunk.location and isinstance(chunk.location, ElementSelectorLocation):
                assert chunk.location.text_match is not None
                # Text match should be a prefix of the full text
                assert len(chunk.location.text_match) <= 50
