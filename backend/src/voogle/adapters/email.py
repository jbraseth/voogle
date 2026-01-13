# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Email content adapter for EML/MBOX ingestion with thread reconstruction.

This module provides an EmailAdapter that implements the ContentAdapter interface
for email messages. It supports EML and MBOX file formats, thread reconstruction
from References/In-Reply-To headers, body extraction from both plain text and
HTML, and attachment delegation to other adapters.
"""
import email
import email.policy
import hashlib
import html
import logging
import mailbox
import re
from collections.abc import AsyncIterator
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path
from typing import Any

from voogle.adapters.base import (
    ChunkConfig,
    ContentAdapter,
    ContentSource,
    RawChunk,
    TextChunk,
)
from voogle.core.fragment import ContentType
from voogle.core.location import EmailThreadLocation, Location

logger = logging.getLogger(__name__)


# Supported email file extensions
EMAIL_EXTENSIONS: frozenset[str] = frozenset({".eml", ".mbox"})


@dataclass
class EmailConfig:
    """Configuration for email extraction.

    Attributes:
        extract_html: Whether to extract text from HTML parts.
        extract_attachments: Whether to delegate attachments to other adapters.
        include_headers: Whether to include email headers in extracted text.
        reconstruct_threads: Whether to reconstruct thread relationships.
        header_fields: List of header fields to include if include_headers is True.
    """

    extract_html: bool = True
    extract_attachments: bool = True
    include_headers: bool = True
    reconstruct_threads: bool = True
    header_fields: tuple[str, ...] = ("From", "To", "Subject", "Date")


class EmailAdapter(ContentAdapter):
    """Content adapter for email messages (EML/MBOX format).

    Extracts text content from email messages, reconstructs thread relationships
    from References/In-Reply-To headers, and can delegate attachments to other
    adapters for processing.

    Example:
        >>> adapter = EmailAdapter()
        >>> source = ContentSource(
        ...     source_id="email-123",
        ...     source_type=ContentType.EMAIL,
        ...     path=Path("/data/messages.mbox"),
        ... )
        >>> async for chunk in adapter.extract(source):
        ...     print(chunk.text, chunk.location)
    """

    def __init__(self, config: EmailConfig | None = None) -> None:
        """Initialize the email adapter.

        Args:
            config: Email extraction configuration. Uses defaults if not provided.
        """
        self._config = config or EmailConfig()
        # Thread tracking: message_id -> (thread_id, position)
        self._thread_map: dict[str, tuple[str, int]] = {}
        # Track thread sizes for location metadata
        self._thread_sizes: dict[str, int] = {}

    @property
    def supported_types(self) -> frozenset[ContentType]:
        """Return the content types this adapter can process.

        Returns:
            Frozen set containing ContentType.EMAIL.
        """
        return frozenset({ContentType.EMAIL})

    def supports(self, source: ContentSource) -> bool:
        """Check if this adapter can process the given source.

        Args:
            source: The content source to check.

        Returns:
            True if the source is an email file (EML/MBOX).
        """
        if source.source_type != ContentType.EMAIL:
            return False

        # Check file extension if path is available
        if source.path is not None:
            suffix = source.path.suffix.lower()
            return suffix in EMAIL_EXTENSIONS

        # Check URL extension or MIME type
        if source.url is not None:
            # Try to extract extension from URL path
            from urllib.parse import urlparse

            parsed = urlparse(source.url)
            url_path = parsed.path
            if "." in url_path:
                suffix = "." + url_path.rsplit(".", 1)[-1].lower()
                if suffix in EMAIL_EXTENSIONS:
                    return True

            # Check MIME type in metadata as fallback
            mime_type = source.metadata.get("mime_type", "")
            return mime_type in ("message/rfc822", "application/mbox")

        return False

    async def extract(self, source: ContentSource) -> AsyncIterator[RawChunk]:
        """Extract text chunks from email messages.

        Extracts email body text with thread position information.
        Reconstructs threads from References/In-Reply-To headers.

        Args:
            source: The email source to extract from.

        Yields:
            RawChunk instances with extracted text and EmailThreadLocation.

        Raises:
            ValueError: If the source is not supported or file not found.
        """
        if not self.supports(source):
            raise ValueError(f"Unsupported source: {source.source_id}")

        if source.path is None:
            raise ValueError(
                f"Email source {source.source_id} requires a local file path"
            )

        if not source.path.exists():
            raise ValueError(f"Email file not found: {source.path}")

        logger.info("Starting email extraction of %s", source.path)

        # Reset thread tracking for this extraction
        self._thread_map = {}
        self._thread_sizes = {}

        suffix = source.path.suffix.lower()

        if suffix == ".mbox":
            async for chunk in self._extract_mbox(source.path):
                yield chunk
        else:  # .eml
            async for chunk in self._extract_eml(source.path):
                yield chunk

        logger.info("Completed email extraction of %s", source.path)

    async def _extract_mbox(self, path: Path) -> AsyncIterator[RawChunk]:
        """Extract messages from an MBOX file.

        Args:
            path: Path to the MBOX file.

        Yields:
            RawChunk instances for each message.
        """
        mbox = mailbox.mbox(str(path))
        try:
            # First pass: build thread map if reconstruction enabled
            if self._config.reconstruct_threads:
                self._build_thread_map(list(mbox))

            # Second pass: extract content
            for msg in mbox:
                async for chunk in self._extract_message(msg):
                    yield chunk
        finally:
            mbox.close()

    async def _extract_eml(self, path: Path) -> AsyncIterator[RawChunk]:
        """Extract a single EML file.

        Args:
            path: Path to the EML file.

        Yields:
            RawChunk instances for the message.
        """
        with open(path, "rb") as f:
            msg = email.message_from_binary_file(f, policy=email.policy.default)

        # For single message, thread is just this message
        message_id = self._get_message_id(msg)
        thread_id = self._compute_thread_id([message_id])
        self._thread_map[message_id] = (thread_id, 1)
        self._thread_sizes[thread_id] = 1

        async for chunk in self._extract_message(msg):
            yield chunk

    def _build_thread_map(self, messages: list[Any]) -> None:
        """Build thread relationships from message headers.

        Uses References and In-Reply-To headers to reconstruct
        thread structure. Messages are grouped by their thread root.

        Args:
            messages: List of email message objects.
        """
        # Map message_id to its references
        id_to_refs: dict[str, list[str]] = {}
        # Map message_id to message for ordering
        id_to_msg: dict[str, Any] = {}

        for msg in messages:
            message_id = self._get_message_id(msg)
            id_to_msg[message_id] = msg

            # Get thread references
            refs = self._get_thread_references(msg)
            id_to_refs[message_id] = refs

        # Group messages by thread root
        thread_groups: dict[str, list[str]] = {}

        for message_id, refs in id_to_refs.items():
            # Thread root is the first reference, or this message if no refs
            if refs:
                thread_root = refs[0]
            else:
                thread_root = message_id

            if thread_root not in thread_groups:
                thread_groups[thread_root] = []
            thread_groups[thread_root].append(message_id)

        # Assign positions within each thread
        for thread_root, message_ids in thread_groups.items():
            # Sort by date if available
            sorted_ids = self._sort_by_date(message_ids, id_to_msg)
            thread_id = self._compute_thread_id([thread_root])
            thread_size = len(sorted_ids)
            self._thread_sizes[thread_id] = thread_size

            for position, msg_id in enumerate(sorted_ids, start=1):
                self._thread_map[msg_id] = (thread_id, position)

    def _sort_by_date(
        self, message_ids: list[str], id_to_msg: dict[str, Any]
    ) -> list[str]:
        """Sort message IDs by their Date header.

        Args:
            message_ids: List of message IDs to sort.
            id_to_msg: Mapping of message ID to message object.

        Returns:
            Sorted list of message IDs.
        """
        from email.utils import parsedate_to_datetime

        def get_date(msg_id: str) -> float:
            msg = id_to_msg.get(msg_id)
            if msg is None:
                return 0.0
            date_str = msg.get("Date", "")
            if not date_str:
                return 0.0
            try:
                dt = parsedate_to_datetime(date_str)
                return dt.timestamp()
            except (TypeError, ValueError):
                return 0.0

        return sorted(message_ids, key=get_date)

    def _get_message_id(self, msg: Any) -> str:
        """Get the Message-ID header from a message.

        Args:
            msg: Email message object.

        Returns:
            Message-ID string, or generated ID if not present.
        """
        message_id = msg.get("Message-ID", "")
        if message_id:
            return str(message_id).strip()

        # Generate a unique ID based on content hash
        content = str(msg)
        return f"<generated-{hashlib.sha256(content.encode()).hexdigest()[:16]}>"

    def _get_thread_references(self, msg: Any) -> list[str]:
        """Get thread references from References and In-Reply-To headers.

        Args:
            msg: Email message object.

        Returns:
            List of message IDs that this message references.
        """
        refs: list[str] = []

        # Parse References header
        references = msg.get("References", "")
        if references:
            # Extract message IDs (format: <id@domain>)
            pattern = r"<[^>]+>"
            refs.extend(re.findall(pattern, str(references)))

        # Parse In-Reply-To header
        in_reply_to = msg.get("In-Reply-To", "")
        if in_reply_to:
            pattern = r"<[^>]+>"
            for ref in re.findall(pattern, str(in_reply_to)):
                if ref not in refs:
                    refs.append(ref)

        return refs

    def _compute_thread_id(self, refs: list[str]) -> str:
        """Compute a stable thread ID from references.

        Args:
            refs: List of message ID references.

        Returns:
            A short hash string to identify the thread.
        """
        if not refs:
            return "orphan"

        # Use first reference (thread root) for thread ID
        root = refs[0]
        return hashlib.sha256(root.encode()).hexdigest()[:12]

    async def _extract_message(self, msg: Any) -> AsyncIterator[RawChunk]:
        """Extract text content from a single email message.

        Args:
            msg: Email message object.

        Yields:
            RawChunk instances with message text and location.
        """
        message_id = self._get_message_id(msg)
        thread_info = self._thread_map.get(message_id)

        if thread_info:
            thread_id, position = thread_info
            total = self._thread_sizes.get(thread_id)
        else:
            thread_id = self._compute_thread_id([message_id])
            position = 1
            total = 1

        location = EmailThreadLocation(
            message_id=message_id,
            thread_id=thread_id,
            thread_position=position,
            total_in_thread=total,
        )

        # Build text content
        text_parts: list[str] = []

        # Include headers if configured
        if self._config.include_headers:
            header_text = self._extract_headers(msg)
            if header_text:
                text_parts.append(header_text)

        # Extract body
        body_text = self._extract_body(msg)
        if body_text:
            text_parts.append(body_text)

        if text_parts:
            full_text = "\n\n".join(text_parts)
            full_text = self._normalize_text(full_text)

            if full_text:
                metadata = self._extract_metadata(msg)
                yield RawChunk(
                    text=full_text,
                    location=location,
                    metadata=metadata,
                )

        # Extract attachments if configured
        if self._config.extract_attachments:
            async for chunk in self._extract_attachments(msg, location):
                yield chunk

    def _extract_headers(self, msg: Any) -> str:
        """Extract configured header fields as text.

        Args:
            msg: Email message object.

        Returns:
            Header text in "Field: Value" format.
        """
        header_lines: list[str] = []

        for field in self._config.header_fields:
            value = msg.get(field, "")
            if value:
                header_lines.append(f"{field}: {value}")

        return "\n".join(header_lines)

    def _extract_body(self, msg: Any) -> str:
        """Extract body text from message parts.

        Prefers plain text, falls back to HTML if configured.

        Args:
            msg: Email message object.

        Returns:
            Extracted body text.
        """
        plain_text = ""
        html_text = ""

        if isinstance(msg, EmailMessage):
            body = msg.get_body(preferencelist=("plain", "html"))
            if body:
                content_type = body.get_content_type()
                content = body.get_content()
                if content_type == "text/plain" and isinstance(content, str):
                    plain_text = content
                elif content_type == "text/html" and isinstance(content, str):
                    html_text = content
        else:
            # Handle older message format
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain" and not plain_text:
                        payload = part.get_payload(decode=True)
                        if payload:
                            charset = part.get_content_charset() or "utf-8"
                            try:
                                plain_text = payload.decode(charset, errors="replace")
                            except (LookupError, UnicodeDecodeError):
                                plain_text = payload.decode("utf-8", errors="replace")
                    elif content_type == "text/html" and not html_text:
                        payload = part.get_payload(decode=True)
                        if payload:
                            charset = part.get_content_charset() or "utf-8"
                            try:
                                html_text = payload.decode(charset, errors="replace")
                            except (LookupError, UnicodeDecodeError):
                                html_text = payload.decode("utf-8", errors="replace")
            else:
                content_type = msg.get_content_type()
                payload = msg.get_payload(decode=True)
                if payload:
                    charset = msg.get_content_charset() or "utf-8"
                    try:
                        text = payload.decode(charset, errors="replace")
                    except (LookupError, UnicodeDecodeError):
                        text = payload.decode("utf-8", errors="replace")
                    if content_type == "text/plain":
                        plain_text = text
                    elif content_type == "text/html":
                        html_text = text

        # Prefer plain text
        if plain_text:
            return plain_text

        # Fall back to HTML if configured
        if html_text and self._config.extract_html:
            return self._html_to_text(html_text)

        return ""

    def _html_to_text(self, html_content: str) -> str:
        """Convert HTML content to plain text.

        Args:
            html_content: HTML string to convert.

        Returns:
            Plain text extracted from HTML.
        """
        # Remove script and style elements
        text = re.sub(r"<script[^>]*>.*?</script>", "", html_content, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)

        # Add newlines for block elements
        block_tags = ["p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6"]
        for tag in block_tags:
            text = re.sub(rf"<{tag}[^>]*>", "\n", text, flags=re.IGNORECASE)
            text = re.sub(rf"</{tag}>", "\n", text, flags=re.IGNORECASE)

        # Remove remaining HTML tags
        text = re.sub(r"<[^>]+>", "", text)

        # Unescape HTML entities
        text = html.unescape(text)

        return text

    async def _extract_attachments(
        self, msg: Any, parent_location: EmailThreadLocation
    ) -> AsyncIterator[RawChunk]:
        """Extract attachment information for delegation.

        Note: Full attachment extraction requires integration with
        the adapter registry to delegate to appropriate adapters.
        This implementation extracts attachment metadata.

        Args:
            msg: Email message object.
            parent_location: Location of the parent message.

        Yields:
            RawChunk instances for attachment metadata.
        """
        if isinstance(msg, EmailMessage):
            for attachment in msg.iter_attachments():
                filename = attachment.get_filename()
                content_type = attachment.get_content_type()

                if filename:
                    yield RawChunk(
                        text=f"[Attachment: {filename} ({content_type})]",
                        location=parent_location,
                        metadata={
                            "attachment": True,
                            "filename": filename,
                            "content_type": content_type,
                        },
                    )
        else:
            # Handle older message format
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_maintype() == "multipart":
                        continue
                    filename = part.get_filename()
                    if filename:
                        content_type = part.get_content_type()
                        yield RawChunk(
                            text=f"[Attachment: {filename} ({content_type})]",
                            location=parent_location,
                            metadata={
                                "attachment": True,
                                "filename": filename,
                                "content_type": content_type,
                            },
                        )

    def _extract_metadata(self, msg: Any) -> dict[str, Any]:
        """Extract email metadata for RawChunk.

        Args:
            msg: Email message object.

        Returns:
            Dictionary of email metadata.
        """
        metadata: dict[str, Any] = {
            "content_type": "email",
        }

        # Extract common headers
        for header in ("From", "To", "Cc", "Subject", "Date", "Message-ID"):
            value = msg.get(header)
            if value:
                metadata[header.lower().replace("-", "_")] = str(value)

        return metadata

    def _normalize_text(self, text: str) -> str:
        """Normalize extracted text.

        Args:
            text: Raw extracted text.

        Returns:
            Normalized text with cleaned whitespace.
        """
        # Replace multiple whitespace with single space (preserve newlines)
        text = re.sub(r"[^\S\n]+", " ", text)
        # Collapse multiple newlines
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Strip leading/trailing whitespace
        text = text.strip()
        return text

    def chunk(
        self,
        raw_chunks: list[RawChunk],
        source: ContentSource,
        config: ChunkConfig | None = None,
    ) -> list[TextChunk]:
        """Process raw email chunks into text chunks for embedding.

        Combines email text into chunks of approximately target_words words,
        preserving thread location information.

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
        current_location: EmailThreadLocation | None = None
        current_metadata: dict[str, Any] = {}
        sequence_index = 0

        for raw_chunk in raw_chunks:
            words = raw_chunk.text.split()

            # Update location (use first chunk's location for the combined chunk)
            if current_location is None and isinstance(raw_chunk.location, EmailThreadLocation):
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
            EmailThreadLocation for the chunk, or None if not available.
        """
        return chunk.location

    def get_deep_link(self, chunk: TextChunk, base_url: str) -> str | None:
        """Generate a deep link URL for a text chunk.

        Creates a URL with message-id parameter to navigate directly
        to the email message.

        Args:
            chunk: The text chunk to generate a link for.
            base_url: The base URL of the email archive.

        Returns:
            URL with message-id parameter, or None if no location available.
        """
        location = self.get_location(chunk)
        if location is None:
            return None
        return location.to_deep_link(base_url)
