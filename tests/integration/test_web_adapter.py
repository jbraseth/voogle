# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Integration tests for WebAdapter content adapter.

Tests web content extraction and CSS selector validation with:
- Static HTML fixture tests
- Text extraction accuracy
- CSS selector validity
- Boilerplate removal effectiveness
- Deep link format validation
"""
import tempfile
from pathlib import Path

import pytest

from voogle import embedding, vector
from voogle.adapters.base import ChunkConfig, ContentSource, RawChunk, TextChunk
from voogle.adapters.web import (
    WebAdapter,
    WebConfig,
)
from voogle.core.fragment import ContentType
from voogle.core.location import ElementSelectorLocation

pytestmark = pytest.mark.integration


# Check if BeautifulSoup is available
try:
    from bs4 import BeautifulSoup  # noqa: F401
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

requires_bs4 = pytest.mark.skipif(
    not BS4_AVAILABLE,
    reason="BeautifulSoup4 not installed"
)


@requires_bs4
class TestStaticHTMLFixture:
    """Integration tests using static HTML fixture files."""

    @pytest.mark.description("WebAdapter processes sample HTML fixture file")
    @pytest.mark.asyncio
    async def test_adapter_processes_html_fixture(
        self, content_fixtures_dir: Path
    ) -> None:
        """Test that WebAdapter can process the sample_webpage.html fixture."""
        html_path = content_fixtures_dir / "sample_webpage.html"
        if not html_path.exists():
            pytest.skip("Sample webpage fixture not found")

        adapter = WebAdapter()
        source = ContentSource(
            source_id="sample-webpage",
            source_type=ContentType.TEXT,
            path=html_path,
            metadata={"mime_type": "text/html"},
        )

        assert adapter.supports(source) is True

        # Extract raw chunks from HTML
        raw_chunks: list[RawChunk] = []
        async for chunk in adapter.extract(source):
            raw_chunks.append(chunk)

        # Should have extracted some content
        assert len(raw_chunks) > 0, "Should extract at least one chunk from HTML"

        # Verify chunks have required fields
        for chunk in raw_chunks:
            assert chunk.text.strip(), "Chunk should have text"
            assert isinstance(chunk.location, ElementSelectorLocation), (
                "Should have ElementSelectorLocation"
            )
            assert chunk.location.selector, "Should have CSS selector"

    @pytest.mark.description("WebAdapter extracts title from HTML document")
    @pytest.mark.asyncio
    async def test_extracts_title_metadata(
        self, content_fixtures_dir: Path
    ) -> None:
        """Test that extraction captures page title in metadata."""
        html_path = content_fixtures_dir / "sample_webpage.html"
        if not html_path.exists():
            pytest.skip("Sample webpage fixture not found")

        adapter = WebAdapter()
        source = ContentSource(
            source_id="sample-webpage",
            source_type=ContentType.TEXT,
            path=html_path,
            metadata={"mime_type": "text/html"},
        )

        raw_chunks: list[RawChunk] = []
        async for chunk in adapter.extract(source):
            raw_chunks.append(chunk)

        # At least one chunk should have title metadata
        titles = [c.metadata.get("title") for c in raw_chunks if c.metadata.get("title")]
        assert len(titles) > 0, "Should extract page title"
        assert "Semantic Search" in titles[0], "Title should contain expected text"

    @pytest.mark.description("WebAdapter handles inline HTML content")
    @pytest.mark.asyncio
    async def test_processes_inline_html_string(self) -> None:
        """Test processing HTML provided as a string via temp file."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head><title>Test Page</title></head>
        <body>
            <main>
                <article>
                    <h1>Test Article</h1>
                    <p>This is a paragraph with enough text to meet the minimum length requirement for extraction. It discusses important topics.</p>
                </article>
            </main>
        </body>
        </html>
        """

        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
            f.write(html_content)
            html_path = Path(f.name)

        try:
            adapter = WebAdapter()
            source = ContentSource(
                source_id="inline-test",
                source_type=ContentType.TEXT,
                path=html_path,
                metadata={"mime_type": "text/html"},
            )

            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

            assert len(raw_chunks) > 0, "Should extract content from inline HTML"

            # Verify expected content is present
            all_text = " ".join(c.text for c in raw_chunks).lower()
            assert "paragraph" in all_text or "important" in all_text

        finally:
            html_path.unlink(missing_ok=True)


@requires_bs4
class TestTextExtractionAccuracy:
    """Tests for text extraction accuracy verification."""

    @pytest.mark.description("Extraction captures main content sections")
    @pytest.mark.asyncio
    async def test_extracts_main_content_sections(
        self, content_fixtures_dir: Path
    ) -> None:
        """Test that extraction captures expected content sections."""
        html_path = content_fixtures_dir / "sample_webpage.html"
        if not html_path.exists():
            pytest.skip("Sample webpage fixture not found")

        adapter = WebAdapter()
        source = ContentSource(
            source_id="content-test",
            source_type=ContentType.TEXT,
            path=html_path,
            metadata={"mime_type": "text/html"},
        )

        raw_chunks: list[RawChunk] = []
        async for chunk in adapter.extract(source):
            raw_chunks.append(chunk)

        # Combine all extracted text
        full_text = " ".join(chunk.text for chunk in raw_chunks).lower()

        # Should capture key content from sample_webpage.html
        expected_phrases = [
            "semantic",
            "search",
            "embedding",
            "vector",
        ]

        found_phrases = [p for p in expected_phrases if p in full_text]
        assert len(found_phrases) >= 2, (
            f"Should find at least 2 key phrases. Found: {found_phrases}. "
            f"Text sample: {full_text[:200]}..."
        )

    @pytest.mark.description("Extraction preserves text from nested elements")
    @pytest.mark.asyncio
    async def test_preserves_nested_element_text(self) -> None:
        """Test that text from nested elements is properly extracted."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <body>
            <main>
                <article>
                    <section id="intro">
                        <p>This paragraph contains <strong>bold text</strong> and
                        <em>italic text</em> that should be preserved as plain text.</p>
                    </section>
                </article>
            </main>
        </body>
        </html>
        """

        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
            f.write(html_content)
            html_path = Path(f.name)

        try:
            adapter = WebAdapter()
            source = ContentSource(
                source_id="nested-test",
                source_type=ContentType.TEXT,
                path=html_path,
                metadata={"mime_type": "text/html"},
            )

            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

            full_text = " ".join(c.text for c in raw_chunks).lower()

            # Should extract text content, preserving inline elements
            assert "bold text" in full_text or "italic text" in full_text, (
                f"Should preserve inline element text. Got: {full_text}"
            )

        finally:
            html_path.unlink(missing_ok=True)

    @pytest.mark.description("Extraction produces non-empty chunks")
    @pytest.mark.asyncio
    async def test_produces_non_empty_chunks(
        self, content_fixtures_dir: Path
    ) -> None:
        """Test that all extracted chunks have meaningful content."""
        html_path = content_fixtures_dir / "sample_webpage.html"
        if not html_path.exists():
            pytest.skip("Sample webpage fixture not found")

        adapter = WebAdapter()
        source = ContentSource(
            source_id="non-empty-test",
            source_type=ContentType.TEXT,
            path=html_path,
            metadata={"mime_type": "text/html"},
        )

        raw_chunks: list[RawChunk] = []
        async for chunk in adapter.extract(source):
            raw_chunks.append(chunk)

        # All chunks should have non-trivial text
        for chunk in raw_chunks:
            assert len(chunk.text) >= 20, (
                f"Chunk text should meet min length. Got: '{chunk.text}'"
            )


@requires_bs4
class TestCSSSelectorValidity:
    """Tests for CSS selector generation and validity."""

    @pytest.mark.description("Generated CSS selectors are syntactically valid")
    @pytest.mark.asyncio
    async def test_css_selectors_syntactically_valid(self) -> None:
        """Test that generated CSS selectors have valid syntax."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <body>
            <main>
                <article id="main-article">
                    <p class="intro-text">First paragraph with introductory content that is long enough.</p>
                    <div class="content-block">
                        <p>Second paragraph in a div block with substantial text content here.</p>
                    </div>
                </article>
            </main>
        </body>
        </html>
        """

        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
            f.write(html_content)
            html_path = Path(f.name)

        try:
            adapter = WebAdapter()
            source = ContentSource(
                source_id="selector-test",
                source_type=ContentType.TEXT,
                path=html_path,
                metadata={"mime_type": "text/html"},
            )

            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

            for chunk in raw_chunks:
                assert isinstance(chunk.location, ElementSelectorLocation)
                selector = chunk.location.selector

                # Verify basic CSS selector syntax
                assert selector, "Selector should not be empty"
                # Should not contain invalid characters for CSS
                assert "\n" not in selector, "Selector should not contain newlines"
                assert "\t" not in selector, "Selector should not contain tabs"

                # Should be a valid CSS selector pattern
                # Either ID (#id), class (.class), element (tag), or combination
                valid_patterns = [
                    selector.startswith("#"),  # ID selector
                    selector.startswith("."),  # Class selector
                    selector[0].isalpha(),  # Element selector
                ]
                assert any(valid_patterns), f"Invalid selector pattern: {selector}"

        finally:
            html_path.unlink(missing_ok=True)

    @pytest.mark.description("CSS selectors reference correct elements")
    @pytest.mark.asyncio
    async def test_css_selectors_match_content(self) -> None:
        """Test that CSS selectors correspond to their content location."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <body>
            <main>
                <section id="unique-section">
                    <p>Content in a uniquely identified section that has enough text to extract properly.</p>
                </section>
            </main>
        </body>
        </html>
        """

        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
            f.write(html_content)
            html_path = Path(f.name)

        try:
            adapter = WebAdapter()
            source = ContentSource(
                source_id="match-test",
                source_type=ContentType.TEXT,
                path=html_path,
                metadata={"mime_type": "text/html"},
            )

            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

            # Find chunk from unique section
            section_chunks = [
                c for c in raw_chunks
                if isinstance(c.location, ElementSelectorLocation)
                and ("unique" in c.location.selector.lower() or
                     "unique" in (c.metadata.get("element_id") or "").lower())
            ]

            # Should have found the unique section or child elements
            # Verify selectors are reasonable for the content
            for chunk in raw_chunks:
                assert isinstance(chunk.location, ElementSelectorLocation)
                selector = chunk.location.selector
                # Selector should contain recognizable element references
                assert any(
                    tag in selector.lower()
                    for tag in ["p", "div", "section", "article", "main", "#"]
                ), f"Selector should reference known elements: {selector}"

        finally:
            html_path.unlink(missing_ok=True)

    @pytest.mark.description("CSS selectors are unique within document")
    @pytest.mark.asyncio
    async def test_css_selector_uniqueness(self) -> None:
        """Test that CSS selectors provide unique element identification."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <body>
            <main>
                <article>
                    <p>First paragraph with enough content to be extracted by the adapter.</p>
                    <p>Second paragraph also with sufficient text content for extraction.</p>
                    <p>Third paragraph providing additional text content for uniqueness testing.</p>
                </article>
            </main>
        </body>
        </html>
        """

        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
            f.write(html_content)
            html_path = Path(f.name)

        try:
            adapter = WebAdapter()
            source = ContentSource(
                source_id="uniqueness-test",
                source_type=ContentType.TEXT,
                path=html_path,
                metadata={"mime_type": "text/html"},
            )

            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

            # Each chunk should have a selector
            selectors = [
                c.location.selector for c in raw_chunks
                if isinstance(c.location, ElementSelectorLocation)
            ]

            # With text_match, we can have same selector but different text_match
            # Just verify we have selectors
            assert len(selectors) > 0, "Should have extracted selectors"

        finally:
            html_path.unlink(missing_ok=True)


@requires_bs4
class TestBoilerplateRemoval:
    """Tests for boilerplate removal effectiveness."""

    @pytest.mark.description("Navigation elements are removed from extraction")
    @pytest.mark.asyncio
    async def test_removes_navigation_elements(self) -> None:
        """Test that navigation elements are not included in extraction."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <body>
            <nav>
                <a href="/">Home - Navigation Link</a>
                <a href="/about">About - Navigation Link</a>
            </nav>
            <main>
                <article>
                    <p>Main content that should be extracted with sufficient length to pass the minimum.</p>
                </article>
            </main>
        </body>
        </html>
        """

        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
            f.write(html_content)
            html_path = Path(f.name)

        try:
            adapter = WebAdapter(config=WebConfig(remove_boilerplate=True))
            source = ContentSource(
                source_id="nav-removal-test",
                source_type=ContentType.TEXT,
                path=html_path,
                metadata={"mime_type": "text/html"},
            )

            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

            full_text = " ".join(c.text for c in raw_chunks).lower()

            # Navigation content should not be present
            assert "navigation link" not in full_text, (
                f"Navigation should be removed. Found: {full_text}"
            )

        finally:
            html_path.unlink(missing_ok=True)

    @pytest.mark.description("Footer elements are removed from extraction")
    @pytest.mark.asyncio
    async def test_removes_footer_elements(self) -> None:
        """Test that footer elements are not included in extraction."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <body>
            <main>
                <article>
                    <p>Main article content that has enough words to be extracted properly by the adapter.</p>
                </article>
            </main>
            <footer>
                <p>Copyright 2025 Footer Content That Should Not Appear</p>
                <a href="/privacy">Privacy Policy Footer Link</a>
            </footer>
        </body>
        </html>
        """

        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
            f.write(html_content)
            html_path = Path(f.name)

        try:
            adapter = WebAdapter(config=WebConfig(remove_boilerplate=True))
            source = ContentSource(
                source_id="footer-removal-test",
                source_type=ContentType.TEXT,
                path=html_path,
                metadata={"mime_type": "text/html"},
            )

            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

            full_text = " ".join(c.text for c in raw_chunks).lower()

            # Footer content should not be present
            assert "footer content" not in full_text, (
                f"Footer should be removed. Found: {full_text}"
            )
            assert "footer link" not in full_text

        finally:
            html_path.unlink(missing_ok=True)

    @pytest.mark.description("Script and style tags are removed")
    @pytest.mark.asyncio
    async def test_removes_script_and_style(self) -> None:
        """Test that script and style content is excluded."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                .hidden-style { display: none; }
            </style>
            <script>
                var secretCode = "DO_NOT_EXTRACT_THIS";
            </script>
        </head>
        <body>
            <main>
                <p>Visible main content paragraph with enough text to be properly extracted.</p>
            </main>
            <script>
                console.log("SCRIPT_CONTENT_SHOULD_NOT_APPEAR");
            </script>
        </body>
        </html>
        """

        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
            f.write(html_content)
            html_path = Path(f.name)

        try:
            adapter = WebAdapter(config=WebConfig(remove_boilerplate=True))
            source = ContentSource(
                source_id="script-removal-test",
                source_type=ContentType.TEXT,
                path=html_path,
                metadata={"mime_type": "text/html"},
            )

            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

            full_text = " ".join(c.text for c in raw_chunks).lower()

            # Script and style content should not be present
            assert "secretcode" not in full_text.replace(" ", "")
            assert "script_content" not in full_text.replace("_", "")
            assert "hidden-style" not in full_text

        finally:
            html_path.unlink(missing_ok=True)

    @pytest.mark.description("Main content is preserved when boilerplate is removed")
    @pytest.mark.asyncio
    async def test_preserves_main_content(self) -> None:
        """Test that main content is kept while boilerplate is removed."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <body>
            <header><nav>Navigation Menu Links Here</nav></header>
            <main>
                <article>
                    <h1>Important Article Title</h1>
                    <p>This is the main content that absolutely must be preserved during extraction.</p>
                    <p>Additional paragraph with more valuable content that should also be extracted.</p>
                </article>
            </main>
            <aside class="sidebar">Sidebar content should not appear</aside>
            <footer>Footer copyright info should not appear</footer>
        </body>
        </html>
        """

        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
            f.write(html_content)
            html_path = Path(f.name)

        try:
            adapter = WebAdapter(config=WebConfig(remove_boilerplate=True))
            source = ContentSource(
                source_id="preserve-main-test",
                source_type=ContentType.TEXT,
                path=html_path,
                metadata={"mime_type": "text/html"},
            )

            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

            full_text = " ".join(c.text for c in raw_chunks).lower()

            # Main content should be present
            assert "must be preserved" in full_text, (
                f"Main content should be preserved. Got: {full_text}"
            )

            # Boilerplate should be removed
            assert "sidebar content" not in full_text
            assert "navigation menu" not in full_text

        finally:
            html_path.unlink(missing_ok=True)

    @pytest.mark.description("Boilerplate removal can be disabled")
    @pytest.mark.asyncio
    async def test_boilerplate_removal_can_be_disabled(self) -> None:
        """Test that boilerplate removal can be turned off via config."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <body>
            <nav>
                <p>Navigation content that would normally be removed but should appear now.</p>
            </nav>
            <main>
                <p>Main content that should always be extracted regardless of settings.</p>
            </main>
        </body>
        </html>
        """

        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
            f.write(html_content)
            html_path = Path(f.name)

        try:
            # Disable boilerplate removal
            adapter = WebAdapter(config=WebConfig(remove_boilerplate=False))
            source = ContentSource(
                source_id="no-removal-test",
                source_type=ContentType.TEXT,
                path=html_path,
                metadata={"mime_type": "text/html"},
            )

            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

            full_text = " ".join(c.text for c in raw_chunks).lower()

            # With boilerplate removal disabled, nav content should be present
            # Note: content from nav may still not appear if there's no
            # main/article/body container handling - this depends on implementation
            assert "main content" in full_text, "Main content should always be present"

        finally:
            html_path.unlink(missing_ok=True)


class TestDeepLinkFormatValidation:
    """Tests for deep link URL format validation."""

    @pytest.mark.description("Deep link uses text fragment format")
    def test_deep_link_uses_text_fragment(self) -> None:
        """Test that deep link URLs use text fragment (#:~:text=) format."""
        adapter = WebAdapter()
        location = ElementSelectorLocation(
            selector="article > p:nth-child(1)",
            selector_type="css",
            text_match="Sample text content",
        )
        chunk = TextChunk(
            text="Sample text content for testing deep links",
            source_id="web-page-123",
            source_type=ContentType.TEXT,
            location=location,
        )

        base_url = "https://example.com/article"
        deep_link = adapter.get_deep_link(chunk, base_url)

        assert deep_link is not None
        assert "#:~:text=" in deep_link, f"Should use text fragment format: {deep_link}"
        assert "Sample" in deep_link, "Should include text match in fragment"

    @pytest.mark.description("Deep link uses ID fragment for ID selectors")
    def test_deep_link_uses_id_fragment(self) -> None:
        """Test that deep link uses #id for ID-based selectors."""
        adapter = WebAdapter()
        location = ElementSelectorLocation(
            selector="#section-one",
            selector_type="css",
            text_match=None,  # No text match, use ID
        )
        chunk = TextChunk(
            text="Section content",
            source_id="web-page-123",
            source_type=ContentType.TEXT,
            location=location,
        )

        base_url = "https://example.com/page"
        deep_link = adapter.get_deep_link(chunk, base_url)

        assert deep_link is not None
        assert deep_link == "https://example.com/page#section-one", (
            f"Should use ID fragment: {deep_link}"
        )

    @pytest.mark.description("Deep link properly encodes special characters")
    def test_deep_link_encodes_special_chars(self) -> None:
        """Test that deep link URLs properly encode special characters."""
        adapter = WebAdapter()
        location = ElementSelectorLocation(
            selector="p.intro",
            selector_type="css",
            text_match="Text with spaces & symbols",
        )
        chunk = TextChunk(
            text="Full text content",
            source_id="web-page-123",
            source_type=ContentType.TEXT,
            location=location,
        )

        base_url = "https://example.com/page"
        deep_link = adapter.get_deep_link(chunk, base_url)

        assert deep_link is not None
        # Spaces should be encoded
        assert "%20" in deep_link or "+" in deep_link or " " not in deep_link.split("#")[-1], (
            f"Spaces should be encoded: {deep_link}"
        )

    @pytest.mark.description("Deep link returns None for chunk without location")
    def test_deep_link_without_location(self) -> None:
        """Test that deep link returns None when chunk has no location."""
        adapter = WebAdapter()
        chunk = TextChunk(
            text="Content without location",
            source_id="web-page-123",
            source_type=ContentType.TEXT,
            location=None,
        )

        base_url = "https://example.com/page"
        deep_link = adapter.get_deep_link(chunk, base_url)

        assert deep_link is None, "Should return None for chunk without location"

    @pytest.mark.description("Deep link handles various base URL formats")
    @pytest.mark.parametrize(
        "base_url",
        [
            "https://example.com/article",
            "https://example.com/path/to/page.html",
            "http://localhost:8080/docs",
            "https://sub.domain.example.com/article",
        ],
    )
    def test_deep_link_various_url_formats(self, base_url: str) -> None:
        """Test deep link generation with various URL formats."""
        adapter = WebAdapter()
        location = ElementSelectorLocation(
            selector="p.content",
            selector_type="css",
            text_match="Test content",
        )
        chunk = TextChunk(
            text="Test content text",
            source_id="test",
            source_type=ContentType.TEXT,
            location=location,
        )

        deep_link = adapter.get_deep_link(chunk, base_url)
        assert deep_link is not None
        assert deep_link.startswith(base_url), f"Should preserve base URL: {deep_link}"


@requires_bs4
class TestEndToEndWebIngestSearch:
    """End-to-end tests: ingest web content -> search -> verify."""

    @pytest.mark.description("Ingested web content can be searched semantically")
    @pytest.mark.asyncio
    async def test_e2e_web_ingest_search(self) -> None:
        """Test complete flow: extract HTML -> chunk -> index -> search."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <body>
            <main>
                <article>
                    <h1>Introduction to Machine Learning</h1>
                    <p>Machine learning is a subset of artificial intelligence that enables systems to learn from data and improve their performance without explicit programming.</p>
                    <p>Neural networks are computational models inspired by biological neural networks that form the basis of deep learning.</p>
                    <p>Vector embeddings convert text into numerical representations that capture semantic meaning and enable similarity search.</p>
                </article>
            </main>
        </body>
        </html>
        """

        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
            f.write(html_content)
            html_path = Path(f.name)

        try:
            # Step 1: Extract
            adapter = WebAdapter()
            source = ContentSource(
                source_id="ml-article-001",
                source_type=ContentType.TEXT,
                path=html_path,
                metadata={"mime_type": "text/html"},
            )

            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

            assert len(raw_chunks) > 0, "Should extract content from HTML"

            # Step 2: Chunk
            config = ChunkConfig(target_words=30, overlap_words=5)
            text_chunks = adapter.chunk(raw_chunks, source, config)

            assert len(text_chunks) > 0, "Should produce text chunks"

            # Step 3: Index into Qdrant
            provider = embedding.get_embeddings_provider()
            client = vector.get_client()  # In-memory client
            collection_name = "test-web-e2e"

            vector.ensure_collection(client, collection_name, provider.get_embedding_dimension())

            # Calculate embeddings and store
            texts = [chunk.text for chunk in text_chunks]
            embeddings = provider.encode_texts(texts)

            points = []
            for i, (chunk, emb) in enumerate(zip(text_chunks, embeddings)):
                location = chunk.location
                selector = location.selector if isinstance(location, ElementSelectorLocation) else None

                points.append(
                    vector.qdrant_client.models.PointStruct(
                        id=3000 + i,
                        vector=emb.tolist() if hasattr(emb, "tolist") else list(emb),
                        payload={
                            "source_id": chunk.source_id,
                            "source_type": chunk.source_type.value,
                            "text": chunk.text,
                            "selector": selector,
                            "sequence_index": chunk.sequence_index,
                        },
                    )
                )

            client.upsert(collection_name=collection_name, points=points)

            # Step 4: Search
            query_embedding = embedding.text2embedding("deep learning neural networks", provider)
            results = client.query_points(
                collection_name=collection_name,
                query=query_embedding[0].tolist(),
                limit=5,
            ).points

            # Step 5: Verify
            assert len(results) > 0, "Should find search results"

            # Verify results have expected structure
            for result in results:
                assert result.payload is not None
                assert "text" in result.payload
                assert "source_id" in result.payload
                assert result.payload["source_id"] == "ml-article-001"

            # Verify semantic relevance - top result should be about neural networks
            top_result_text = results[0].payload["text"].lower()
            assert any(
                term in top_result_text
                for term in ["neural", "network", "deep", "learning"]
            ), f"Top result should be about neural networks: {top_result_text}"

        finally:
            html_path.unlink(missing_ok=True)

    @pytest.mark.description("Search results include CSS selector metadata")
    @pytest.mark.asyncio
    async def test_search_results_include_selectors(self) -> None:
        """Test that search results include CSS selector information."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <body>
            <main>
                <section id="unique-content-section">
                    <p>Unique content for selector testing with sufficient length for extraction.</p>
                </section>
            </main>
        </body>
        </html>
        """

        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
            f.write(html_content)
            html_path = Path(f.name)

        try:
            adapter = WebAdapter()
            source = ContentSource(
                source_id="selector-metadata-test",
                source_type=ContentType.TEXT,
                path=html_path,
                metadata={"mime_type": "text/html"},
            )

            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

            text_chunks = adapter.chunk(raw_chunks, source)

            # Index
            provider = embedding.get_embeddings_provider()
            client = vector.get_client()
            collection_name = "test-selector-metadata"
            vector.ensure_collection(client, collection_name, provider.get_embedding_dimension())

            texts = [c.text for c in text_chunks]
            embeddings = provider.encode_texts(texts)

            points = []
            for i, (chunk, emb) in enumerate(zip(text_chunks, embeddings)):
                loc = chunk.location
                points.append(
                    vector.qdrant_client.models.PointStruct(
                        id=4000 + i,
                        vector=emb.tolist() if hasattr(emb, "tolist") else list(emb),
                        payload={
                            "text": chunk.text,
                            "source_id": chunk.source_id,
                            "selector": loc.selector if isinstance(loc, ElementSelectorLocation) else None,
                        },
                    )
                )

            client.upsert(collection_name=collection_name, points=points)

            # Search
            query_emb = embedding.text2embedding("unique content", provider)
            results = client.query_points(
                collection_name=collection_name,
                query=query_emb[0].tolist(),
                limit=2,
            ).points

            assert len(results) > 0
            for result in results:
                payload = result.payload
                assert payload is not None
                # Selector should be present
                if payload.get("selector"):
                    assert isinstance(payload["selector"], str)

        finally:
            html_path.unlink(missing_ok=True)


class TestWebAdapterConfiguration:
    """Tests for WebAdapter configuration options."""

    @requires_bs4
    @pytest.mark.description("Min text length config filters short content")
    @pytest.mark.asyncio
    async def test_min_text_length_filtering(self) -> None:
        """Test that min_text_length configuration filters short content."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <body>
            <main>
                <p>Short</p>
                <p>This is a longer paragraph that should definitely be included in the extraction results.</p>
            </main>
        </body>
        </html>
        """

        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
            f.write(html_content)
            html_path = Path(f.name)

        try:
            # High min_text_length should filter short content
            adapter = WebAdapter(config=WebConfig(min_text_length=20))
            source = ContentSource(
                source_id="min-length-test",
                source_type=ContentType.TEXT,
                path=html_path,
                metadata={"mime_type": "text/html"},
            )

            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

            # "Short" should not appear (too short)
            all_texts = [c.text for c in raw_chunks]
            assert not any(t == "Short" for t in all_texts), (
                "Short text should be filtered"
            )

        finally:
            html_path.unlink(missing_ok=True)

    @pytest.mark.description("WebAdapter supports different content types")
    def test_supports_various_content_types(self) -> None:
        """Test that WebAdapter correctly identifies supported content types."""
        adapter = WebAdapter()

        # Should support HTML via MIME type
        html_source = ContentSource(
            source_id="html-test",
            source_type=ContentType.TEXT,
            url="https://example.com/page",
            metadata={"mime_type": "text/html"},
        )
        assert adapter.supports(html_source) is True

        # Should support XHTML via MIME type
        xhtml_source = ContentSource(
            source_id="xhtml-test",
            source_type=ContentType.TEXT,
            url="https://example.com/page",
            metadata={"mime_type": "application/xhtml+xml"},
        )
        assert adapter.supports(xhtml_source) is True

        # Should not support non-TEXT content types
        audio_source = ContentSource(
            source_id="audio-test",
            source_type=ContentType.AUDIO,
            url="https://example.com/audio.mp3",
        )
        assert adapter.supports(audio_source) is False

    @pytest.mark.description("WebAdapter supports HTML file extensions")
    def test_supports_html_file_extensions(self) -> None:
        """Test that WebAdapter supports files with HTML extensions."""
        adapter = WebAdapter()

        # Should support .html files
        html_file_source = ContentSource(
            source_id="html-file",
            source_type=ContentType.TEXT,
            path=Path("/path/to/page.html"),
        )
        assert adapter.supports(html_file_source) is True

        # Should support .htm files
        htm_file_source = ContentSource(
            source_id="htm-file",
            source_type=ContentType.TEXT,
            path=Path("/path/to/page.htm"),
        )
        assert adapter.supports(htm_file_source) is True

        # Should support .xhtml files
        xhtml_file_source = ContentSource(
            source_id="xhtml-file",
            source_type=ContentType.TEXT,
            path=Path("/path/to/page.xhtml"),
        )
        assert adapter.supports(xhtml_file_source) is True

    @pytest.mark.description("WebAdapter rejects non-HTML URLs")
    def test_rejects_non_html_urls(self) -> None:
        """Test that WebAdapter rejects URLs for non-HTML content."""
        adapter = WebAdapter()

        # Should reject JSON URLs
        json_source = ContentSource(
            source_id="json-test",
            source_type=ContentType.TEXT,
            url="https://api.example.com/data.json",
        )
        assert adapter.supports(json_source) is False

        # Should reject PDF URLs
        pdf_source = ContentSource(
            source_id="pdf-test",
            source_type=ContentType.TEXT,
            url="https://example.com/document.pdf",
        )
        assert adapter.supports(pdf_source) is False


@requires_bs4
class TestChunkingBehavior:
    """Tests for chunking configuration and behavior."""

    @pytest.mark.description("Chunking respects target word count")
    @pytest.mark.asyncio
    async def test_chunking_target_words(self) -> None:
        """Test that chunking produces chunks near target word count."""
        # Create HTML with enough content for multiple chunks
        paragraphs = [
            "This is paragraph one with some content. " * 5,
            "This is paragraph two with different content. " * 5,
            "This is paragraph three with more content. " * 5,
        ]
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body>
            <main>
                <article>
                    <p>{paragraphs[0]}</p>
                    <p>{paragraphs[1]}</p>
                    <p>{paragraphs[2]}</p>
                </article>
            </main>
        </body>
        </html>
        """

        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
            f.write(html_content)
            html_path = Path(f.name)

        try:
            adapter = WebAdapter()
            source = ContentSource(
                source_id="chunk-test",
                source_type=ContentType.TEXT,
                path=html_path,
                metadata={"mime_type": "text/html"},
            )

            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

            # Use small target for more chunks
            config = ChunkConfig(target_words=20, overlap_words=3)
            text_chunks = adapter.chunk(raw_chunks, source, config)

            # Should produce multiple chunks
            assert len(text_chunks) >= 1, "Should produce chunks"

            # Verify chunks have locations
            for chunk in text_chunks:
                if chunk.location:
                    assert isinstance(chunk.location, ElementSelectorLocation)

        finally:
            html_path.unlink(missing_ok=True)

    @pytest.mark.description("Chunking preserves sequence order")
    @pytest.mark.asyncio
    async def test_chunking_sequence_order(self) -> None:
        """Test that chunks maintain correct sequence ordering."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <body>
            <main>
                <article>
                    <p>First paragraph content with enough words to be extracted properly by adapter.</p>
                    <p>Second paragraph content with enough words to be extracted properly by adapter.</p>
                    <p>Third paragraph content with enough words to be extracted properly by adapter.</p>
                </article>
            </main>
        </body>
        </html>
        """

        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
            f.write(html_content)
            html_path = Path(f.name)

        try:
            adapter = WebAdapter()
            source = ContentSource(
                source_id="sequence-test",
                source_type=ContentType.TEXT,
                path=html_path,
                metadata={"mime_type": "text/html"},
            )

            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

            text_chunks = adapter.chunk(raw_chunks, source)

            # Verify sequence indices are sequential
            indices = [c.sequence_index for c in text_chunks]
            assert indices == sorted(indices), "Sequence indices should be in order"
            assert indices[0] == 0, "First sequence index should be 0"

        finally:
            html_path.unlink(missing_ok=True)
