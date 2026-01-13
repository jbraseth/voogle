# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for AdapterRegistry class."""
from collections.abc import AsyncIterator
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from voogle.adapters.base import (
    ChunkConfig,
    ContentAdapter,
    ContentSource,
    RawChunk,
    TextChunk,
)
from voogle.adapters.registry import AdapterRegistry
from voogle.core import ContentType, Location

pytestmark = pytest.mark.unit


class MockAdapter(ContentAdapter):
    """Mock adapter for testing."""

    def __init__(self, content_types: frozenset[ContentType]) -> None:
        self._content_types = content_types

    @property
    def supported_types(self) -> frozenset[ContentType]:
        return self._content_types

    def supports(self, source: ContentSource) -> bool:
        return source.source_type in self._content_types

    async def extract(self, source: ContentSource) -> AsyncIterator[RawChunk]:
        yield RawChunk(text="mock chunk")

    def chunk(
        self,
        raw_chunks: list[RawChunk],
        source: ContentSource,
        config: ChunkConfig | None = None,
    ) -> list[TextChunk]:
        return [
            TextChunk(
                text=rc.text,
                source_id=source.source_id,
                source_type=source.source_type,
                sequence_index=i,
            )
            for i, rc in enumerate(raw_chunks)
        ]

    def get_location(self, chunk: TextChunk) -> Location | None:
        return chunk.location

    def get_deep_link(self, chunk: TextChunk, base_url: str) -> str | None:
        return None


class SelectiveAdapter(ContentAdapter):
    """Adapter that only supports specific sources based on metadata."""

    def __init__(self, required_key: str) -> None:
        self._required_key = required_key

    @property
    def supported_types(self) -> frozenset[ContentType]:
        return frozenset({ContentType.AUDIO, ContentType.VIDEO})

    def supports(self, source: ContentSource) -> bool:
        return self._required_key in source.metadata

    async def extract(self, source: ContentSource) -> AsyncIterator[RawChunk]:
        yield RawChunk(text="selective chunk")

    def chunk(
        self,
        raw_chunks: list[RawChunk],
        source: ContentSource,
        config: ChunkConfig | None = None,
    ) -> list[TextChunk]:
        return []

    def get_location(self, chunk: TextChunk) -> Location | None:
        return None

    def get_deep_link(self, chunk: TextChunk, base_url: str) -> str | None:
        return None


class TestAdapterRegistryInit:
    """Tests for AdapterRegistry initialization."""

    @pytest.mark.description("AdapterRegistry initializes with empty state")
    def test_init_no_auto_discover(self) -> None:
        registry = AdapterRegistry(auto_discover=False)
        assert repr(registry) == "AdapterRegistry(adapters=0, content_types=0, fallback=None)"

    @pytest.mark.description("AdapterRegistry auto-discovery runs on init")
    @patch("voogle.adapters.registry.entry_points")
    def test_init_auto_discover_called(self, mock_entry_points: MagicMock) -> None:
        mock_entry_points.return_value = []
        registry = AdapterRegistry(auto_discover=True)
        mock_entry_points.assert_called_once_with(group="voogle.adapters")
        assert registry is not None


class TestAdapterRegistration:
    """Tests for adapter registration."""

    @pytest.mark.description("Register adapter for single content type")
    def test_register_single_type(self) -> None:
        registry = AdapterRegistry(auto_discover=False)
        adapter = MockAdapter(frozenset({ContentType.AUDIO}))

        registry.register(adapter)

        adapters = registry.list_adapters()
        assert ContentType.AUDIO in adapters
        assert len(adapters[ContentType.AUDIO]) == 1
        assert adapters[ContentType.AUDIO][0] == (0, "MockAdapter")

    @pytest.mark.description("Register adapter for multiple content types")
    def test_register_multiple_types(self) -> None:
        registry = AdapterRegistry(auto_discover=False)
        adapter = MockAdapter(frozenset({ContentType.AUDIO, ContentType.VIDEO}))

        registry.register(adapter)

        adapters = registry.list_adapters()
        assert ContentType.AUDIO in adapters
        assert ContentType.VIDEO in adapters

    @pytest.mark.description("Register adapter with custom priority")
    def test_register_with_priority(self) -> None:
        registry = AdapterRegistry(auto_discover=False)
        adapter = MockAdapter(frozenset({ContentType.AUDIO}))

        registry.register(adapter, priority=10)

        adapters = registry.list_adapters()
        assert adapters[ContentType.AUDIO][0] == (10, "MockAdapter")

    @pytest.mark.description("Register multiple adapters for same type respects priority")
    def test_priority_ordering(self) -> None:
        registry = AdapterRegistry(auto_discover=False)

        adapter_low = MockAdapter(frozenset({ContentType.AUDIO}))
        adapter_high = MockAdapter(frozenset({ContentType.AUDIO}))

        registry.register(adapter_low, priority=5)
        registry.register(adapter_high, priority=15)

        adapters = registry.list_adapters()
        # Higher priority should be first
        assert adapters[ContentType.AUDIO][0][0] == 15
        assert adapters[ContentType.AUDIO][1][0] == 5

    @pytest.mark.description("Register non-adapter raises TypeError")
    def test_register_invalid_type_raises(self) -> None:
        registry = AdapterRegistry(auto_discover=False)

        with pytest.raises(TypeError, match="Expected ContentAdapter instance"):
            registry.register("not an adapter")  # type: ignore[arg-type]


