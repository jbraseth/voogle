# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Feed generation orchestrator for source adapters.

This module discovers available adapters and runs them to generate
RSS feeds from external sources.
"""

from __future__ import annotations

import logging
from pathlib import Path

from voogle import settings
from voogle.sources import LocalFeed, SourceAdapter, SourceAdapterError

logger = logging.getLogger(__name__)


# Registry of feed paths for quick lookup
_feed_registry: dict[str, LocalFeed] = {}


def get_generated_feeds_dir() -> Path:
    """Return the directory for generated RSS feeds."""
    path = settings.settings.data_dir / "generated-feeds"
    path.mkdir(parents=True, exist_ok=True)
    return path


def discover_adapters() -> list[SourceAdapter]:
    """Discover all available source adapters.

    Returns adapters that have configuration present.
    Adapters without config directories are skipped.
    """
    adapters: list[SourceAdapter] = []
    local_dir = settings.settings.data_dir / "local"

    # YouTube adapter (if config exists)
    youtube_config_dir = local_dir / "youtube"
    if youtube_config_dir.exists() and any(youtube_config_dir.glob("*.json")):
        try:
            from voogle.sources.youtube import YouTubeAdapter

            adapters.append(
                YouTubeAdapter(
                    config_dir=youtube_config_dir,
                    output_dir=get_generated_feeds_dir() / "youtube",
                )
            )
        except ImportError:
            logger.debug("YouTube adapter not available (yt-dlp not installed)")

    # BibleProject adapter (if config exists)
    bibleproject_config_dir = local_dir / "bibleproject"
    if bibleproject_config_dir.exists() and any(bibleproject_config_dir.glob("*.json")):
        from voogle.sources.bibleproject import BibleProjectAdapter

        adapters.append(
            BibleProjectAdapter(
                config_dir=bibleproject_config_dir,
                output_dir=get_generated_feeds_dir() / "bibleproject",
            )
        )

    return adapters


def generate_all_feeds() -> list[LocalFeed]:
    """Run all adapters and collect generated feeds.

    Returns:
        List of all LocalFeed objects from all adapters

    Raises:
        SourceAdapterError: If any adapter fails (fail loud)
    """
    global _feed_registry
    _feed_registry.clear()

    all_feeds: list[LocalFeed] = []
    adapters = discover_adapters()

    if not adapters:
        logger.info("No source adapters configured")
        return all_feeds

    logger.info(f"Running {len(adapters)} source adapter(s)")

    for adapter in adapters:
        logger.info(f"Running adapter: {adapter.adapter_id}")
        try:
            feeds = adapter.generate_feeds()
            all_feeds.extend(feeds)

            # Register feeds for lookup
            for feed in feeds:
                _feed_registry[feed.channel_url] = feed
                logger.info(f"  Generated: {feed.channel_url} -> {feed.path}")

        except Exception as e:
            # Fail loud: Don't continue if any adapter fails
            raise SourceAdapterError(
                f"Adapter {adapter.adapter_id} failed to generate feeds: {e}"
            ) from e

    logger.info(f"Generated {len(all_feeds)} feed(s) total")
    return all_feeds


def find_local_feed(channel_url: str) -> LocalFeed | None:
    """Find a LocalFeed by its channel URL.

    Args:
        channel_url: The local:// URL for the channel

    Returns:
        LocalFeed if found, None otherwise
    """
    return _feed_registry.get(channel_url)


def is_local_feed_url(url: str) -> bool:
    """Check if a URL is a local feed URL."""
    return url.startswith("local://")
