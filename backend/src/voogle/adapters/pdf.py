# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""PDF content adapter for extracting text using PyMuPDF.

This module provides a PdfAdapter that implements the ContentAdapter interface
for PDF documents. It uses PyMuPDF (fitz) for text extraction with block-level
coordinates, table detection, and heading hierarchy extraction.
"""
import logging
import re
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any

from voogle.adapters.base import (
    ChunkConfig,
    ContentAdapter,
    ContentSource,
    RawChunk,
    TextChunk,
)
from voogle.core.fragment import ContentType
from voogle.core.location import Location, PageBboxLocation

logger = logging.getLogger(__name__)


# Supported PDF file extensions
PDF_EXTENSIONS: frozenset[str] = frozenset({".pdf"})


@dataclass
class PdfConfig:
    """Configuration for PDF extraction.

    Attributes:
        extract_images: Whether to attempt OCR on embedded images.
        detect_tables: Whether to detect and extract table structures.
        detect_headings: Whether to detect heading hierarchy from font sizes.
        min_heading_size: Minimum font size ratio to consider as heading.
        ocr_language: Language for OCR if extract_images is enabled.
    """

    extract_images: bool = False
    detect_tables: bool = True
    detect_headings: bool = True
    min_heading_size: float = 1.2  # 20% larger than body text
    ocr_language: str = "eng"


def _get_fitz() -> Any:
    """Lazy import of PyMuPDF (fitz) module.

    Returns:
        The fitz module from PyMuPDF.

    Raises:
        ImportError: If PyMuPDF is not installed.
    """
    try:
        import fitz
        return fitz
    except ImportError as e:
        raise ImportError(
            "PyMuPDF is required for PDF processing. "
            "Install with: pip install 'voogle[pdf]' or pip install pymupdf"
        ) from e


class PdfAdapter(ContentAdapter):
    """Content adapter for PDF documents using PyMuPDF.

    Extracts text with block-level coordinates, supports table detection,
    heading hierarchy extraction, and optional image OCR.

    Example:
        >>> adapter = PdfAdapter()
        >>> source = ContentSource(
        ...     source_id="doc-123",
        ...     source_type=ContentType.DOCUMENT,
        ...     path=Path("/data/document.pdf"),
        ... )
        >>> async for chunk in adapter.extract(source):
        ...     print(chunk.text, chunk.location)
    """

    def __init__(self, config: PdfConfig | None = None) -> None:
        """Initialize the PDF adapter.

        Args:
            config: PDF extraction configuration. Uses defaults if not provided.
        """
        self._config = config or PdfConfig()

    @property
    def supported_types(self) -> frozenset[ContentType]:
        """Return the content types this adapter can process.

        Returns:
            Frozen set containing ContentType.DOCUMENT.
        """
        return frozenset({ContentType.DOCUMENT})

    def supports(self, source: ContentSource) -> bool:
        """Check if this adapter can process the given source.

        Args:
            source: The content source to check.

        Returns:
            True if the source is a PDF document.
        """
        if source.source_type != ContentType.DOCUMENT:
            return False

        # Check file extension if path is available
        if source.path is not None:
            suffix = source.path.suffix.lower()
            return suffix in PDF_EXTENSIONS

        # Check URL extension or MIME type
        if source.url is not None:
            # Try to extract extension from URL path
            from urllib.parse import urlparse

            parsed = urlparse(source.url)
            url_path = parsed.path
            if "." in url_path:
                suffix = "." + url_path.rsplit(".", 1)[-1].lower()
                if suffix in PDF_EXTENSIONS:
                    return True

            # Check MIME type in metadata as fallback
            mime_type = source.metadata.get("mime_type", "")
            return mime_type == "application/pdf"

        return False

    async def extract(self, source: ContentSource) -> AsyncIterator[RawChunk]:
        """Extract text chunks from a PDF document.

        Extracts text blocks with their page numbers and bounding boxes.
        Optionally detects tables and heading hierarchy.

        Args:
            source: The PDF source to extract from.

        Yields:
            RawChunk instances with extracted text and PageBboxLocation.

        Raises:
            ValueError: If the source is not supported or file not found.
        """
        if not self.supports(source):
            raise ValueError(f"Unsupported source: {source.source_id}")

        if source.path is None:
            raise ValueError(
                f"PDF source {source.source_id} requires a local file path"
            )

        if not source.path.exists():
            raise ValueError(f"PDF file not found: {source.path}")

        logger.info("Starting PDF extraction of %s", source.path)

        fitz = _get_fitz()
        doc = fitz.open(str(source.path))

        try:
            # First pass: calculate average body text font size if heading detection enabled
            avg_font_size = None
            if self._config.detect_headings:
                avg_font_size = self._calculate_avg_font_size(doc)

            # Extract text from each page
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_width = page.rect.width
                page_height = page.rect.height

                # Get text blocks with positions
                blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]

                for block in blocks:
                    # Skip image blocks unless OCR is enabled
                    if block.get("type") == 1:  # Image block
                        if self._config.extract_images:
                            async for chunk in self._extract_image_text(
                                page, block, page_num, page_width, page_height
                            ):
                                yield chunk
                        continue

                    # Process text block
                    async for chunk in self._extract_text_block(
                        block, page_num, page_width, page_height, avg_font_size
                    ):
                        yield chunk

                # Detect tables if enabled
                if self._config.detect_tables:
                    async for chunk in self._extract_tables(
                        page, page_num, page_width, page_height
                    ):
                        yield chunk

        finally:
            doc.close()

        logger.info("Completed PDF extraction of %s", source.path)

    def _calculate_avg_font_size(self, doc: Any) -> float:
        """Calculate the average font size across the document.

        Args:
            doc: PyMuPDF document object.

        Returns:
            Average font size of text in the document.
        """
        total_size = 0.0
        count = 0

        for page in doc:
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if block.get("type") == 0:  # Text block
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            size = span.get("size", 0)
                            if size > 0:
                                total_size += size
                                count += 1

        return total_size / count if count > 0 else 12.0  # Default to 12pt

    async def _extract_text_block(
        self,
        block: dict[str, Any],
        page_num: int,
        page_width: float,
        page_height: float,
        avg_font_size: float | None,
    ) -> AsyncIterator[RawChunk]:
        """Extract text from a single text block.

        Args:
            block: PyMuPDF text block dictionary.
            page_num: Zero-indexed page number.
            page_width: Page width in points.
            page_height: Page height in points.
            avg_font_size: Average font size for heading detection.

        Yields:
            RawChunk instances for the text block.
        """
        # Collect all text and metadata from the block
        text_parts: list[str] = []
        font_sizes: list[float] = []
        is_bold = False
        font_name = ""

        for line in block.get("lines", []):
            line_text_parts: list[str] = []
            for span in line.get("spans", []):
                span_text = span.get("text", "").strip()
                if span_text:
                    line_text_parts.append(span_text)
                    font_sizes.append(span.get("size", 0))
                    # Check for bold font
                    font = span.get("font", "")
                    if font:
                        font_name = font
                        if "bold" in font.lower() or "heavy" in font.lower():
                            is_bold = True

            if line_text_parts:
                text_parts.append(" ".join(line_text_parts))

        if not text_parts:
            return

        text = " ".join(text_parts)
        text = self._normalize_text(text)

        if not text:
            return

        # Calculate bounding box as percentage of page
        bbox = block.get("bbox", (0, 0, page_width, page_height))
        x = (bbox[0] / page_width) * 100
        y = (bbox[1] / page_height) * 100
        width = ((bbox[2] - bbox[0]) / page_width) * 100
        height = ((bbox[3] - bbox[1]) / page_height) * 100

        # Clamp values to valid range
        x = max(0, min(100, x))
        y = max(0, min(100, y))
        width = max(0, min(100 - x, width))
        height = max(0, min(100 - y, height))

        location = PageBboxLocation(
            page=page_num + 1,  # Convert to 1-indexed
            x=x,
            y=y,
            width=width,
            height=height,
        )

        # Build metadata
        metadata: dict[str, Any] = {
            "block_type": "text",
            "font_name": font_name,
        }

        # Detect heading level
        if avg_font_size and font_sizes:
            max_font_size = max(font_sizes)
            if max_font_size >= avg_font_size * self._config.min_heading_size:
                heading_level = self._determine_heading_level(
                    max_font_size, avg_font_size, is_bold
                )
                metadata["heading_level"] = heading_level
                metadata["is_heading"] = True

        yield RawChunk(
            text=text,
            location=location,
            metadata=metadata,
        )

    def _determine_heading_level(
        self,
        font_size: float,
        avg_font_size: float,
        is_bold: bool,
    ) -> int:
        """Determine heading level based on font size ratio.

        Args:
            font_size: Font size of the text.
            avg_font_size: Average body text font size.
            is_bold: Whether the text is bold.

        Returns:
            Heading level (1-6), where 1 is the largest.
        """
        ratio = font_size / avg_font_size

        # Map font size ratios to heading levels
        if ratio >= 2.0:
            return 1
        elif ratio >= 1.7:
            return 2
        elif ratio >= 1.5:
            return 3
        elif ratio >= 1.3:
            return 4
        elif ratio >= 1.2:
            return 5 if not is_bold else 4
        else:
            return 6

    async def _extract_tables(
        self,
        page: Any,
        page_num: int,
        page_width: float,
        page_height: float,
    ) -> AsyncIterator[RawChunk]:
        """Extract tables from a page using PyMuPDF's table detection.

        Args:
            page: PyMuPDF page object.
            page_num: Zero-indexed page number.
            page_width: Page width in points.
            page_height: Page height in points.

        Yields:
            RawChunk instances for detected tables.
        """
        try:
            tables = page.find_tables()
        except AttributeError:
            # find_tables may not be available in older PyMuPDF versions
            logger.debug("Table detection not available for page %d", page_num + 1)
            return

        for table in tables:
            # Extract table content as text
            try:
                df = table.to_pandas()
                # Convert DataFrame to readable text format
                rows = []
                for _, row in df.iterrows():
                    row_text = " | ".join(str(cell) for cell in row if cell)
                    if row_text.strip():
                        rows.append(row_text)

                if not rows:
                    continue

                text = " || ".join(rows)
                text = self._normalize_text(text)

                if not text:
                    continue

                # Get table bounding box
                bbox = table.bbox
                x = (bbox[0] / page_width) * 100
                y = (bbox[1] / page_height) * 100
                width = ((bbox[2] - bbox[0]) / page_width) * 100
                height = ((bbox[3] - bbox[1]) / page_height) * 100

                # Clamp values
                x = max(0, min(100, x))
                y = max(0, min(100, y))
                width = max(0, min(100 - x, width))
                height = max(0, min(100 - y, height))

                location = PageBboxLocation(
                    page=page_num + 1,
                    x=x,
                    y=y,
                    width=width,
                    height=height,
                )

                yield RawChunk(
                    text=text,
                    location=location,
                    metadata={
                        "block_type": "table",
                        "rows": len(rows),
                        "columns": len(df.columns) if hasattr(df, 'columns') else 0,
                    },
                )

            except Exception as e:
                logger.warning("Failed to extract table on page %d: %s", page_num + 1, e)
                continue

    async def _extract_image_text(
        self,
        _page: Any,
        _block: dict[str, Any],
        page_num: int,
        _page_width: float,
        _page_height: float,
    ) -> AsyncIterator[RawChunk]:
        """Extract text from an image block using OCR.

        Args:
            _page: PyMuPDF page object (unused - reserved for future OCR).
            _block: Image block dictionary (unused - reserved for future OCR).
            page_num: Zero-indexed page number.
            _page_width: Page width in points (unused - reserved for future OCR).
            _page_height: Page height in points (unused - reserved for future OCR).

        Yields:
            RawChunk instances for OCR'd text from images.
        """
        # OCR implementation would require additional dependencies (tesseract/pytesseract)
        # For now, this is a placeholder that can be extended
        logger.debug(
            "Image OCR not implemented - skipping image on page %d",
            page_num + 1,
        )
        # This yield is here to make this an async generator
        if False:  # pragma: no cover
            yield RawChunk(text="")

    def _normalize_text(self, text: str) -> str:
        """Normalize extracted text.

        Args:
            text: Raw extracted text.

        Returns:
            Normalized text with cleaned whitespace.
        """
        # Replace multiple whitespace with single space
        text = re.sub(r"\s+", " ", text)
        # Strip leading/trailing whitespace
        text = text.strip()
        return text

    def chunk(
        self,
        raw_chunks: list[RawChunk],
        source: ContentSource,
        config: ChunkConfig | None = None,
    ) -> list[TextChunk]:
        """Process raw PDF chunks into text chunks for embedding.

        Combines adjacent text blocks into chunks of approximately
        target_words words, preserving page location information.

        Args:
            raw_chunks: List of RawChunk instances from extraction.
            source: The source these chunks came from.
            config: Chunking configuration. Uses defaults if not provided.

        Returns:
            List of TextChunk instances ready for embedding.
        """
        if not raw_chunks:
            return []

        cfg = config or ChunkConfig()
        text_chunks: list[TextChunk] = []

        # Accumulate content into chunks
        current_words: list[str] = []
        current_location: PageBboxLocation | None = None
        current_metadata: dict[str, Any] = {}
        sequence_index = 0

        for raw_chunk in raw_chunks:
            words = raw_chunk.text.split()

            # Update location (use first block's location for the chunk)
            if current_location is None and isinstance(raw_chunk.location, PageBboxLocation):
                current_location = raw_chunk.location
                current_metadata = dict(raw_chunk.metadata)

            current_words.extend(words)

            # Check if we've reached the target word count
            if len(current_words) >= cfg.target_words:
                text = " ".join(current_words)
                text_chunks.append(
                    TextChunk(
                        text=text,
                        source_id=source.source_id,
                        source_type=source.source_type,
                        location=current_location,
                        sequence_index=sequence_index,
                        metadata=current_metadata,
                    )
                )
                sequence_index += 1

                # Handle overlap
                if cfg.overlap_words > 0 and len(current_words) > cfg.overlap_words:
                    current_words = current_words[-cfg.overlap_words:]
                    # Keep the last location for context
                else:
                    current_words = []
                    current_location = None
                    current_metadata = {}

        # Don't forget the final chunk
        if current_words:
            text = " ".join(current_words)
            text_chunks.append(
                TextChunk(
                    text=text,
                    source_id=source.source_id,
                    source_type=source.source_type,
                    location=current_location,
                    sequence_index=sequence_index,
                    metadata=current_metadata,
                )
            )

        return text_chunks

    def get_location(self, chunk: TextChunk) -> Location | None:
        """Get the location for a text chunk.

        Args:
            chunk: The text chunk to get location for.

        Returns:
            PageBboxLocation for the chunk, or None if not available.
        """
        return chunk.location

    def get_deep_link(self, chunk: TextChunk, base_url: str) -> str | None:
        """Generate a deep link URL for a text chunk.

        Creates a URL with PDF page fragment to navigate directly to
        the page in a PDF viewer.

        Args:
            chunk: The text chunk to generate a link for.
            base_url: The base URL of the PDF document.

        Returns:
            URL with page parameter (e.g., #page=5), or None if
            no page location is available.
        """
        location = self.get_location(chunk)
        if location is None:
            return None
        return location.to_deep_link(base_url)