class TestGetAdapter:
    """Tests for getting adapters."""

    @pytest.mark.description("Get adapter for matching content type")
    def test_get_adapter_by_type(self) -> None:
        registry = AdapterRegistry(auto_discover=False)
        adapter = MockAdapter(frozenset({ContentType.AUDIO}))
        registry.register(adapter)

        source = ContentSource(
            source_id="test-123",
            source_type=ContentType.AUDIO,
            path=Path("/test.mp3"),
        )

        result = registry.get_adapter(source)
        assert result is adapter

    @pytest.mark.description("Get adapter returns None when no match")
    def test_get_adapter_no_match(self) -> None:
        registry = AdapterRegistry(auto_discover=False)
        adapter = MockAdapter(frozenset({ContentType.AUDIO}))
        registry.register(adapter)

        source = ContentSource(
            source_id="test-123",
            source_type=ContentType.VIDEO,
            path=Path("/test.mp4"),
        )

        result = registry.get_adapter(source)
        assert result is None

    @pytest.mark.description("Get adapter uses MIME type mapping")
    def test_get_adapter_by_mime(self) -> None:
        registry = AdapterRegistry(auto_discover=False)
        adapter = MockAdapter(frozenset({ContentType.AUDIO}))
        registry.register(adapter)

        # Source has AUDIO type with matching MIME type
        source = ContentSource(
            source_id="test-123",
            source_type=ContentType.AUDIO,
            path=Path("/test.mp3"),
            metadata={"mime_type": "audio/mpeg"},
        )

        result = registry.get_adapter(source)
        assert result is adapter

    @pytest.mark.description("Get adapter uses fallback when no match")
    def test_get_adapter_with_fallback(self) -> None:
        registry = AdapterRegistry(auto_discover=False)
        # Create a fallback that supports all content types
        fallback = MockAdapter(frozenset({
            ContentType.AUDIO,
            ContentType.VIDEO,
            ContentType.DOCUMENT,
            ContentType.SLIDE,
            ContentType.TEXT,
        }))
        registry.set_fallback_adapter(fallback)

        source = ContentSource(
            source_id="test-123",
            source_type=ContentType.DOCUMENT,
            path=Path("/test.pdf"),
        )

        result = registry.get_adapter(source)
        assert result is fallback

    @pytest.mark.description("Get adapter respects adapter.supports() method")
    def test_get_adapter_respects_supports(self) -> None:
        registry = AdapterRegistry(auto_discover=False)
        selective = SelectiveAdapter(required_key="special")
        generic = MockAdapter(frozenset({ContentType.AUDIO}))

        registry.register(selective, priority=10)
        registry.register(generic, priority=5)

        # Source without 'special' key should use generic adapter
        source_normal = ContentSource(
            source_id="test-1",
            source_type=ContentType.AUDIO,
            path=Path("/test.mp3"),
        )
        result = registry.get_adapter(source_normal)
        assert result is generic

        # Source with 'special' key should use selective adapter
        source_special = ContentSource(
            source_id="test-2",
            source_type=ContentType.AUDIO,
            path=Path("/test.mp3"),
            metadata={"special": True},
        )
        result = registry.get_adapter(source_special)
        assert result is selective

    @pytest.mark.description("Get adapter for content type directly")
    def test_get_adapter_for_type(self) -> None:
        registry = AdapterRegistry(auto_discover=False)
        adapter = MockAdapter(frozenset({ContentType.VIDEO}))
        registry.register(adapter, priority=5)

        result = registry.get_adapter_for_type(ContentType.VIDEO)
        assert result is adapter

        result = registry.get_adapter_for_type(ContentType.AUDIO)
        assert result is None

    @pytest.mark.description("Get adapter for MIME type")
    def test_get_adapter_for_mime(self) -> None:
        registry = AdapterRegistry(auto_discover=False)
        adapter = MockAdapter(frozenset({ContentType.AUDIO}))
        registry.register(adapter)

        result = registry.get_adapter_for_mime("audio/mpeg")
        assert result is adapter

        result = registry.get_adapter_for_mime("application/unknown")
        assert result is None


