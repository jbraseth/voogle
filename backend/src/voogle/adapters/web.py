# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Web content adapter for extracting and chunking HTML content.

This module provides a WebAdapter that implements the ContentAdapter interface
for web pages. It uses BeautifulSoup for HTML parsing, includes boilerplate
removal, CSS selector generation for ElementSelectorLocation, and text fragment
URL support (#:~:text=).
"""
import logging
import re
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

from voogle.adapters.base import (
    ChunkConfig,
    ContentAdapter,
    ContentSource,
    RawChunk,
    TextChunk,
)
from voogle.core.fragment import ContentType
from voogle.core.location import ElementSelectorLocation, Location

logger = logging.getLogger(__name__)


# Tags that typically contain boilerplate content
BOILERPLATE_TAGS: frozenset[str] = frozenset({
    "script", "style", "nav", "header", "footer", "aside",
    "noscript", "iframe", "form", "button", "input", "select",
    "textarea", "meta", "link", "comment",
})

# Tags that typically contain main content
CONTENT_TAGS: frozenset[str] = frozenset({
    "article", "main", "section", "div", "p", "h1", "h2", "h3",
    "h4", "h5", "h6", "blockquote", "pre", "code", "li", "td", "th",
    "figcaption", "caption",
})

# Block-level elements that should introduce text breaks
BLOCK_ELEMENTS: frozenset[str] = frozenset({
    "p", "div", "article", "section", "main", "aside", "header", "footer",
    "nav", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "pre", "ul",
    "ol", "li", "table", "tr", "td", "th", "form", "fieldset", "address",
    "figure", "figcaption", "br", "hr",
})


@dataclass
class WebConfig:
    """Configuration for web content extraction.

    Attributes:
        remove_boilerplate: Remove navigation, footer, and other boilerplate.
        use_playwright: Use Playwright for JavaScript-rendered content.
        timeout: Timeout for fetching/rendering in seconds.
        user_agent: User agent string for requests.
        extract_links: Whether to extract and preserve links.
        min_text_length: Minimum text length for a block to be included.
    """

    remove_boilerplate: bool = True
    use_playwright: bool = False
    timeout: float = 30.0
    user_agent: str = "Mozilla/5.0 (compatible; VoogleBot/1.0)"
    extract_links: bool = True
    min_text_length: int = 20


class WebAdapter(ContentAdapter):
    """Content adapter for web pages using BeautifulSoup.

    Supports HTML content extraction with boilerplate removal, CSS selector
    generation for deep linking, and text fragment URLs.

    Example:
        >>> adapter = WebAdapter()
        >>> source = ContentSource(
        ...     source_id="page-123",
        ...     source_type=ContentType.TEXT,
        ...     url="https://example.com/article",
        ... )
        >>> async for chunk in adapter.extract(source):
        ...     print(chunk.text, chunk.location)
    """

    def __init__(self, config: WebConfig | None = None) -> None:
        """Initialize the web adapter.

        Args:
            config: Web extraction configuration. Uses defaults if not provided.
        """
        self._config = config or WebConfig()
        self._bs4_available: bool | None = None
        self._playwright_available: bool | None = None

    @property
    def supported_types(self) -> frozenset[ContentType]:
        """Return the content types this adapter can process.

        Returns:
            Frozen set containing ContentType.TEXT.
        """
        return frozenset({ContentType.TEXT})

    def supports(self, source: ContentSource) -> bool:
        """Check if this adapter can process the given source.

        Args:
            source: The content source to check.

        Returns:
            True if the source is HTML/web content.
        """
        if source.source_type != ContentType.TEXT:
            return False

        # Check if it's HTML content via MIME type
        mime_type = source.metadata.get("mime_type", "")
        if mime_type in ("text/html", "application/xhtml+xml"):
            return True

        # Check file extension for local files
        if source.path is not None:
            suffix = source.path.suffix.lower()
            return suffix in (".html", ".htm", ".xhtml")

        # Check URL for web content
        if source.url is not None:
            parsed = urlparse(source.url)
            # Accept HTTP/HTTPS URLs
            if parsed.scheme in ("http", "https"):
                path = parsed.path.lower()
                # Check if path explicitly ends with HTML extension
                if path.endswith((".html", ".htm", ".xhtml")):
                    return True
                # Reject known non-HTML extensions
                non_html_extensions = (
                    ".json", ".xml", ".txt", ".pdf", ".jpg", ".jpeg", ".png",
                    ".gif", ".svg", ".css", ".js", ".mp3", ".mp4", ".wav",
                    ".zip", ".tar", ".gz", ".doc", ".docx", ".xls", ".xlsx",
                )
                if any(path.endswith(ext) for ext in non_html_extensions):
                    return False
                # Accept URLs without known non-HTML extension (common for web pages)
                return True

        return False

    def _ensure_bs4(self) -> None:
        """Ensure BeautifulSoup is available."""
        if self._bs4_available is None:
            try:
                from bs4 import BeautifulSoup  # noqa: F401
                self._bs4_available = True
            except ImportError:
                self._bs4_available = False

        if not self._bs4_available:
            raise ImportError(
                "BeautifulSoup4 is required for web content extraction. "
                "Install it with: pip install beautifulsoup4 lxml"
            )

    async def _fetch_content(self, source: ContentSource) -> str:
        """Fetch HTML content from source.

        Args:
            source: The content source to fetch.

        Returns:
            HTML content as string.

        Raises:
            ValueError: If content cannot be fetched.
        """
        if source.path is not None:
            if not source.path.exists():
                raise ValueError(f"HTML file not found: {source.path}")
            return source.path.read_text(encoding="utf-8")

        if source.url is not None:
            if self._config.use_playwright:
                return await self._fetch_with_playwright(source.url)
            return await self._fetch_with_httpx(source.url)

        raise ValueError(f"No path or URL provided for source: {source.source_id}")

    async def _fetch_with_httpx(self, url: str) -> str:
        """Fetch content using httpx.

        Args:
            url: URL to fetch.

        Returns:
            HTML content.
        """
        import httpx

        async with httpx.AsyncClient(
            timeout=self._config.timeout,
            follow_redirects=True,
        ) as client:
            headers = {"User-Agent": self._config.user_agent}
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.text

    async def _fetch_with_playwright(self, url: str) -> str:
        """Fetch JavaScript-rendered content using Playwright.

        Args:
            url: URL to fetch.

        Returns:
            Rendered HTML content.
        """
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            raise ImportError(
                "Playwright is required for JavaScript rendering. "
                "Install it with: pip install playwright && playwright install"
            )

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            try:
                page = await browser.new_page(user_agent=self._config.user_agent)
                await page.goto(url, timeout=int(self._config.timeout * 1000))
                # Wait for content to load
                await page.wait_for_load_state("networkidle")
                return await page.content()
            finally:
                await browser.close()

    def _parse_html(self, html: str) -> Any:
        """Parse HTML content with BeautifulSoup.

        Args:
            html: HTML string to parse.

        Returns:
            BeautifulSoup object.
        """
        self._ensure_bs4()
        from bs4 import BeautifulSoup

        # Try lxml parser first, fall back to html.parser
        try:
            return BeautifulSoup(html, "lxml")
        except Exception:
            return BeautifulSoup(html, "html.parser")

    def _remove_boilerplate(self, soup: Any) -> None:
        """Remove boilerplate elements from the soup in-place.

        Args:
            soup: BeautifulSoup object to modify.
        """
        # Remove known boilerplate tags
        for tag in BOILERPLATE_TAGS:
            for element in soup.find_all(tag):
                element.decompose()

        # Remove elements with common boilerplate class/id patterns
        boilerplate_patterns = [
            r"nav", r"menu", r"sidebar", r"footer", r"header",
            r"banner", r"cookie", r"popup", r"modal", r"advertisement",
            r"social", r"share", r"comment", r"related",
        ]
        pattern = re.compile("|".join(boilerplate_patterns), re.IGNORECASE)

        for element in soup.find_all(True):
            class_str = " ".join(element.get("class", []))
            id_str = element.get("id", "")
            if pattern.search(class_str) or pattern.search(id_str):
                element.decompose()

    def _generate_css_selector(self, element: Any) -> str:
        """Generate a unique CSS selector for an element.

        Args:
            element: BeautifulSoup element.

        Returns:
            CSS selector string.
        """
        # Try ID first (most specific)
        if element.get("id"):
            return f"#{element['id']}"

        # Build selector path
        parts: list[str] = []
        current = element

        while current and current.name and current.name != "[document]":
            selector = current.name

            # Add class if unique among siblings
            classes = current.get("class", [])
            if classes:
                selector += "." + ".".join(classes)

            # Add nth-child if needed for uniqueness
            parent = current.parent
            if parent:
                siblings = [s for s in parent.children if hasattr(s, "name") and s.name == current.name]
                if len(siblings) > 1:
                    index = siblings.index(current) + 1
                    selector += f":nth-child({index})"

            parts.append(selector)
            current = current.parent

            # Stop at body or when we have enough specificity
            if current and current.name in ("body", "html"):
                break

        parts.reverse()
        return " > ".join(parts) if parts else "body"

    def _extract_text_blocks(
        self,
        soup: Any,
        base_url: str | None = None,
    ) -> list[tuple[str, str, str | None]]:
        """Extract text blocks with their CSS selectors.

        Args:
            soup: BeautifulSoup object.
            base_url: Optional base URL for resolving relative links.

        Returns:
            List of (text, css_selector, element_id) tuples.
        """
        blocks: list[tuple[str, str, str | None]] = []

        # Find main content containers
        main_content = soup.find("main") or soup.find("article") or soup.find("body")
        if not main_content:
            return blocks

        # Extract text from content elements
        for element in main_content.find_all(CONTENT_TAGS):
            # Skip if element has no direct text
            text = element.get_text(separator=" ", strip=True)
            if len(text) < self._config.min_text_length:
                continue

            # Skip if text is mostly from child block elements
            direct_text_parts: list[str] = []
            for child in element.children:
                if isinstance(child, str):
                    direct_text_parts.append(child)
                elif hasattr(child, "name") and child.name not in BLOCK_ELEMENTS:
                    child_str = getattr(child, "string", None)
                    if child_str:
                        direct_text_parts.append(str(child_str))
            direct_text = "".join(direct_text_parts).strip()

            if len(direct_text) >= self._config.min_text_length:
                selector = self._generate_css_selector(element)
                element_id = element.get("id")
                blocks.append((direct_text, selector, element_id))

        return blocks

    async def extract(self, source: ContentSource) -> AsyncIterator[RawChunk]:
        """Extract content chunks from a web page.

        Parses HTML, removes boilerplate, and yields RawChunk instances
        with text and ElementSelectorLocation for deep linking.

        Args:
            source: The web source to extract from.

        Yields:
            RawChunk instances with extracted text and locations.

        Raises:
            ValueError: If the source is not supported or cannot be fetched.
        """
        if not self.supports(source):
            raise ValueError(f"Unsupported source: {source.source_id}")

        logger.info("Starting extraction of %s", source.url or source.path)

        # Fetch HTML content
        html = await self._fetch_content(source)

        # Parse HTML
        soup = self._parse_html(html)

        # Remove boilerplate if configured
        if self._config.remove_boilerplate:
            self._remove_boilerplate(soup)

        # Extract title for metadata
        title = ""
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text(strip=True)

        # Extract text blocks with selectors
        base_url = source.url
        blocks = self._extract_text_blocks(soup, base_url)

        for text, selector, element_id in blocks:
            # Create location with CSS selector and text for fragment
            # Use first ~50 chars for text match (text fragment spec)
            text_match = text[:50] if len(text) > 50 else text
            location = ElementSelectorLocation(
                selector=selector,
                selector_type="css",
                text_match=text_match,
            )

            metadata: dict[str, Any] = {}
            if title:
                metadata["title"] = title
            if element_id:
                metadata["element_id"] = element_id
            if base_url:
                metadata["url"] = base_url

            yield RawChunk(
                text=text,
                location=location,
                metadata=metadata,
            )

        logger.info("Completed extraction of %s", source.url or source.path)

    def chunk(
        self,
        raw_chunks: list[RawChunk],
        source: ContentSource,
        config: ChunkConfig | None = None,
    ) -> list[TextChunk]:
        """Process raw web chunks into text chunks for embedding.

        Combines adjacent text blocks into chunks of approximately
        target_words words, preserving location information for deep linking.

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

        current_words: list[str] = []
        current_location: ElementSelectorLocation | None = None
        current_metadata: dict[str, Any] = {}
        sequence_index = 0

        for raw_chunk in raw_chunks:
            words = raw_chunk.text.split()

            # Store first location for the chunk
            if current_location is None and isinstance(raw_chunk.location, ElementSelectorLocation):
                current_location = raw_chunk.location
                current_metadata = dict(raw_chunk.metadata)

            current_words.extend(words)

            # Check if we've reached the target word count
            if len(current_words) >= cfg.target_words:
                text = " ".join(current_words)

                # Update text_match to reflect actual chunk content
                location = None
                if current_location:
                    text_match = text[:50] if len(text) > 50 else text
                    location = ElementSelectorLocation(
                        selector=current_location.selector,
                        selector_type=current_location.selector_type,
                        text_match=text_match,
                    )

                text_chunks.append(
                    TextChunk(
                        text=text,
                        source_id=source.source_id,
                        source_type=source.source_type,
                        location=location,
                        sequence_index=sequence_index,
                        metadata=current_metadata,
                    )
                )
                sequence_index += 1

                # Handle overlap
                if cfg.overlap_words > 0 and len(current_words) > cfg.overlap_words:
                    current_words = current_words[-cfg.overlap_words:]
                else:
                    current_words = []
                    current_location = None
                    current_metadata = {}

        # Don't forget the final chunk
        if current_words:
            text = " ".join(current_words)

            location = None
            if current_location:
                text_match = text[:50] if len(text) > 50 else text
                location = ElementSelectorLocation(
                    selector=current_location.selector,
                    selector_type=current_location.selector_type,
                    text_match=text_match,
                )

            text_chunks.append(
                TextChunk(
                    text=text,
                    source_id=source.source_id,
                    source_type=source.source_type,
                    location=location,
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
            ElementSelectorLocation for the chunk, or None if not available.
        """
        return chunk.location

    def get_deep_link(self, chunk: TextChunk, base_url: str) -> str | None:
        """Generate a deep link URL with text fragment.

        Creates a URL with text fragment (#:~:text=) to jump directly
        to the text position in the browser.

        Args:
            chunk: The text chunk to generate a link for.
            base_url: The base URL of the web page.

        Returns:
            URL with text fragment (e.g., https://example.com#:~:text=some%20text),
            or None if no location is available.
        """
        location = self.get_location(chunk)
        if location is None:
            return None
        return location.to_deep_link(base_url)
