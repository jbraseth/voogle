# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for MCP corpus resources."""

import pytest

from voogle.core import ContentType
from voogle.mcp.resources import (
    CorpusResource,
    CorpusResourceContent,
    CorpusResourceProvider,
    get_corpus_resource_content,
    get_corpus_resource_templates,
    get_corpus_resources,
)
from voogle.services.corpus_service import CorpusService

pytestmark = pytest.mark.unit


class TestCorpusResourceDataclasses:
    """Tests for resource dataclass structures."""

    @pytest.mark.description("CorpusResource has correct default mime_type")
    def test_corpus_resource_defaults(self) -> None:
        resource = CorpusResource(
            uri="semantic://test/info",
            name="Test Corpus",
            description="Test description",
        )
        assert resource.mime_type == "application/json"

    @pytest.mark.description("CorpusResource stores all fields correctly")
    def test_corpus_resource_fields(self) -> None:
        resource = CorpusResource(
            uri="semantic://corpus-1/info",
            name="My Corpus",
            description="A test corpus",
            mime_type="text/plain",
        )
        assert resource.uri == "semantic://corpus-1/info"
        assert resource.name == "My Corpus"
        assert resource.description == "A test corpus"
        assert resource.mime_type == "text/plain"

    @pytest.mark.description("CorpusResourceContent stores all fields correctly")
    def test_corpus_resource_content_fields(self) -> None:
        content = CorpusResourceContent(
            id="corpus-1",
            name="Podcasts",
            description="Audio podcasts",
            document_count=100,
            last_updated="2025-01-01T00:00:00",
            content_types=["audio"],
            settings={"language": "en"},
        )
        assert content.id == "corpus-1"
        assert content.name == "Podcasts"
        assert content.description == "Audio podcasts"
        assert content.document_count == 100
        assert content.last_updated == "2025-01-01T00:00:00"
        assert content.content_types == ["audio"]
        assert content.settings == {"language": "en"}


class TestCorpusResourceProviderEmpty:
    """Tests for CorpusResourceProvider with empty service."""

    @pytest.mark.description("list_resources returns empty list when no corpora exist")
    def test_empty_list_resources(self) -> None:
        service = CorpusService()
        provider = CorpusResourceProvider(corpus_service=service)
        resources = provider.list_resources()
        assert resources == []

    @pytest.mark.description("get_resource returns None for non-existent corpus")
    def test_get_nonexistent_resource(self) -> None:
        service = CorpusService()
        provider = CorpusResourceProvider(corpus_service=service)
        content = provider.get_resource("nonexistent")
        assert content is None


class TestCorpusResourceProviderWithData:
    """Tests for CorpusResourceProvider with corpus data."""

    @pytest.fixture
    def corpus_service(self) -> CorpusService:
        """Create a corpus service with test data."""
        service = CorpusService()
        service.create(
            id="podcasts",
            name="Podcasts",
            description="Audio podcast episodes",
            content_types=[ContentType.AUDIO],
            settings={"language": "en"},
        )
        service.create(
            id="videos",
            name="Videos",
            description="Video content collection",
            content_types=[ContentType.VIDEO],
            settings={"resolution": "1080p"},
        )
        service.create(
            id="docs",
            name="Documents",
            description="Text documents",
            content_types=[ContentType.DOCUMENT],
        )
        return service

    @pytest.mark.description("list_resources returns all corpora as resources")
    def test_list_resources(self, corpus_service: CorpusService) -> None:
        provider = CorpusResourceProvider(corpus_service=corpus_service)
        resources = provider.list_resources()

        assert len(resources) == 3
        uris = [r.uri for r in resources]
        assert "semantic://podcasts/info" in uris
        assert "semantic://videos/info" in uris
        assert "semantic://docs/info" in uris

    @pytest.mark.description("list_resources returns correct resource metadata")
    def test_list_resources_metadata(self, corpus_service: CorpusService) -> None:
        provider = CorpusResourceProvider(corpus_service=corpus_service)
        resources = provider.list_resources()

        podcasts = next(r for r in resources if "podcasts" in r.uri)
        assert podcasts.name == "Podcasts"
        assert podcasts.description == "Audio podcast episodes"
        assert podcasts.mime_type == "application/json"

    @pytest.mark.description("get_resource returns correct corpus content")
    def test_get_resource(self, corpus_service: CorpusService) -> None:
        provider = CorpusResourceProvider(corpus_service=corpus_service)
        content = provider.get_resource("podcasts")

        assert content is not None
        assert content.id == "podcasts"
        assert content.name == "Podcasts"
        assert content.description == "Audio podcast episodes"
        assert content.document_count == 0
        assert "audio" in content.content_types
        assert content.settings == {"language": "en"}
        assert content.last_updated is not None

    @pytest.mark.description("get_resource returns None for non-existent corpus")
    def test_get_resource_not_found(self, corpus_service: CorpusService) -> None:
        provider = CorpusResourceProvider(corpus_service=corpus_service)
        content = provider.get_resource("nonexistent")
        assert content is None