class TestMimeMappings:
    """Tests for MIME type mappings."""

    @pytest.mark.description("Default MIME mappings are present")
    def test_default_mappings(self) -> None:
        registry = AdapterRegistry(auto_discover=False)
        mappings = registry.list_mime_mappings()

        assert mappings["audio/mpeg"] == ContentType.AUDIO
        assert mappings["video/mp4"] == ContentType.VIDEO
        assert mappings["application/pdf"] == ContentType.DOCUMENT
        assert mappings["text/plain"] == ContentType.TEXT

    @pytest.mark.description("Register custom MIME mapping")
    def test_register_custom_mapping(self) -> None:
        registry = AdapterRegistry(auto_discover=False)

        registry.register_mime_mapping("audio/custom", ContentType.AUDIO)

        mappings = registry.list_mime_mappings()
        assert mappings["audio/custom"] == ContentType.AUDIO


class TestFallbackAdapter:
    """Tests for fallback adapter."""

    @pytest.mark.description("Set fallback adapter")
    def test_set_fallback(self) -> None:
        registry = AdapterRegistry(auto_discover=False)
        fallback = MockAdapter(frozenset({ContentType.TEXT}))

        registry.set_fallback_adapter(fallback)

        assert "fallback=MockAdapter" in repr(registry)

    @pytest.mark.description("Set invalid fallback raises TypeError")
    def test_set_invalid_fallback_raises(self) -> None:
        registry = AdapterRegistry(auto_discover=False)

        with pytest.raises(TypeError, match="Expected ContentAdapter instance"):
            registry.set_fallback_adapter("not an adapter")  # type: ignore[arg-type]

    @pytest.mark.description("Fallback not used when supports() returns False")
    def test_fallback_respects_supports(self) -> None:
        registry = AdapterRegistry(auto_discover=False)
        fallback = SelectiveAdapter(required_key="fallback_allowed")
        registry.set_fallback_adapter(fallback)

        # Source without required key should not use fallback
        source = ContentSource(
            source_id="test",
            source_type=ContentType.DOCUMENT,
            path=Path("/test.pdf"),
        )

        result = registry.get_adapter(source)
        assert result is None


class TestAutoDiscovery:
    """Tests for entry point auto-discovery."""

    @pytest.mark.description("Entry point adapter is discovered and registered")
    @patch("voogle.adapters.registry.entry_points")
    def test_discover_adapter_class(self, mock_entry_points: MagicMock) -> None:
        # Mock an entry point that returns an adapter class
        mock_ep = MagicMock()
        mock_ep.name = "mock-audio"
        mock_ep.load.return_value = lambda: MockAdapter(frozenset({ContentType.AUDIO}))
        mock_entry_points.return_value = [mock_ep]

        registry = AdapterRegistry(auto_discover=True)

        adapters = registry.list_adapters()
        assert ContentType.AUDIO in adapters

    @pytest.mark.description("Failed entry point load is logged and skipped")
    @patch("voogle.adapters.registry.entry_points")
    def test_discover_handles_load_error(self, mock_entry_points: MagicMock) -> None:
        mock_ep = MagicMock()
        mock_ep.name = "broken-adapter"
        mock_ep.load.side_effect = ImportError("Module not found")
        mock_entry_points.return_value = [mock_ep]

        # Should not raise
        registry = AdapterRegistry(auto_discover=True)
        assert registry is not None
        assert registry.list_adapters() == {}


class TestRegistryRepr:
    """Tests for registry string representation."""

    @pytest.mark.description("Registry repr shows adapter count")
    def test_repr_with_adapters(self) -> None:
        registry = AdapterRegistry(auto_discover=False)
        adapter1 = MockAdapter(frozenset({ContentType.AUDIO}))
        adapter2 = MockAdapter(frozenset({ContentType.VIDEO, ContentType.DOCUMENT}))

        registry.register(adapter1)
        registry.register(adapter2)

        result = repr(registry)
        assert "adapters=3" in result  # 1 + 2 registrations
        assert "content_types=3" in result

    @pytest.mark.description("Registry repr shows fallback")
    def test_repr_with_fallback(self) -> None:
        registry = AdapterRegistry(auto_discover=False)
        fallback = MockAdapter(frozenset({ContentType.TEXT}))
        registry.set_fallback_adapter(fallback)

        result = repr(registry)
        assert "fallback=MockAdapter" in result
