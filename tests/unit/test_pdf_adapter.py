# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for PdfAdapter content adapter."""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from voogle.adapters.pdf import (
    PDF_EXTENSIONS,
    PdfAdapter,
    PdfConfig,
)
from voogle.adapters.base import ChunkConfig, ContentSource, RawChunk
from voogle.core.fragment import ContentType
from voogle.core.location import PageBboxLocation

pytestmark = pytest.mark.unit


class TestPdfAdapterInit:
    """Tests for PdfAdapter initialization."""

    @pytest.mark.description("PdfAdapter initializes with default config")
    def test_init_default_config(self) -> None:
        adapter = PdfAdapter()
        assert adapter._config.extract_images is False
        assert adapter._config.detect_tables is True
        assert adapter._config.detect_headings is True
        assert adapter._config.min_heading_size == 1.2
        assert adapter._config.ocr_language == "eng"

    @pytest.mark.description("PdfAdapter initializes with custom config")
    def test_init_custom_config(self) -> None:
        config = PdfConfig(
            extract_images=True,
            detect_tables=False,
            detect_headings=False,
            min_heading_size=1.5,
            ocr_language="deu",
        )
        adapter = PdfAdapter(config=config)
        assert adapter._config.extract_images is True
        assert adapter._config.detect_tables is False
        assert adapter._config.detect_headings is False
        assert adapter._config.min_heading_size == 1.5
        assert adapter._config.ocr_language == "deu"


class TestPdfAdapterSupportedTypes:
    """Tests for PdfAdapter.supported_types property."""

    @pytest.mark.description("supported_types returns DOCUMENT only")
    def test_supported_types(self) -> None:
        adapter = PdfAdapter()
        assert adapter.supported_types == frozenset({ContentType.DOCUMENT})


class TestPdfAdapterSupports:
    """Tests for PdfAdapter.supports method."""

    @pytest.mark.description("supports returns True for PDF files")
    def test_supports_pdf(self) -> None:
        adapter = PdfAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.DOCUMENT,
            path=Path("/data/document.pdf"),
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns True for uppercase PDF extension")
    def test_supports_pdf_uppercase(self) -> None:
        adapter = PdfAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.DOCUMENT,
            path=Path("/data/document.PDF"),
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns False for non-document content type")
    def test_rejects_non_document_type(self) -> None:
        adapter = PdfAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.AUDIO,
            path=Path("/data/audio.mp3"),
        )
        assert adapter.supports(source) is False

    @pytest.mark.description("supports returns False for non-PDF document")
    def test_rejects_non_pdf_document(self) -> None:
        adapter = PdfAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.DOCUMENT,
            path=Path("/data/document.docx"),
        )
        assert adapter.supports(source) is False

    @pytest.mark.description("supports works with URL sources")
    def test_supports_url_source(self) -> None:
        adapter = PdfAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.DOCUMENT,
            url="https://example.com/document.pdf",
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns True for PDF MIME type")
    def test_supports_mime_type(self) -> None:
        adapter = PdfAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.DOCUMENT,
            url="https://example.com/download",
            metadata={"mime_type": "application/pdf"},
        )
        assert adapter.supports(source) is True

    @pytest.mark.description("supports returns False for non-PDF MIME type")
    def test_rejects_wrong_mime_type(self) -> None:
        adapter = PdfAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.DOCUMENT,
            url="https://example.com/download",
            metadata={"mime_type": "application/msword"},
        )
        assert adapter.supports(source) is False