class TestCorpusResourceTemplates:
    """Tests for resource templates."""

    @pytest.mark.description("get_resource_templates returns corpus info template")
    def test_get_resource_templates(self) -> None:
        provider = CorpusResourceProvider()
        templates = provider.get_resource_templates()

        assert len(templates) == 1
        template = templates[0]
        assert template["uriTemplate"] == "semantic://{corpus_id}/info"
        assert template["name"] == "Corpus Information"
        assert "description" in template
        assert template["mimeType"] == "application/json"


class TestModuleLevelFunctions:
    """Tests for module-level convenience functions."""

    @pytest.fixture
    def corpus_service(self) -> CorpusService:
        """Create a corpus service with test data."""
        service = CorpusService()
        service.create(
            id="test-corpus",
            name="Test Corpus",
            description="A test corpus",
            content_types=[ContentType.DOCUMENT],
        )
        return service

    @pytest.mark.description("get_corpus_resources returns list of resource dicts")
    def test_get_corpus_resources(self, corpus_service: CorpusService) -> None:
        resources = get_corpus_resources(corpus_service)

        assert len(resources) == 1
        resource = resources[0]
        assert resource["uri"] == "semantic://test-corpus/info"
        assert resource["name"] == "Test Corpus"
        assert resource["description"] == "A test corpus"
        assert resource["mimeType"] == "application/json"

    @pytest.mark.description("get_corpus_resources returns empty list when no corpora")
    def test_get_corpus_resources_empty(self) -> None:
        service = CorpusService()
        resources = get_corpus_resources(service)
        assert resources == []

    @pytest.mark.description("get_corpus_resource_content returns corpus dict")
    def test_get_corpus_resource_content(self, corpus_service: CorpusService) -> None:
        content = get_corpus_resource_content("test-corpus", corpus_service)

        assert content is not None
        assert content["id"] == "test-corpus"
        assert content["name"] == "Test Corpus"
        assert content["description"] == "A test corpus"
        assert content["document_count"] == 0
        assert "document" in content["content_types"]
        assert "last_updated" in content
        assert "settings" in content

    @pytest.mark.description("get_corpus_resource_content returns None for not found")
    def test_get_corpus_resource_content_not_found(
        self, corpus_service: CorpusService
    ) -> None:
        content = get_corpus_resource_content("nonexistent", corpus_service)
        assert content is None

    @pytest.mark.description("get_corpus_resource_templates returns template list")
    def test_get_corpus_resource_templates(self) -> None:
        templates = get_corpus_resource_templates()

        assert len(templates) == 1
        assert templates[0]["uriTemplate"] == "semantic://{corpus_id}/info"


class TestURIScheme:
    """Tests for URI scheme consistency."""

    @pytest.mark.description("CorpusResourceProvider uses semantic URI scheme")
    def test_uri_scheme(self) -> None:
        assert CorpusResourceProvider.URI_SCHEME == "semantic"

    @pytest.mark.description("resource URIs follow semantic://{id}/info pattern")
    def test_uri_pattern(self) -> None:
        service = CorpusService()
        service.create(id="my-corpus", name="Test", description="Test")
        provider = CorpusResourceProvider(corpus_service=service)

        resources = provider.list_resources()
        assert len(resources) == 1
        assert resources[0].uri == "semantic://my-corpus/info"


class TestLazyInitialization:
    """Tests for lazy service initialization."""

    @pytest.mark.description("CorpusResourceProvider lazily initializes service")
    def test_lazy_init(self) -> None:
        provider = CorpusResourceProvider()
        # Service should not be created yet
        assert provider._corpus_service is None

        # Accessing the property should create it
        service = provider.corpus_service
        assert service is not None
        assert provider._corpus_service is service

    @pytest.mark.description("CorpusResourceProvider reuses injected service")
    def test_injected_service(self) -> None:
        service = CorpusService()
        provider = CorpusResourceProvider(corpus_service=service)

        # Should use the injected service
        assert provider.corpus_service is service
