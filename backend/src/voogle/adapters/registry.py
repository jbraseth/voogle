# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Adapter registry for automatic discovery and MIME-type routing.

This module provides an AdapterRegistry that manages content adapters,
supporting automatic discovery via entry points, MIME-type routing,
priority-based selection, and fallback to a generic text adapter.
"""
import logging
from importlib.metadata import entry_points

from voogle.adapters.base import ContentAdapter, ContentSource
from voogle.core.fragment import ContentType

logger = logging.getLogger(__name__)


class AdapterRegistry:
    """Registry for content adapters with automatic discovery and routing.

    The registry manages content adapters and provides routing based on
    content type and MIME type. It supports:
    - Manual registration of adapters with priority
    - Automatic discovery via entry points
    - Content type-based adapter selection
    - MIME-type routing
    - Fallback to generic text adapter

    Adapters with higher priority values are preferred when multiple
    adapters can handle the same content type.

    Example:
        >>> registry = AdapterRegistry()
        >>> registry.register(MyAudioAdapter(), priority=10)
        >>> adapter = registry.get_adapter(audio_source)
    """

    # Entry point group name for adapter discovery
    ENTRY_POINT_GROUP = "voogle.adapters"

    # Default priority for registered adapters
    DEFAULT_PRIORITY = 0

    def __init__(self, auto_discover: bool = True) -> None:
        """Initialize the adapter registry.

        Args:
            auto_discover: If True, automatically discover and register
                adapters from entry points. Defaults to True.
        """
        # Map of content type -> list of (priority, adapter) tuples
        self._adapters: dict[ContentType, list[tuple[int, ContentAdapter]]] = {}

        # Map of MIME type -> content type for routing
        self._mime_mappings: dict[str, ContentType] = self._default_mime_mappings()

        # Fallback adapter for unrecognized content
        self._fallback_adapter: ContentAdapter | None = None

        logger.debug("Initializing AdapterRegistry (auto_discover=%s)", auto_discover)

        if auto_discover:
            self._discover_adapters()

    def _default_mime_mappings(self) -> dict[str, ContentType]:
        """Return default MIME type to content type mappings.

        Returns:
            Dictionary mapping MIME types to ContentType values.
        """
        return {
            # Audio types
            "audio/mpeg": ContentType.AUDIO,
            "audio/mp3": ContentType.AUDIO,
            "audio/wav": ContentType.AUDIO,
            "audio/ogg": ContentType.AUDIO,
            "audio/flac": ContentType.AUDIO,
            "audio/aac": ContentType.AUDIO,
            "audio/m4a": ContentType.AUDIO,
            "audio/x-m4a": ContentType.AUDIO,
            # Video types
            "video/mp4": ContentType.VIDEO,
            "video/mpeg": ContentType.VIDEO,
            "video/webm": ContentType.VIDEO,
            "video/ogg": ContentType.VIDEO,
            "video/quicktime": ContentType.VIDEO,
            "video/x-msvideo": ContentType.VIDEO,
            # Document types
            "application/pdf": ContentType.DOCUMENT,
            "application/msword": ContentType.DOCUMENT,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ContentType.DOCUMENT,
            # Slide types
            "application/vnd.ms-powerpoint": ContentType.SLIDE,
            "application/vnd.openxmlformats-officedocument.presentationml.presentation": ContentType.SLIDE,
            # Text types
            "text/plain": ContentType.TEXT,
            "text/html": ContentType.TEXT,
            "text/markdown": ContentType.TEXT,
            "application/json": ContentType.TEXT,
        }

    def _discover_adapters(self) -> None:
        """Discover and register adapters from entry points.

        Loads adapters registered under the 'voogle.adapters' entry point
        group. Each entry point should reference an adapter class or factory
        function that returns a ContentAdapter instance.
        """
        eps = entry_points(group=self.ENTRY_POINT_GROUP)

        discovered_count = 0
        for ep in eps:
            try:
                adapter_factory = ep.load()

                # Support both class and factory function
                if isinstance(adapter_factory, type):
                    adapter = adapter_factory()
                else:
                    adapter = adapter_factory()

                # Extract priority from entry point extras or use default
                priority = self._extract_priority(ep)

                self.register(adapter, priority=priority)
                discovered_count += 1
                logger.info(
                    "Discovered adapter '%s' (priority=%d) from entry point",
                    ep.name,
                    priority,
                )
            except Exception as e:
                logger.warning(
                    "Failed to load adapter from entry point '%s': %s",
                    ep.name,
                    e,
                )

        logger.debug("Discovered %d adapters from entry points", discovered_count)

    def _extract_priority(self, ep: object) -> int:
        """Extract priority from entry point metadata.

        Args:
            ep: Entry point object (reserved for future use).

        Returns:
            Priority value, or DEFAULT_PRIORITY if not specified.
        """
        # Entry points can have extras in brackets, e.g., "name[priority=10]"
        # For simplicity, we use default priority unless overridden
        # The ep parameter is kept for future extensibility
        _ = ep  # Explicitly acknowledge unused parameter
        return self.DEFAULT_PRIORITY

    def register(
        self,
        adapter: ContentAdapter,
        priority: int = DEFAULT_PRIORITY,
    ) -> None:
        """Register an adapter for its supported content types.

        Args:
            adapter: The content adapter to register.
            priority: Priority value for this adapter. Higher values
                are preferred when multiple adapters support the same
                content type. Defaults to DEFAULT_PRIORITY.

        Raises:
            TypeError: If adapter is not a ContentAdapter instance.
        """
        if not isinstance(adapter, ContentAdapter):
            raise TypeError(
                f"Expected ContentAdapter instance, got {type(adapter).__name__}"
            )

        for content_type in adapter.supported_types:
            if content_type not in self._adapters:
                self._adapters[content_type] = []

            self._adapters[content_type].append((priority, adapter))

            # Keep sorted by priority (highest first)
            self._adapters[content_type].sort(key=lambda x: x[0], reverse=True)

            logger.debug(
                "Registered adapter %s for %s (priority=%d)",
                type(adapter).__name__,
                content_type.name,
                priority,
            )

    def register_mime_mapping(self, mime_type: str, content_type: ContentType) -> None:
        """Register a custom MIME type to content type mapping.

        Args:
            mime_type: The MIME type string (e.g., "audio/custom").
            content_type: The ContentType this MIME type should map to.
        """
        self._mime_mappings[mime_type] = content_type
        logger.debug("Registered MIME mapping: %s -> %s", mime_type, content_type.name)

    def set_fallback_adapter(self, adapter: ContentAdapter) -> None:
        """Set the fallback adapter for unrecognized content.

        The fallback adapter is used when no other adapter matches
        the content source.

        Args:
            adapter: The adapter to use as fallback.

        Raises:
            TypeError: If adapter is not a ContentAdapter instance.
        """
        if not isinstance(adapter, ContentAdapter):
            raise TypeError(
                f"Expected ContentAdapter instance, got {type(adapter).__name__}"
            )

        self._fallback_adapter = adapter
        logger.info("Set fallback adapter: %s", type(adapter).__name__)

    def get_adapter(self, source: ContentSource) -> ContentAdapter | None:
        """Get the best adapter for a content source.

        Finds the most appropriate adapter based on:
        1. Content type from the source
        2. MIME type if available in source metadata
        3. Priority ranking among matching adapters
        4. Fallback adapter if no match found

        Args:
            source: The content source to find an adapter for.

        Returns:
            The best matching ContentAdapter, or None if no adapter
            can handle the source and no fallback is set.
        """
        content_type = source.source_type

        # Try to get MIME-based content type if available
        mime_type = source.metadata.get("mime_type")
        if mime_type and mime_type in self._mime_mappings:
            mapped_type = self._mime_mappings[mime_type]
            logger.debug(
                "MIME type '%s' mapped to %s for source %s",
                mime_type,
                mapped_type.name,
                source.source_id,
            )
            content_type = mapped_type

        # Find adapters for this content type
        adapters = self._adapters.get(content_type, [])

        # Check each adapter in priority order
        for priority, adapter in adapters:
            if adapter.supports(source):
                logger.debug(
                    "Selected adapter %s (priority=%d) for source %s",
                    type(adapter).__name__,
                    priority,
                    source.source_id,
                )
                return adapter

        # No matching adapter found, try fallback
        if self._fallback_adapter is not None:
            if self._fallback_adapter.supports(source):
                logger.debug(
                    "Using fallback adapter %s for source %s",
                    type(self._fallback_adapter).__name__,
                    source.source_id,
                )
                return self._fallback_adapter
            logger.debug(
                "Fallback adapter %s does not support source %s",
                type(self._fallback_adapter).__name__,
                source.source_id,
            )

        logger.warning(
            "No adapter found for source %s (type=%s, mime=%s)",
            source.source_id,
            content_type.name,
            mime_type,
        )
        return None

    def get_adapter_for_type(
        self, content_type: ContentType
    ) -> ContentAdapter | None:
        """Get the highest priority adapter for a content type.

        Args:
            content_type: The content type to find an adapter for.

        Returns:
            The highest priority adapter for this type, or None if
            no adapter is registered.
        """
        adapters = self._adapters.get(content_type, [])
        if adapters:
            priority, adapter = adapters[0]
            logger.debug(
                "Selected adapter %s (priority=%d) for type %s",
                type(adapter).__name__,
                priority,
                content_type.name,
            )
            return adapter
        return None

    def get_adapter_for_mime(self, mime_type: str) -> ContentAdapter | None:
        """Get an adapter based on MIME type.

        Args:
            mime_type: The MIME type to find an adapter for.

        Returns:
            The highest priority adapter for this MIME type, or None
            if the MIME type is not mapped or no adapter is registered.
        """
        content_type = self._mime_mappings.get(mime_type)
        if content_type is None:
            logger.debug("Unknown MIME type: %s", mime_type)
            return None

        return self.get_adapter_for_type(content_type)

    def list_adapters(self) -> dict[ContentType, list[tuple[int, str]]]:
        """List all registered adapters by content type.

        Returns:
            Dictionary mapping content types to lists of
            (priority, adapter_class_name) tuples.
        """
        result: dict[ContentType, list[tuple[int, str]]] = {}
        for content_type, adapters in self._adapters.items():
            result[content_type] = [
                (priority, type(adapter).__name__)
                for priority, adapter in adapters
            ]
        return result

    def list_mime_mappings(self) -> dict[str, ContentType]:
        """List all MIME type to content type mappings.

        Returns:
            Dictionary mapping MIME types to ContentType values.
        """
        return dict(self._mime_mappings)

    def __repr__(self) -> str:
        """Return a string representation of the registry.

        Returns:
            String showing number of adapters and content types.
        """
        total_adapters = sum(len(adapters) for adapters in self._adapters.values())
        content_types = len(self._adapters)
        fallback = (
            type(self._fallback_adapter).__name__
            if self._fallback_adapter
            else "None"
        )
        return (
            f"AdapterRegistry("
            f"adapters={total_adapters}, "
            f"content_types={content_types}, "
            f"fallback={fallback})"
        )
