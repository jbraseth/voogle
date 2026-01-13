# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Integration tests for PdfAdapter content adapter.

Tests PDF extraction and location accuracy with:
- Multi-page PDF processing
- Text extraction completeness
- Page number accuracy
- Bounding box validation
- Complex layout tests (tables, columns)
- Deep link format validation
"""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from voogle import embedding, vector
from voogle.adapters.pdf import PdfAdapter, PdfConfig
from voogle.adapters.base import ChunkConfig, ContentSource, RawChunk, TextChunk
from voogle.core.fragment import ContentType
from voogle.core.location import PageBboxLocation

pytestmark = pytest.mark.integration


class TestPdfAdapterWithMultiPagePDF:
    """Integration tests for multi-page PDF processing."""

    @pytest.mark.description("PdfAdapter extracts text from all pages")
    @pytest.mark.asyncio
    async def test_adapter_extracts_all_pages(self, tmp_path: Path) -> None:
        """Test that PdfAdapter extracts content from multiple pages."""
        pdf_file = tmp_path / "multipage.pdf"
        pdf_file.touch()

        # Create mock blocks for 3 pages
        page1_block = _create_mock_text_block(
            "Page one content with introduction.",
            bbox=(50, 100, 450, 150),
            font_size=12.0,
        )
        page2_block = _create_mock_text_block(
            "Page two content with details.",
            bbox=(50, 100, 450, 150),
            font_size=12.0,
        )
        page3_block = _create_mock_text_block(
            "Page three content with conclusion.",
            bbox=(50, 100, 450, 150),
            font_size=12.0,
        )

        mock_pages = [
            _create_mock_page([page1_block]),
            _create_mock_page([page2_block]),
            _create_mock_page([page3_block]),
        ]

        mock_doc = _create_mock_document(mock_pages)
        mock_fitz = _create_mock_fitz(mock_doc)

        adapter = PdfAdapter()
        source = ContentSource(
            source_id="multipage-doc",
            source_type=ContentType.DOCUMENT,
            path=pdf_file,
        )

        with patch("voogle.adapters.pdf._get_fitz", return_value=mock_fitz):
            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

        # Should extract from all 3 pages
        assert len(raw_chunks) == 3, f"Expected 3 chunks, got {len(raw_chunks)}"

        # Verify page numbers
        pages_found = {chunk.location.page for chunk in raw_chunks}
        assert pages_found == {1, 2, 3}, f"Should find pages 1, 2, 3. Found: {pages_found}"

        # Verify content from each page
        texts = [chunk.text for chunk in raw_chunks]
        assert any("introduction" in t for t in texts), "Should include page 1 content"
        assert any("details" in t for t in texts), "Should include page 2 content"
        assert any("conclusion" in t for t in texts), "Should include page 3 content"

    @pytest.mark.description("PdfAdapter maintains correct page order")
    @pytest.mark.asyncio
    async def test_page_order_maintained(self, tmp_path: Path) -> None:
        """Test that chunks are extracted in page order."""
        pdf_file = tmp_path / "ordered.pdf"
        pdf_file.touch()

        # Create 5 pages with distinct content
        mock_pages = [
            _create_mock_page([_create_mock_text_block(f"Content for page {i + 1}")])
            for i in range(5)
        ]

        mock_doc = _create_mock_document(mock_pages)
        mock_fitz = _create_mock_fitz(mock_doc)

        adapter = PdfAdapter()
        source = ContentSource(
            source_id="ordered-doc",
            source_type=ContentType.DOCUMENT,
            path=pdf_file,
        )

        with patch("voogle.adapters.pdf._get_fitz", return_value=mock_fitz):
            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

        # Verify page numbers are in ascending order
        page_numbers = [chunk.location.page for chunk in raw_chunks]
        assert page_numbers == sorted(page_numbers), (
            f"Pages should be in order. Got: {page_numbers}"
        )

        # Verify all pages present
        assert set(page_numbers) == {1, 2, 3, 4, 5}


class TestTextExtractionCompleteness:
    """Tests for text extraction completeness."""

    @pytest.mark.description("All text blocks are extracted")
    @pytest.mark.asyncio
    async def test_all_blocks_extracted(self, tmp_path: Path) -> None:
        """Test that all text blocks from a page are extracted."""
        pdf_file = tmp_path / "multiblock.pdf"
        pdf_file.touch()

        # Create multiple blocks on a single page
        blocks = [
            _create_mock_text_block("First paragraph of text."),
            _create_mock_text_block("Second paragraph of text."),
            _create_mock_text_block("Third paragraph of text."),
            _create_mock_text_block("Fourth paragraph of text."),
        ]

        mock_pages = [_create_mock_page(blocks)]
        mock_doc = _create_mock_document(mock_pages)
        mock_fitz = _create_mock_fitz(mock_doc)

        adapter = PdfAdapter()
        source = ContentSource(
            source_id="multiblock-doc",
            source_type=ContentType.DOCUMENT,
            path=pdf_file,
        )

        with patch("voogle.adapters.pdf._get_fitz", return_value=mock_fitz):
            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

        # Should extract all 4 blocks
        assert len(raw_chunks) == 4, f"Expected 4 blocks, got {len(raw_chunks)}"

        # Verify each block's content is present
        all_text = " ".join(chunk.text for chunk in raw_chunks)
        assert "First" in all_text
        assert "Second" in all_text
        assert "Third" in all_text
        assert "Fourth" in all_text

    @pytest.mark.description("Text with multiple lines is properly joined")
    @pytest.mark.asyncio
    async def test_multiline_text_joined(self, tmp_path: Path) -> None:
        """Test that multi-line text blocks are properly joined."""
        pdf_file = tmp_path / "multiline.pdf"
        pdf_file.touch()

        # Create a block with multiple lines
        multiline_block = {
            "type": 0,
            "bbox": (50, 100, 450, 200),
            "lines": [
                {"spans": [{"text": "First line of text.", "size": 12.0, "font": "Helvetica"}]},
                {"spans": [{"text": "Second line continues.", "size": 12.0, "font": "Helvetica"}]},
                {"spans": [{"text": "Third line ends.", "size": 12.0, "font": "Helvetica"}]},
            ],
        }

        mock_pages = [_create_mock_page([multiline_block])]
        mock_doc = _create_mock_document(mock_pages)
        mock_fitz = _create_mock_fitz(mock_doc)

        adapter = PdfAdapter()
        source = ContentSource(
            source_id="multiline-doc",
            source_type=ContentType.DOCUMENT,
            path=pdf_file,
        )

        with patch("voogle.adapters.pdf._get_fitz", return_value=mock_fitz):
            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

        # Should produce one chunk with all lines joined
        assert len(raw_chunks) == 1
        text = raw_chunks[0].text
        assert "First line of text." in text
        assert "Second line continues." in text
        assert "Third line ends." in text

    @pytest.mark.description("Empty blocks are skipped")
    @pytest.mark.asyncio
    async def test_empty_blocks_skipped(self, tmp_path: Path) -> None:
        """Test that empty or whitespace-only blocks are skipped."""
        pdf_file = tmp_path / "empty.pdf"
        pdf_file.touch()

        blocks = [
            _create_mock_text_block("Real content here."),
            _create_mock_text_block("   "),  # Whitespace only
            _create_mock_text_block(""),  # Empty
            _create_mock_text_block("More real content."),
        ]

        mock_pages = [_create_mock_page(blocks)]
        mock_doc = _create_mock_document(mock_pages)
        mock_fitz = _create_mock_fitz(mock_doc)

        adapter = PdfAdapter()
        source = ContentSource(
            source_id="empty-doc",
            source_type=ContentType.DOCUMENT,
            path=pdf_file,
        )

        with patch("voogle.adapters.pdf._get_fitz", return_value=mock_fitz):
            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

        # Should only extract non-empty blocks
        assert len(raw_chunks) == 2
        texts = [chunk.text for chunk in raw_chunks]
        assert "Real content here." in texts
        assert "More real content." in texts


class TestPageNumberAccuracy:
    """Tests for page number accuracy."""

    @pytest.mark.description("Page numbers are 1-indexed")
    @pytest.mark.asyncio
    async def test_page_numbers_one_indexed(self, tmp_path: Path) -> None:
        """Test that page numbers start at 1, not 0."""
        pdf_file = tmp_path / "pages.pdf"
        pdf_file.touch()

        mock_pages = [
            _create_mock_page([_create_mock_text_block("First page content.")])
        ]
        mock_doc = _create_mock_document(mock_pages)
        mock_fitz = _create_mock_fitz(mock_doc)

        adapter = PdfAdapter()
        source = ContentSource(
            source_id="pages-doc",
            source_type=ContentType.DOCUMENT,
            path=pdf_file,
        )

        with patch("voogle.adapters.pdf._get_fitz", return_value=mock_fitz):
            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

        assert len(raw_chunks) == 1
        assert raw_chunks[0].location.page == 1, "First page should be numbered 1"

    @pytest.mark.description("Page numbers increment correctly")
    @pytest.mark.asyncio
    async def test_page_numbers_increment(self, tmp_path: Path) -> None:
        """Test that page numbers increment correctly across pages."""
        pdf_file = tmp_path / "increment.pdf"
        pdf_file.touch()

        mock_pages = [
            _create_mock_page([_create_mock_text_block(f"Page {i + 1}")])
            for i in range(10)
        ]
        mock_doc = _create_mock_document(mock_pages)
        mock_fitz = _create_mock_fitz(mock_doc)

        adapter = PdfAdapter()
        source = ContentSource(
            source_id="increment-doc",
            source_type=ContentType.DOCUMENT,
            path=pdf_file,
        )

        with patch("voogle.adapters.pdf._get_fitz", return_value=mock_fitz):
            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

        # Verify page numbers 1 through 10
        page_numbers = [chunk.location.page for chunk in raw_chunks]
        assert page_numbers == list(range(1, 11)), (
            f"Expected pages 1-10, got {page_numbers}"
        )

    @pytest.mark.description("Multiple blocks on same page have same page number")
    @pytest.mark.asyncio
    async def test_same_page_blocks_same_number(self, tmp_path: Path) -> None:
        """Test that all blocks on the same page have the same page number."""
        pdf_file = tmp_path / "samepage.pdf"
        pdf_file.touch()

        # Multiple blocks on page 2
        blocks_page2 = [
            _create_mock_text_block("Block A on page 2."),
            _create_mock_text_block("Block B on page 2."),
            _create_mock_text_block("Block C on page 2."),
        ]

        mock_pages = [
            _create_mock_page([_create_mock_text_block("Page 1 content.")]),
            _create_mock_page(blocks_page2),
        ]
        mock_doc = _create_mock_document(mock_pages)
        mock_fitz = _create_mock_fitz(mock_doc)

        adapter = PdfAdapter()
        source = ContentSource(
            source_id="samepage-doc",
            source_type=ContentType.DOCUMENT,
            path=pdf_file,
        )

        with patch("voogle.adapters.pdf._get_fitz", return_value=mock_fitz):
            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

        # Chunks from page 2 should all have page=2
        page2_chunks = [c for c in raw_chunks if c.location.page == 2]
        assert len(page2_chunks) == 3, f"Expected 3 chunks from page 2, got {len(page2_chunks)}"


class TestBoundingBoxValidation:
    """Tests for bounding box validation."""

    @pytest.mark.description("Bounding box values are in valid range 0-100")
    @pytest.mark.asyncio
    async def test_bbox_values_in_range(self, tmp_path: Path) -> None:
        """Test that all bounding box values are in the 0-100 range."""
        pdf_file = tmp_path / "bbox.pdf"
        pdf_file.touch()

        # Create blocks at various positions
        blocks = [
            _create_mock_text_block("Top left", bbox=(0, 0, 100, 50)),
            _create_mock_text_block("Center", bbox=(200, 300, 400, 400)),
            _create_mock_text_block("Bottom right", bbox=(400, 600, 500, 700)),
        ]

        mock_pages = [_create_mock_page(blocks, page_width=500, page_height=700)]
        mock_doc = _create_mock_document(mock_pages)
        mock_fitz = _create_mock_fitz(mock_doc)

        adapter = PdfAdapter()
        source = ContentSource(
            source_id="bbox-doc",
            source_type=ContentType.DOCUMENT,
            path=pdf_file,
        )

        with patch("voogle.adapters.pdf._get_fitz", return_value=mock_fitz):
            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

        for chunk in raw_chunks:
            loc = chunk.location
            assert isinstance(loc, PageBboxLocation), "Location should be PageBboxLocation"
            assert 0 <= loc.x <= 100, f"x={loc.x} should be in [0, 100]"
            assert 0 <= loc.y <= 100, f"y={loc.y} should be in [0, 100]"
            assert 0 <= loc.width <= 100, f"width={loc.width} should be in [0, 100]"
            assert 0 <= loc.height <= 100, f"height={loc.height} should be in [0, 100]"

    @pytest.mark.description("Bounding box is calculated as percentage of page")
    @pytest.mark.asyncio
    async def test_bbox_as_percentage(self, tmp_path: Path) -> None:
        """Test that bounding box is correctly calculated as percentage of page."""
        pdf_file = tmp_path / "percent.pdf"
        pdf_file.touch()

        # Block at 25% from left, 50% from top
        # Page is 500x700, block is at (125, 350) with size (250, 175)
        block = _create_mock_text_block(
            "Positioned block",
            bbox=(125, 350, 375, 525),
        )

        mock_pages = [_create_mock_page([block], page_width=500, page_height=700)]
        mock_doc = _create_mock_document(mock_pages)
        mock_fitz = _create_mock_fitz(mock_doc)

        adapter = PdfAdapter()
        source = ContentSource(
            source_id="percent-doc",
            source_type=ContentType.DOCUMENT,
            path=pdf_file,
        )

        with patch("voogle.adapters.pdf._get_fitz", return_value=mock_fitz):
            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

        assert len(raw_chunks) == 1
        loc = raw_chunks[0].location

        # Verify percentage calculations (with tolerance for floating point)
        assert abs(loc.x - 25.0) < 0.1, f"x should be ~25%, got {loc.x}"
        assert abs(loc.y - 50.0) < 0.1, f"y should be ~50%, got {loc.y}"
        assert abs(loc.width - 50.0) < 0.1, f"width should be ~50%, got {loc.width}"
        assert abs(loc.height - 25.0) < 0.1, f"height should be ~25%, got {loc.height}"

    @pytest.mark.description("Bounding box values are clamped to valid range")
    @pytest.mark.asyncio
    async def test_bbox_clamped(self, tmp_path: Path) -> None:
        """Test that out-of-bounds bounding box values are clamped."""
        pdf_file = tmp_path / "clamped.pdf"
        pdf_file.touch()

        # Block that extends beyond page boundaries
        block = _create_mock_text_block(
            "Overflow block",
            bbox=(-50, -50, 600, 800),  # Beyond 500x700 page
        )

        mock_pages = [_create_mock_page([block], page_width=500, page_height=700)]
        mock_doc = _create_mock_document(mock_pages)
        mock_fitz = _create_mock_fitz(mock_doc)

        adapter = PdfAdapter()
        source = ContentSource(
            source_id="clamped-doc",
            source_type=ContentType.DOCUMENT,
            path=pdf_file,
        )

        with patch("voogle.adapters.pdf._get_fitz", return_value=mock_fitz):
            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

        assert len(raw_chunks) == 1
        loc = raw_chunks[0].location

        # Values should be clamped to valid range
        assert 0 <= loc.x <= 100
        assert 0 <= loc.y <= 100
        assert 0 <= loc.width <= 100
        assert 0 <= loc.height <= 100
        # x + width should not exceed 100
        assert loc.x + loc.width <= 100.01  # Allow small floating point error


class TestComplexLayoutsTablesColumns:
    """Tests for complex PDF layouts (tables, columns)."""

    @pytest.mark.description("Tables are detected and extracted")
    @pytest.mark.asyncio
    async def test_table_detection(self, tmp_path: Path) -> None:
        """Test that tables are detected and extracted."""
        pdf_file = tmp_path / "tables.pdf"
        pdf_file.touch()

        # Create a mock table
        mock_table = MagicMock()
        mock_table.bbox = (50, 200, 450, 400)

        # Mock DataFrame for table content
        mock_df = MagicMock()
        mock_df.iterrows.return_value = iter([
            (0, MagicMock(__iter__=lambda s: iter(["Header A", "Header B"]))),
            (1, MagicMock(__iter__=lambda s: iter(["Row 1 Col A", "Row 1 Col B"]))),
            (2, MagicMock(__iter__=lambda s: iter(["Row 2 Col A", "Row 2 Col B"]))),
        ])
        mock_df.columns = ["A", "B"]
        mock_table.to_pandas.return_value = mock_df

        mock_page = _create_mock_page([_create_mock_text_block("Regular text.")])
        mock_page.find_tables.return_value = [mock_table]

        mock_doc = _create_mock_document([mock_page])
        mock_fitz = _create_mock_fitz(mock_doc)

        adapter = PdfAdapter(config=PdfConfig(detect_tables=True))
        source = ContentSource(
            source_id="tables-doc",
            source_type=ContentType.DOCUMENT,
            path=pdf_file,
        )

        with patch("voogle.adapters.pdf._get_fitz", return_value=mock_fitz):
            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

        # Should have text block + table block
        assert len(raw_chunks) >= 1

        # Find the table chunk
        table_chunks = [c for c in raw_chunks if c.metadata.get("block_type") == "table"]
        assert len(table_chunks) == 1, "Should extract one table"

        # Verify table metadata
        table_chunk = table_chunks[0]
        assert table_chunk.metadata["rows"] == 3
        assert table_chunk.metadata["columns"] == 2

        # Verify table text contains pipe separators
        assert "|" in table_chunk.text

    @pytest.mark.description("Table detection can be disabled")
    @pytest.mark.asyncio
    async def test_table_detection_disabled(self, tmp_path: Path) -> None:
        """Test that table detection can be disabled."""
        pdf_file = tmp_path / "notables.pdf"
        pdf_file.touch()

        mock_page = _create_mock_page([_create_mock_text_block("Just text.")])
        mock_doc = _create_mock_document([mock_page])
        mock_fitz = _create_mock_fitz(mock_doc)

        # Disable table detection
        adapter = PdfAdapter(config=PdfConfig(detect_tables=False))
        source = ContentSource(
            source_id="notables-doc",
            source_type=ContentType.DOCUMENT,
            path=pdf_file,
        )

        with patch("voogle.adapters.pdf._get_fitz", return_value=mock_fitz):
            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

        # Should not call find_tables
        mock_page.find_tables.assert_not_called()

        # Only text block should be extracted
        assert len(raw_chunks) == 1
        assert raw_chunks[0].metadata.get("block_type") == "text"

    @pytest.mark.description("Headings are detected based on font size")
    @pytest.mark.asyncio
    async def test_heading_detection(self, tmp_path: Path) -> None:
        """Test that headings are detected based on font size ratio."""
        pdf_file = tmp_path / "headings.pdf"
        pdf_file.touch()

        # Create blocks with different font sizes
        heading_block = _create_mock_text_block(
            "Chapter One: Introduction",
            font_size=24.0,
            font_name="Helvetica-Bold",
        )
        body_block = _create_mock_text_block(
            "This is the body text of the chapter with regular formatting.",
            font_size=12.0,
        )
        subheading_block = _create_mock_text_block(
            "Section 1.1: Details",
            font_size=18.0,
        )

        mock_pages = [_create_mock_page([heading_block, body_block, subheading_block])]
        mock_doc = _create_mock_document(mock_pages)
        mock_fitz = _create_mock_fitz(mock_doc)

        adapter = PdfAdapter(config=PdfConfig(detect_headings=True))
        source = ContentSource(
            source_id="headings-doc",
            source_type=ContentType.DOCUMENT,
            path=pdf_file,
        )

        with patch("voogle.adapters.pdf._get_fitz", return_value=mock_fitz):
            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

        # Find heading chunks
        heading_chunks = [c for c in raw_chunks if c.metadata.get("is_heading")]

        # Should detect the large font blocks as headings
        assert len(heading_chunks) >= 1, "Should detect at least one heading"

        # Verify heading levels
        for chunk in heading_chunks:
            assert "heading_level" in chunk.metadata
            assert 1 <= chunk.metadata["heading_level"] <= 6

    @pytest.mark.description("Multi-column layout extracts all columns")
    @pytest.mark.asyncio
    async def test_multicolumn_extraction(self, tmp_path: Path) -> None:
        """Test that multi-column layouts have all columns extracted."""
        pdf_file = tmp_path / "columns.pdf"
        pdf_file.touch()

        # Simulate two-column layout with blocks at different x positions
        left_column = _create_mock_text_block(
            "Left column content.",
            bbox=(50, 100, 250, 500),
        )
        right_column = _create_mock_text_block(
            "Right column content.",
            bbox=(260, 100, 460, 500),
        )

        mock_pages = [_create_mock_page([left_column, right_column])]
        mock_doc = _create_mock_document(mock_pages)
        mock_fitz = _create_mock_fitz(mock_doc)

        adapter = PdfAdapter()
        source = ContentSource(
            source_id="columns-doc",
            source_type=ContentType.DOCUMENT,
            path=pdf_file,
        )

        with patch("voogle.adapters.pdf._get_fitz", return_value=mock_fitz):
            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

        # Both columns should be extracted
        assert len(raw_chunks) == 2

        texts = [chunk.text for chunk in raw_chunks]
        assert any("Left column" in t for t in texts)
        assert any("Right column" in t for t in texts)


class TestDeepLinkFormatValidation:
    """Tests for deep link URL format validation."""

    @pytest.mark.description("Deep link includes page parameter")
    def test_deep_link_includes_page(self) -> None:
        """Test that deep link URLs include the page parameter."""
        adapter = PdfAdapter()
        location = PageBboxLocation(page=5, x=10, y=20, width=80, height=10)
        chunk = TextChunk(
            text="Test content",
            source_id="doc-123",
            source_type=ContentType.DOCUMENT,
            location=location,
        )

        base_url = "https://example.com/document.pdf"
        deep_link = adapter.get_deep_link(chunk, base_url)

        assert deep_link is not None
        assert "page=5" in deep_link, f"Deep link should include page: {deep_link}"

    @pytest.mark.description("Deep link uses hash fragment format")
    def test_deep_link_uses_fragment(self) -> None:
        """Test that deep link uses URL fragment (#) format."""
        adapter = PdfAdapter()
        location = PageBboxLocation(page=3)
        chunk = TextChunk(
            text="Test",
            source_id="doc",
            source_type=ContentType.DOCUMENT,
            location=location,
        )

        base_url = "https://example.com/doc.pdf"
        deep_link = adapter.get_deep_link(chunk, base_url)

        assert deep_link is not None
        assert "#" in deep_link, "Deep link should use fragment"
        assert deep_link.startswith(base_url), "Should preserve base URL"
        assert deep_link.endswith("#page=3"), f"Should end with #page=3: {deep_link}"

    @pytest.mark.description("Deep link includes viewrect for non-default bbox")
    def test_deep_link_includes_viewrect(self) -> None:
        """Test that deep link includes viewrect for specific bounding boxes."""
        adapter = PdfAdapter()
        location = PageBboxLocation(page=2, x=10, y=20, width=60, height=30)
        chunk = TextChunk(
            text="Test",
            source_id="doc",
            source_type=ContentType.DOCUMENT,
            location=location,
        )

        base_url = "https://example.com/doc.pdf"
        deep_link = adapter.get_deep_link(chunk, base_url)

        assert deep_link is not None
        assert "page=2" in deep_link
        assert "viewrect=" in deep_link, "Should include viewrect for custom bbox"

    @pytest.mark.description("Deep link omits viewrect for default bbox")
    def test_deep_link_omits_default_viewrect(self) -> None:
        """Test that default full-page bbox doesn't include viewrect."""
        adapter = PdfAdapter()
        # Default bbox is x=0, y=0, width=100, height=100
        location = PageBboxLocation(page=1, x=0, y=0, width=100, height=100)
        chunk = TextChunk(
            text="Test",
            source_id="doc",
            source_type=ContentType.DOCUMENT,
            location=location,
        )

        base_url = "https://example.com/doc.pdf"
        deep_link = adapter.get_deep_link(chunk, base_url)

        assert deep_link is not None
        assert "viewrect" not in deep_link, "Should not include viewrect for default bbox"

    @pytest.mark.description("Deep link returns None without location")
    def test_deep_link_without_location(self) -> None:
        """Test that deep link returns None when chunk has no location."""
        adapter = PdfAdapter()
        chunk = TextChunk(
            text="Test content",
            source_id="doc-123",
            source_type=ContentType.DOCUMENT,
            location=None,
        )

        base_url = "https://example.com/document.pdf"
        deep_link = adapter.get_deep_link(chunk, base_url)

        assert deep_link is None, "Should return None for chunk without location"

    @pytest.mark.description("Deep link handles various base URL formats")
    @pytest.mark.parametrize(
        "base_url,expected_in_link",
        [
            ("https://example.com/doc.pdf", "#page="),
            ("http://localhost:8080/files/document.pdf", "#page="),
            ("https://cdn.example.com/path/to/file.pdf", "#page="),
            ("https://drive.google.com/viewer?id=abc123", "#page="),
        ],
    )
    def test_deep_link_various_urls(self, base_url: str, expected_in_link: str) -> None:
        """Test deep link works with various URL formats."""
        adapter = PdfAdapter()
        location = PageBboxLocation(page=7)
        chunk = TextChunk(
            text="Test",
            source_id="test",
            source_type=ContentType.DOCUMENT,
            location=location,
        )

        deep_link = adapter.get_deep_link(chunk, base_url)
        assert deep_link is not None
        assert expected_in_link in deep_link
        assert "page=7" in deep_link


class TestEndToEndPdfIngestSearchVerify:
    """End-to-end tests: ingest -> chunk -> index -> search -> verify."""

    @pytest.mark.description("Ingested PDF can be searched and results verified")
    @pytest.mark.asyncio
    async def test_e2e_pdf_ingest_search_verify(self, tmp_path: Path) -> None:
        """Test complete flow: ingest PDF -> index -> search -> verify results."""
        pytest.importorskip("sentence_transformers", reason="sentence-transformers not installed")

        pdf_file = tmp_path / "searchable.pdf"
        pdf_file.touch()

        # Create multi-page PDF content about different topics
        pages_content = [
            _create_mock_page([
                _create_mock_text_block(
                    "Introduction to machine learning and artificial intelligence. "
                    "Neural networks are fundamental to deep learning systems."
                )
            ]),
            _create_mock_page([
                _create_mock_text_block(
                    "Database systems provide structured data storage. "
                    "SQL queries enable efficient data retrieval."
                )
            ]),
            _create_mock_page([
                _create_mock_text_block(
                    "Vector embeddings represent semantic meaning. "
                    "Similarity search finds related content."
                )
            ]),
        ]

        mock_doc = _create_mock_document(pages_content)
        mock_fitz = _create_mock_fitz(mock_doc)

        # Step 1: Extract (ingest)
        adapter = PdfAdapter()
        source = ContentSource(
            source_id="test-pdf-001",
            source_type=ContentType.DOCUMENT,
            path=pdf_file,
        )

        with patch("voogle.adapters.pdf._get_fitz", return_value=mock_fitz):
            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

        assert len(raw_chunks) == 3, f"Should extract 3 pages, got {len(raw_chunks)}"

        # Step 2: Chunk
        config = ChunkConfig(target_words=40, overlap_words=5)
        text_chunks = adapter.chunk(raw_chunks, source, config)

        assert len(text_chunks) > 0, "Should produce text chunks"

        # Step 3: Index into Qdrant
        provider = embedding.get_embeddings_provider()
        client = vector.get_client()
        collection_name = "test-pdf-e2e"

        vector.ensure_collection(client, collection_name, provider.get_embedding_dimension())

        texts = [chunk.text for chunk in text_chunks]
        embeddings = provider.encode_texts(texts)

        points = []
        for i, (chunk, emb) in enumerate(zip(text_chunks, embeddings)):
            location = chunk.location
            page = location.page if isinstance(location, PageBboxLocation) else None

            points.append(
                vector.qdrant_client.models.PointStruct(
                    id=3000 + i,
                    vector=emb.tolist() if hasattr(emb, "tolist") else list(emb),
                    payload={
                        "source_id": chunk.source_id,
                        "source_type": chunk.source_type.value,
                        "text": chunk.text,
                        "page": page,
                        "sequence_index": chunk.sequence_index,
                    },
                )
            )

        client.upsert(collection_name=collection_name, points=points)

        # Step 4: Search
        query_embedding = embedding.text2embedding("neural networks deep learning", provider)
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
            assert result.payload["source_id"] == "test-pdf-001"

        # Verify semantic relevance - top result should be about ML/AI
        top_result_text = results[0].payload["text"].lower()
        assert any(
            term in top_result_text
            for term in ["machine", "learning", "neural", "artificial", "intelligence"]
        ), f"Top result should be about ML: {top_result_text}"

    @pytest.mark.description("Search results include page metadata")
    @pytest.mark.asyncio
    async def test_search_results_include_page(self, tmp_path: Path) -> None:
        """Test that search results include page number metadata."""
        pytest.importorskip("sentence_transformers", reason="sentence-transformers not installed")

        pdf_file = tmp_path / "paged.pdf"
        pdf_file.touch()

        # Create pages with distinct content
        pages_content = [
            _create_mock_page([_create_mock_text_block("Page one unique content alpha.")]),
            _create_mock_page([_create_mock_text_block("Page two unique content beta.")]),
        ]

        mock_doc = _create_mock_document(pages_content)
        mock_fitz = _create_mock_fitz(mock_doc)

        adapter = PdfAdapter()
        source = ContentSource(
            source_id="test-paged",
            source_type=ContentType.DOCUMENT,
            path=pdf_file,
        )

        with patch("voogle.adapters.pdf._get_fitz", return_value=mock_fitz):
            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

        text_chunks = adapter.chunk(raw_chunks, source)

        # Index
        provider = embedding.get_embeddings_provider()
        client = vector.get_client()
        collection_name = "test-paged-collection"
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
                        "page": loc.page if isinstance(loc, PageBboxLocation) else None,
                    },
                )
            )

        client.upsert(collection_name=collection_name, points=points)

        # Search
        query_emb = embedding.text2embedding("beta content", provider)
        results = client.query_points(
            collection_name=collection_name,
            query=query_emb[0].tolist(),
            limit=2,
        ).points

        assert len(results) > 0

        # Verify page metadata is present
        for result in results:
            payload = result.payload
            assert payload is not None
            assert "page" in payload
            if payload.get("page") is not None:
                assert payload["page"] >= 1, "Page should be 1-indexed"


