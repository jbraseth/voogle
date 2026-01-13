# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""MCP resources for corpus access.

This module provides MCP resources for exposing corpora as application-controlled
data sources. Resources follow the MCP specification for read-only data access,
allowing AI assistants to discover and retrieve corpus metadata.

URI Patterns:
- semantic://corpora - List all available corpora
- semantic://{corpus_id}/info - Get metadata for a specific corpus
"""
from dataclasses import dataclass
from typing import Any, Optional

from voogle.services.corpus_service import CorpusService


@dataclass
class CorpusResource:
    """MCP resource representation of a corpus.

    Attributes:
        uri: The unique URI for this resource.
        name: Human-readable name for the resource.
        description: Description of the resource contents.
        mime_type: MIME type of the resource content.
    """

    uri: str
    name: str
    description: str
    mime_type: str = "application/json"


@dataclass
class CorpusResourceContent:
    """Content returned when reading a corpus resource.

    Attributes:
        id: Unique identifier of the corpus.
        name: Human-readable name of the corpus.
        description: Description of the corpus contents.
        document_count: Number of documents in the corpus.
        last_updated: ISO timestamp of last update.
        content_types: List of content types in the corpus.
        settings: Corpus-level configuration.
    """

    id: str
    name: str
    description: str
    document_count: int
    last_updated: str
    content_types: list[str]
    settings: dict[str, Any]


class CorpusResourceProvider:
    """Provider for corpus MCP resources.

    Handles resource listing and retrieval for corpora, exposing them
    through the MCP protocol for AI assistant access.
    """

    # Base URI scheme for corpus resources
    URI_SCHEME: str = "semantic"

    def __init__(self, corpus_service: Optional[CorpusService] = None) -> None:
        """Initialize the corpus resource provider.

        Args:
            corpus_service: Optional CorpusService instance for fetching corpora.
                If None, creates a new service with default configuration.
        """
        self._corpus_service = corpus_service

    @property
    def corpus_service(self) -> CorpusService:
        """Get or lazily initialize the corpus service."""
        if self._corpus_service is None:
            self._corpus_service = CorpusService()
        return self._corpus_service

    def list_resources(self) -> list[CorpusResource]:
        """List all available corpus resources.

        Returns:
            List of CorpusResource objects representing available corpora.
        """
        resources = []
        corpora = self.corpus_service.list_all()

        for corpus in corpora:
            resource = CorpusResource(
                uri=f"{self.URI_SCHEME}://{corpus.id}/info",
                name=corpus.name,
                description=corpus.description or f"Corpus: {corpus.name}",
            )
            resources.append(resource)

        return resources

    def get_resource(self, corpus_id: str) -> Optional[CorpusResourceContent]:
        """Get resource content for a specific corpus.

        Args:
            corpus_id: The unique identifier of the corpus.

        Returns:
            CorpusResourceContent with corpus metadata, or None if not found.
        """
        corpus = self.corpus_service.get(corpus_id)
        if corpus is None:
            return None

        return CorpusResourceContent(
            id=corpus.id,
            name=corpus.name,
            description=corpus.description,
            document_count=corpus.document_count,
            last_updated=corpus.updated_at.isoformat(),
            content_types=[ct.value for ct in corpus.content_types],
            settings=corpus.settings,
        )

    def get_resource_templates(self) -> list[dict[str, Any]]:
        """Get resource templates for dynamic resource URIs.

        Returns:
            List of resource template definitions.
        """
        return [
            {
                "uriTemplate": f"{self.URI_SCHEME}://{{corpus_id}}/info",
                "name": "Corpus Information",
                "description": "Get detailed information about a specific corpus",
                "mimeType": "application/json",
            }
        ]


# Module-level functions for convenient access


def get_corpus_resources(corpus_service: Optional[CorpusService] = None) -> list[dict[str, Any]]:
    """Get all corpus resources as dictionaries.

    This is the main entry point for listing corpus resources.
    Returns resources in the MCP-compatible format.

    Args:
        corpus_service: Optional CorpusService instance.

    Returns:
        List of resource dictionaries with uri, name, description, mimeType.
    """
    provider = CorpusResourceProvider(corpus_service=corpus_service)
    resources = provider.list_resources()

    return [
        {
            "uri": r.uri,
            "name": r.name,
            "description": r.description,
            "mimeType": r.mime_type,
        }
        for r in resources
    ]


def get_corpus_resource_content(
    corpus_id: str,
    corpus_service: Optional[CorpusService] = None,
) -> Optional[dict[str, Any]]:
    """Get resource content for a specific corpus.

    Args:
        corpus_id: The unique identifier of the corpus.
        corpus_service: Optional CorpusService instance.

    Returns:
        Dictionary with corpus metadata, or None if not found.
    """
    provider = CorpusResourceProvider(corpus_service=corpus_service)
    content = provider.get_resource(corpus_id)

    if content is None:
        return None

    return {
        "id": content.id,
        "name": content.name,
        "description": content.description,
        "document_count": content.document_count,
        "last_updated": content.last_updated,
        "content_types": content.content_types,
        "settings": content.settings,
    }


def get_corpus_resource_templates() -> list[dict[str, Any]]:
    """Get resource templates for dynamic corpus URIs.

    Returns:
        List of resource template definitions.
    """
    provider = CorpusResourceProvider()
    return provider.get_resource_templates()


def register_corpus_resources(mcp: Any) -> None:
    """Register corpus resources with a FastMCP server instance.

    This function registers the corpus resources using FastMCP's
    @mcp.resource decorator pattern, enabling MCP clients to
    discover and read corpus data.

    Args:
        mcp: FastMCP server instance to register resources with.
    """
    provider = CorpusResourceProvider()

    @mcp.resource("semantic://corpora")
    def list_corpora() -> list[dict[str, Any]]:
        """List all available corpora.

        Returns a list of all corpora with their basic metadata,
        allowing clients to discover available data sources.
        """
        return get_corpus_resources(provider.corpus_service)

    @mcp.resource("semantic://{corpus_id}/info")
    def get_corpus_info(corpus_id: str) -> dict[str, Any]:
        """Get detailed information about a specific corpus.

        Args:
            corpus_id: The unique identifier of the corpus.

        Returns:
            Corpus metadata including document count, content types,
            and configuration settings.

        Raises:
            ValueError: If the corpus is not found.
        """
        content = get_corpus_resource_content(corpus_id, provider.corpus_service)
        if content is None:
            raise ValueError(f"Corpus not found: {corpus_id}")
        return content
