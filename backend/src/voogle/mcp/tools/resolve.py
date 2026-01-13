# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""MCP resolve tool for deep link resolution from semantic URIs.

Provides the ResolveTool for resolving semantic URIs (semantic://corpus/doc#fragment)
into full content with metadata and deep link URLs.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
from urllib.parse import parse_qs, urlparse

from qdrant_client import models

from voogle import vector
from voogle.settings import settings


class OutputFormat(str, Enum):
    """Supported output formats for resolved content.

    TEXT: Plain text output
    MARKDOWN: Markdown formatted output
    HTML: HTML formatted output
    """

    TEXT = "text"
    MARKDOWN = "markdown"
    HTML = "html"


@dataclass
class ParsedURI:
    """Parsed components of a semantic URI.

    Attributes:
        scheme: URI scheme (semantic or voogle).
        corpus: Corpus identifier from the host component.
        document: Document/source identifier from the path.
        fragment: Fragment identifier (optional).
        time: Time offset in seconds (optional, from query params).
    """

    scheme: str
    corpus: Optional[str] = None
    document: Optional[str] = None
    fragment: Optional[str] = None
    time: Optional[float] = None


@dataclass
class ResolveOutput:
    """Output from the resolve tool.

    Attributes:
        content: The full resolved content.
        format: Output format used.
        uri: The original URI that was resolved.
        deep_link: URL to directly access this content in context.
        metadata: Additional metadata about the resolved content.
    """

    content: str
    format: OutputFormat
    uri: str
    deep_link: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ResolveTool:
    """MCP tool for resolving semantic URIs to full content.

    Provides deep link resolution from semantic URIs with support for:
    - URI parsing (semantic://corpus/doc#fragment or voogle://source?t=time)
    - Multiple output formats (text, markdown, html)
    - Metadata extraction
    - Deep link generation
    """

    name: str = "resolve"
    description: str = (
        "Resolve a semantic URI to retrieve full content, metadata, and deep link URL. "
        "Supports semantic://corpus/doc#fragment and voogle://source?t=time formats."
    )

    def __init__(
        self,
        qdrant_client: Optional[vector.qdrant_client.QdrantClient] = None,
    ) -> None:
        """Initialize the resolve tool.

        Args:
            qdrant_client: Optional QdrantClient for fetching content.
                If None, uses the configured client from settings.
        """
        self._qdrant_client = qdrant_client

    @property
    def qdrant_client(self) -> vector.qdrant_client.QdrantClient:
        """Get or lazily initialize the Qdrant client."""
        if self._qdrant_client is None:
            self._qdrant_client = vector.get_configured_client()
        return self._qdrant_client

    @property
    def input_schema(self) -> dict[str, Any]:
        """Return the JSON schema for tool input parameters.

        Returns:
            JSON Schema dictionary describing the input format.
        """
        return {
            "type": "object",
            "properties": {
                "uri": {
                    "type": "string",
                    "description": (
                        "Semantic URI to resolve. Supports formats: "
                        "semantic://corpus/doc#fragment or voogle://source?t=time"
                    ),
                    "minLength": 1,
                },
                "format": {
                    "type": "string",
                    "enum": ["text", "markdown", "html"],
                    "description": "Output format for the resolved content",
                    "default": "text",
                },
            },
            "required": ["uri"],
        }

    def parse_uri(self, uri: str) -> ParsedURI:
        """Parse a semantic URI into its components.

        Supports two URI formats:
        - semantic://corpus/document#fragment
        - voogle://source_id?t=time

        Args:
            uri: The URI string to parse.

        Returns:
            ParsedURI with extracted components.

        Raises:
            ValueError: If the URI is invalid or uses an unsupported scheme.
        """
        if not uri or not uri.strip():
            raise ValueError("uri cannot be empty")

        parsed = urlparse(uri.strip())

        # Validate scheme
        if parsed.scheme not in ("semantic", "voogle"):
            raise ValueError(
                f"Unsupported URI scheme: {parsed.scheme}. "
                "Expected 'semantic' or 'voogle'"
            )

        # Extract corpus (netloc/host)
        corpus = parsed.netloc if parsed.netloc else None

        # Extract document (path, strip leading /)
        document = parsed.path.lstrip("/") if parsed.path else None
        if document == "":
            document = None

        # For voogle:// URIs, the document is actually the host (no netloc)
        if parsed.scheme == "voogle" and corpus:
            document = corpus
            corpus = None

        # Extract fragment
        fragment = parsed.fragment if parsed.fragment else None

        # Extract time from query parameters
        time: Optional[float] = None
        if parsed.query:
            query_params = parse_qs(parsed.query)
            if "t" in query_params:
                try:
                    time = float(query_params["t"][0])
                except (ValueError, IndexError):
                    pass

        return ParsedURI(
            scheme=parsed.scheme,
            corpus=corpus,
            document=document,
            fragment=fragment,
            time=time,
        )

    def _format_content(
        self,
        text: str,
        format: OutputFormat,
        metadata: dict[str, Any],
    ) -> str:
        """Format content according to the specified output format.

        Args:
            text: Raw text content.
            format: Desired output format.
            metadata: Metadata for formatting context.

        Returns:
            Formatted content string.
        """
        if format == OutputFormat.TEXT:
            return text

        source_id = metadata.get("source_id", "")
        source_type = metadata.get("source_type", "")

        if format == OutputFormat.MARKDOWN:
            lines = []
            if source_id:
                lines.append(f"**Source:** {source_id}")
            if source_type:
                lines.append(f"**Type:** {source_type}")
            if metadata.get("start_time") is not None:
                lines.append(f"**Time:** {metadata['start_time']}s")
            if lines:
                lines.append("")
            lines.append(text)
            return "\n".join(lines)

        # format == OutputFormat.HTML
        html_parts = ['<div class="voogle-content">']
        if source_id or source_type:
            html_parts.append('  <div class="metadata">')
            if source_id:
                html_parts.append(f"    <span class=\"source\">{source_id}</span>")
            if source_type:
                html_parts.append(f"    <span class=\"type\">{source_type}</span>")
            if metadata.get("start_time") is not None:
                html_parts.append(
                    f"    <span class=\"time\">{metadata['start_time']}s</span>"
                )
            html_parts.append("  </div>")
        html_parts.append(f'  <p class="content">{text}</p>')
        html_parts.append("</div>")
        return "\n".join(html_parts)

    def _generate_deep_link(
        self,
        source_id: str,
        start_time: Optional[float] = None,
    ) -> str:
        """Generate a deep link URL for the content.

        Args:
            source_id: Source document identifier.
            start_time: Optional time offset in seconds.

        Returns:
            Deep link URL string.
        """
        base_url = getattr(settings, "FRONTEND_URL", "https://voogle.local")

        if start_time is not None:
            return f"{base_url}/play/{source_id}?t={int(start_time)}"
        return f"{base_url}/play/{source_id}"

    def _fetch_by_fragment_id(
        self,
        fragment_id: str,
        collection_name: Optional[str] = None,
    ) -> Optional[dict[str, Any]]:
        """Fetch a fragment by its ID from Qdrant.

        Args:
            fragment_id: The fragment ID to fetch.
            collection_name: Optional collection name override.

        Returns:
            Fragment payload dict or None if not found.
        """
        coll_name = collection_name or vector.get_collection_name(
            settings.embeddings_provider
        )

        try:
            points = self.qdrant_client.retrieve(
                collection_name=coll_name,
                ids=[fragment_id],
                with_payload=True,
            )
            if points:
                return dict(points[0].payload or {})
        except Exception:
            pass

        return None

    def _fetch_by_source(
        self,
        source_id: str,
        time: Optional[float] = None,
        collection_name: Optional[str] = None,
    ) -> Optional[dict[str, Any]]:
        """Fetch fragment(s) by source ID and optional time.

        Args:
            source_id: The source document ID.
            time: Optional time offset to find the matching fragment.
            collection_name: Optional collection name override.

        Returns:
            Fragment payload dict or None if not found.
        """
        coll_name = collection_name or vector.get_collection_name(
            settings.embeddings_provider
        )

        # Build filter for source_id
        conditions: list[models.Condition] = [
            models.FieldCondition(
                key="source_id",
                match=models.MatchValue(value=source_id),
            )
        ]

        # If time specified, filter for fragments containing that time
        if time is not None:
            conditions.append(
                models.FieldCondition(
                    key="start_time",
                    range=models.Range(lte=time),
                )
            )
            conditions.append(
                models.FieldCondition(
                    key="end_time",
                    range=models.Range(gte=time),
                )
            )

        try:
            points = self.qdrant_client.scroll(
                collection_name=coll_name,
                scroll_filter=models.Filter(must=conditions),
                limit=1,
                with_payload=True,
            )[0]

            if points:
                return dict(points[0].payload or {})
        except Exception:
            pass

        # Fallback: try searching by source_id without time constraint
        if time is not None:
            fallback_conditions: list[models.Condition] = [
                models.FieldCondition(
                    key="source_id",
                    match=models.MatchValue(value=source_id),
                )
            ]
            try:
                points = self.qdrant_client.scroll(
                    collection_name=coll_name,
                    scroll_filter=models.Filter(must=fallback_conditions),
                    limit=1,
                    with_payload=True,
                )[0]

                if points:
                    return dict(points[0].payload or {})
            except Exception:
                pass

        return None

    def __call__(
        self,
        uri: str,
        format: str = "text",
    ) -> dict[str, Any]:
        """Resolve a semantic URI to full content.

        Args:
            uri: The semantic URI to resolve.
            format: Output format (text, markdown, html).

        Returns:
            Dictionary containing resolved content, metadata, and deep link.

        Raises:
            ValueError: If the URI is invalid or cannot be resolved.
        """
        # Parse and validate format
        try:
            output_format = OutputFormat(format.lower())
        except ValueError as e:
            raise ValueError(
                f"Unsupported format: {format}. Expected 'text', 'markdown', or 'html'"
            ) from e

        # Parse the URI
        parsed = self.parse_uri(uri)

        # Fetch the content based on URI type
        payload: Optional[dict[str, Any]] = None

        # If we have a fragment ID, try to fetch directly
        if parsed.fragment:
            payload = self._fetch_by_fragment_id(parsed.fragment)

        # If fragment lookup failed or no fragment, try by source
        if payload is None and parsed.document:
            payload = self._fetch_by_source(parsed.document, parsed.time)

        if payload is None:
            raise ValueError(f"Unable to resolve URI: {uri}")

        # Extract content and metadata
        text = str(payload.get("text", ""))
        source_id = str(payload.get("source_id", parsed.document or ""))
        source_type = payload.get("source_type")
        start_time = payload.get("start_time")
        end_time = payload.get("end_time")
        corpus_id = payload.get("corpus_id")

        metadata = {
            "source_id": source_id,
            "source_type": source_type,
            "start_time": start_time,
            "end_time": end_time,
            "corpus_id": corpus_id,
            **{
                k: v
                for k, v in payload.items()
                if k
                not in {
                    "text",
                    "source_id",
                    "source_type",
                    "start_time",
                    "end_time",
                    "corpus_id",
                }
            },
        }

        # Format the content
        formatted_content = self._format_content(text, output_format, metadata)

        # Generate deep link
        deep_link = self._generate_deep_link(source_id, start_time)

        return {
            "content": formatted_content,
            "format": output_format.value,
            "uri": uri,
            "deep_link": deep_link,
            "metadata": metadata,
        }


# Module-level instance for convenient access
resolve_tool = ResolveTool()