class TestChunkingWithLocations:
    """Tests for chunking behavior with page locations."""

    @pytest.mark.description("Chunking preserves first block's location")
    @pytest.mark.asyncio
    async def test_chunking_preserves_location(self, tmp_path: Path) -> None:
        """Test that chunking preserves the first raw chunk's location."""
        pdf_file = tmp_path / "chunkloc.pdf"
        pdf_file.touch()

        # Create multiple blocks on same page
        blocks = [
            _create_mock_text_block(
                "First block with some words for chunking.",
                bbox=(50, 100, 450, 150),
            ),
            _create_mock_text_block(
                "Second block continues the content with more words.",
                bbox=(50, 160, 450, 210),
            ),
        ]

        mock_pages = [_create_mock_page(blocks)]
        mock_doc = _create_mock_document(mock_pages)
        mock_fitz = _create_mock_fitz(mock_doc)

        adapter = PdfAdapter()
        source = ContentSource(
            source_id="chunkloc-doc",
            source_type=ContentType.DOCUMENT,
            path=pdf_file,
        )

        with patch("voogle.adapters.pdf._get_fitz", return_value=mock_fitz):
            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

        # Chunk with small target to force combining
        config = ChunkConfig(target_words=20, overlap_words=3)
        text_chunks = adapter.chunk(raw_chunks, source, config)

        # Verify chunks have locations from first contributing block
        assert len(text_chunks) > 0
        for chunk in text_chunks:
            assert chunk.location is not None
            assert isinstance(chunk.location, PageBboxLocation)
            assert chunk.location.page == 1

    @pytest.mark.description("Chunking assigns correct sequence indices")
    @pytest.mark.asyncio
    async def test_chunking_sequence_indices(self, tmp_path: Path) -> None:
        """Test that chunks have sequential indices."""
        pdf_file = tmp_path / "sequence.pdf"
        pdf_file.touch()

        # Create enough content for multiple chunks
        blocks = [
            _create_mock_text_block(" ".join(["word"] * 50))
            for _ in range(3)
        ]

        mock_pages = [_create_mock_page(blocks)]
        mock_doc = _create_mock_document(mock_pages)
        mock_fitz = _create_mock_fitz(mock_doc)

        adapter = PdfAdapter()
        source = ContentSource(
            source_id="sequence-doc",
            source_type=ContentType.DOCUMENT,
            path=pdf_file,
        )

        with patch("voogle.adapters.pdf._get_fitz", return_value=mock_fitz):
            raw_chunks: list[RawChunk] = []
            async for chunk in adapter.extract(source):
                raw_chunks.append(chunk)

        config = ChunkConfig(target_words=40, overlap_words=5)
        text_chunks = adapter.chunk(raw_chunks, source, config)

        # Verify sequence indices
        indices = [chunk.sequence_index for chunk in text_chunks]
        assert indices == list(range(len(text_chunks))), (
            f"Sequence indices should be 0, 1, 2, ... Got: {indices}"
        )