class TestPdfAdapterExtract:
    """Tests for PdfAdapter.extract method."""

    @pytest.mark.description("extract raises ValueError for unsupported source")
    @pytest.mark.asyncio
    async def test_extract_unsupported_raises(self) -> None:
        adapter = PdfAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.AUDIO,
            path=Path("/data/audio.mp3"),
        )
        with pytest.raises(ValueError, match="Unsupported source"):
            async for _ in adapter.extract(source):
                pass

    @pytest.mark.description("extract raises ValueError for URL-only source")
    @pytest.mark.asyncio
    async def test_extract_url_only_raises(self) -> None:
        adapter = PdfAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.DOCUMENT,
            url="https://example.com/document.pdf",
        )
        with pytest.raises(ValueError, match="requires a local file path"):
            async for _ in adapter.extract(source):
                pass

    @pytest.mark.description("extract raises ValueError for missing file")
    @pytest.mark.asyncio
    async def test_extract_missing_file_raises(self) -> None:
        adapter = PdfAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.DOCUMENT,
            path=Path("/nonexistent/document.pdf"),
        )
        with pytest.raises(ValueError, match="PDF file not found"):
            async for _ in adapter.extract(source):
                pass

    @pytest.mark.description("extract yields RawChunks with page locations")
    @pytest.mark.asyncio
    async def test_extract_yields_chunks(self, tmp_path: Path) -> None:
        # Create a mock PDF file
        pdf_file = tmp_path / "test.pdf"
        pdf_file.touch()

        # Create mock text block
        mock_block = {
            "type": 0,  # Text block
            "bbox": (50, 100, 450, 150),  # x0, y0, x1, y1
            "lines": [
                {
                    "spans": [
                        {
                            "text": "Hello world from PDF",
                            "size": 12.0,
                            "font": "Helvetica",
                        }
                    ]
                }
            ],
        }

        # Create mock page
        mock_page = MagicMock()
        mock_page.rect.width = 500
        mock_page.rect.height = 700
        mock_page.get_text.return_value = {"blocks": [mock_block]}
        mock_page.find_tables.return_value = []

        # Create mock document
        mock_doc = MagicMock()
        mock_doc.__len__ = MagicMock(return_value=1)
        mock_doc.__iter__ = MagicMock(return_value=iter([mock_page]))
        mock_doc.__getitem__ = MagicMock(return_value=mock_page)

        # Create mock fitz module
        mock_fitz = MagicMock()
        mock_fitz.open.return_value = mock_doc
        mock_fitz.TEXT_PRESERVE_WHITESPACE = 1

        adapter = PdfAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.DOCUMENT,
            path=pdf_file,
        )

        with patch("voogle.adapters.pdf._get_fitz", return_value=mock_fitz):
            chunks = []
            async for chunk in adapter.extract(source):
                chunks.append(chunk)

        assert len(chunks) == 1
        assert chunks[0].text == "Hello world from PDF"
        assert isinstance(chunks[0].location, PageBboxLocation)
        assert chunks[0].location.page == 1
        assert chunks[0].metadata["block_type"] == "text"

    @pytest.mark.description("extract detects headings based on font size")
    @pytest.mark.asyncio
    async def test_extract_detects_headings(self, tmp_path: Path) -> None:
        pdf_file = tmp_path / "test.pdf"
        pdf_file.touch()

        # Create blocks with different font sizes
        heading_block = {
            "type": 0,
            "bbox": (50, 50, 450, 100),
            "lines": [
                {
                    "spans": [
                        {
                            "text": "Chapter Title",
                            "size": 24.0,  # Large font = heading
                            "font": "Helvetica-Bold",
                        }
                    ]
                }
            ],
        }
        body_block = {
            "type": 0,
            "bbox": (50, 120, 450, 200),
            "lines": [
                {
                    "spans": [
                        {
                            "text": "Body text content",
                            "size": 12.0,  # Normal font
                            "font": "Helvetica",
                        }
                    ]
                }
            ],
        }

        mock_page = MagicMock()
        mock_page.rect.width = 500
        mock_page.rect.height = 700
        mock_page.get_text.return_value = {"blocks": [heading_block, body_block]}
        mock_page.find_tables.return_value = []

        mock_doc = MagicMock()
        mock_doc.__len__ = MagicMock(return_value=1)
        mock_doc.__iter__ = MagicMock(return_value=iter([mock_page]))
        mock_doc.__getitem__ = MagicMock(return_value=mock_page)

        mock_fitz = MagicMock()
        mock_fitz.open.return_value = mock_doc
        mock_fitz.TEXT_PRESERVE_WHITESPACE = 1

        adapter = PdfAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.DOCUMENT,
            path=pdf_file,
        )

        with patch("voogle.adapters.pdf._get_fitz", return_value=mock_fitz):
            chunks = []
            async for chunk in adapter.extract(source):
                chunks.append(chunk)

        # First chunk should be detected as heading
        assert len(chunks) == 2
        assert chunks[0].metadata.get("is_heading") is True
        assert "heading_level" in chunks[0].metadata


class TestPdfAdapterChunk:
    """Tests for PdfAdapter.chunk method."""

    @pytest.mark.description("chunk returns empty list for empty input")
    def test_chunk_empty_input(self) -> None:
        adapter = PdfAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.DOCUMENT,
            path=Path("/data/document.pdf"),
        )
        result = adapter.chunk([], source)
        assert result == []

    @pytest.mark.description("chunk combines words into target-sized chunks")
    def test_chunk_combines_words(self) -> None:
        adapter = PdfAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.DOCUMENT,
            path=Path("/data/document.pdf"),
        )

        # Create raw chunks with more than target words
        words = "one two three four five six seven eight nine ten " * 5  # 50 words
        raw_chunks = [
            RawChunk(
                text=words,
                location=PageBboxLocation(page=1, x=10, y=20, width=80, height=10),
            )
        ]

        config = ChunkConfig(target_words=40, overlap_words=5)
        result = adapter.chunk(raw_chunks, source, config)

        assert len(result) >= 1
        assert all(chunk.source_id == "test" for chunk in result)
        assert all(chunk.source_type == ContentType.DOCUMENT for chunk in result)

    @pytest.mark.description("chunk preserves page locations from raw chunks")
    def test_chunk_preserves_locations(self) -> None:
        adapter = PdfAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.DOCUMENT,
            path=Path("/data/document.pdf"),
        )

        raw_chunks = [
            RawChunk(
                text="word " * 45,
                location=PageBboxLocation(page=5, x=10, y=20, width=80, height=10),
            )
        ]

        config = ChunkConfig(target_words=40, overlap_words=5)
        result = adapter.chunk(raw_chunks, source, config)

        assert len(result) >= 1
        assert result[0].location is not None
        assert isinstance(result[0].location, PageBboxLocation)
        assert result[0].location.page == 5

    @pytest.mark.description("chunk increments sequence_index correctly")
    def test_chunk_sequence_index(self) -> None:
        adapter = PdfAdapter()
        source = ContentSource(
            source_id="test",
            source_type=ContentType.DOCUMENT,
            path=Path("/data/document.pdf"),
        )

        # Create enough words for multiple chunks
        raw_chunks = [
            RawChunk(
                text="word " * 100,
                location=PageBboxLocation(page=1),
            )
        ]

        config = ChunkConfig(target_words=40, overlap_words=5)
        result = adapter.chunk(raw_chunks, source, config)

        assert len(result) >= 2
        for i, chunk in enumerate(result):
            assert chunk.sequence_index == i


class TestPdfAdapterGetLocation:
    """Tests for PdfAdapter.get_location method."""

    @pytest.mark.description("get_location returns chunk location")
    def test_get_location_returns_location(self) -> None:
        from voogle.adapters.base import TextChunk

        adapter = PdfAdapter()
        location = PageBboxLocation(page=3, x=10, y=20, width=80, height=10)
        chunk = TextChunk(
            text="test",
            source_id="test",
            source_type=ContentType.DOCUMENT,
            location=location,
        )

        result = adapter.get_location(chunk)
        assert result == location

    @pytest.mark.description("get_location returns None when no location")
    def test_get_location_returns_none(self) -> None:
        from voogle.adapters.base import TextChunk

        adapter = PdfAdapter()
        chunk = TextChunk(
            text="test",
            source_id="test",
            source_type=ContentType.DOCUMENT,
        )

        result = adapter.get_location(chunk)
        assert result is None


class TestPdfAdapterGetDeepLink:
    """Tests for PdfAdapter.get_deep_link method."""

    @pytest.mark.description("get_deep_link generates page URL")
    def test_get_deep_link_with_page(self) -> None:
        from voogle.adapters.base import TextChunk

        adapter = PdfAdapter()
        location = PageBboxLocation(page=5)
        chunk = TextChunk(
            text="test",
            source_id="test",
            source_type=ContentType.DOCUMENT,
            location=location,
        )

        result = adapter.get_deep_link(chunk, "https://example.com/doc.pdf")
        assert result is not None
        assert "page=5" in result

    @pytest.mark.description("get_deep_link returns None without location")
    def test_get_deep_link_without_location(self) -> None:
        from voogle.adapters.base import TextChunk

        adapter = PdfAdapter()
        chunk = TextChunk(
            text="test",
            source_id="test",
            source_type=ContentType.DOCUMENT,
        )

        result = adapter.get_deep_link(chunk, "https://example.com/doc.pdf")
        assert result is None


class TestPdfConfig:
    """Tests for PdfConfig dataclass."""

    @pytest.mark.description("PdfConfig has correct defaults")
    def test_default_values(self) -> None:
        config = PdfConfig()
        assert config.extract_images is False
        assert config.detect_tables is True
        assert config.detect_headings is True
        assert config.min_heading_size == 1.2
        assert config.ocr_language == "eng"

    @pytest.mark.description("PdfConfig accepts custom values")
    def test_custom_values(self) -> None:
        config = PdfConfig(
            extract_images=True,
            detect_tables=False,
            detect_headings=False,
            min_heading_size=1.8,
            ocr_language="fra",
        )
        assert config.extract_images is True
        assert config.detect_tables is False
        assert config.detect_headings is False
        assert config.min_heading_size == 1.8
        assert config.ocr_language == "fra"


class TestPdfExtensions:
    """Tests for PDF_EXTENSIONS constant."""

    @pytest.mark.description("PDF_EXTENSIONS contains .pdf")
    def test_contains_pdf(self) -> None:
        assert ".pdf" in PDF_EXTENSIONS

    @pytest.mark.description("PDF_EXTENSIONS is frozen")
    def test_is_frozen(self) -> None:
        assert isinstance(PDF_EXTENSIONS, frozenset)