# Helper functions for creating mock objects


def _create_mock_text_block(
    text: str,
    bbox: tuple[float, float, float, float] = (50, 100, 450, 150),
    font_size: float = 12.0,
    font_name: str = "Helvetica",
) -> dict:
    """Create a mock PyMuPDF text block."""
    return {
        "type": 0,  # Text block
        "bbox": bbox,
        "lines": [
            {
                "spans": [
                    {
                        "text": text,
                        "size": font_size,
                        "font": font_name,
                    }
                ]
            }
        ],
    }


def _create_mock_page(
    blocks: list[dict],
    page_width: float = 500,
    page_height: float = 700,
) -> MagicMock:
    """Create a mock PyMuPDF page."""
    mock_page = MagicMock()
    mock_page.rect.width = page_width
    mock_page.rect.height = page_height
    mock_page.get_text.return_value = {"blocks": blocks}
    mock_page.find_tables.return_value = []
    return mock_page


def _create_mock_document(pages: list[MagicMock]) -> MagicMock:
    """Create a mock PyMuPDF document."""
    mock_doc = MagicMock()
    mock_doc.__len__ = MagicMock(return_value=len(pages))
    mock_doc.__iter__ = MagicMock(return_value=iter(pages))
    mock_doc.__getitem__ = MagicMock(side_effect=lambda i: pages[i])
    return mock_doc


def _create_mock_fitz(mock_doc: MagicMock) -> MagicMock:
    """Create a mock fitz (PyMuPDF) module."""
    mock_fitz = MagicMock()
    mock_fitz.open.return_value = mock_doc
    mock_fitz.TEXT_PRESERVE_WHITESPACE = 1
    return mock_fitz
