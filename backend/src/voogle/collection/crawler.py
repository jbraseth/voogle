# Copyright (c) 2022-2024 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Main high-level data collection related functions.

It offers functions to retrieve poscast channels and episodes.
"""

from __future__ import annotations

import importlib.resources
import json
import logging

from voogle import models, storage
from voogle.collection import feed, local
from voogle.sources import generator as source_generator

logger = logging.getLogger(__name__)


def default_channels() -> list[dict]:
    """Return list of default hardcoded podcast feeds"""
    with importlib.resources.open_text("voogle.collection", "urls.json") as f:
        data = json.load(f)
    return data


async def get_or_create_channel(
    feed_url: str, language: str | None = None
) -> tuple[bool, models.Channel | None]:
    """Read a feed url and return its corresponding channel object,
    creating it if needed or retrieving it from the database if it
    already exists.

    """
    logger.info(f"get or create channel from url: {feed_url}, lang {language}")
    created = False
    ch = await models.Channel.objects.get_or_none(feed=feed_url)
    if ch is None:
        created = True
        logger.info(f"creating the channel from url {feed_url}...")
        ch = feed.read_channel(feed_url, language)
        ch = await ch.save() if ch else None
    return created, ch


async def add_default_channels() -> int:
    """Add all the default channels hardcoded in Voogle's code (see
    urls.json)

    Return the number of channels added

    """
    logger.info("adding all the Voogle default channels ")
    total = 0
    for podcast in default_channels():
        url = podcast["url"]
        lang = podcast.get("language", None)
        logger.info(f"get or create channel {url}, lang {lang}")
        created, channel = await get_or_create_channel(podcast["url"], lang)
        total += 1 if created and channel else 0
    logger.info(f"finished adding default channels: {total}")
    return total


async def get_or_create_local_channel(info: dict) -> tuple[bool, models.Channel]:
    created = False
    logger.info(f"get or create local channel from folder {info['folder']}")
    ch = await models.Channel.objects.get_or_none(local_folder=info["folder"])
    if ch is None:
        created, ch = True, await local.read_local_channel(info).save()
    return created, ch


async def add_local_channels() -> int:
    """Add all the channels configured in the local sources file from
    local folder.

    Return the number of channels added.

    """
    logger.info("adding channels from local folder")
    total = 0
    if storage.LOCAL_SOURCES_PATH.exists():
        for channel_info in json.loads(storage.LOCAL_SOURCES_PATH.read_bytes()):
            created, _ = await get_or_create_local_channel(channel_info)
            total += 1 if created else 0
    return total


def read_local_feed_channel(feed_path: str, language: str | None = None) -> models.Channel | None:
    """Read a channel from a locally generated RSS feed file.

    Args:
        feed_path: Path to the RSS XML file
        language: Optional language override

    Returns:
        Channel model (not yet saved to database)
    """
    from pathlib import Path

    import xmltodict

    path = Path(feed_path)
    if not path.exists():
        logger.error(f"Local feed file not found: {feed_path}")
        return None

    try:
        with open(path, encoding="utf-8") as f:
            parsed = xmltodict.parse(f.read())
    except Exception as e:
        logger.error(f"Failed to parse local feed {feed_path}: {e}")
        return None

    channel_info = parsed["rss"]["channel"]
    language = language or channel_info.get("language", "").lower()

    return models.Channel(
        kind=models.ChannelKind.local.value,
        title=channel_info["title"],
        description=channel_info.get("description", ""),
        language=feed.LANGUAGES_MAP.get(language, language[:2] if language else ""),
        url=channel_info.get("link", ""),
        feed=feed_path,  # Use file path as feed identifier
        local_folder="",  # Not a folder-based local channel
        image=channel_info.get("image", {}).get("url", "") if isinstance(channel_info.get("image"), dict) else "",
    )


async def get_or_create_generated_channel(
    local_feed: source_generator.LocalFeed, language: str | None = None
) -> tuple[bool, models.Channel | None]:
    """Read a generated local feed and return its corresponding channel.

    Uses channel_url as the unique identifier to avoid duplicates.
    """
    logger.info(f"get or create channel from local feed: {local_feed.channel_url}")
    created = False

    # Use channel_url as the feed identifier for uniqueness
    ch = await models.Channel.objects.get_or_none(feed=local_feed.channel_url)
    if ch is None:
        created = True
        logger.info(f"creating channel from local feed: {local_feed.path}")
        ch = read_local_feed_channel(str(local_feed.path), language)
        if ch:
            # Override feed with channel_url for proper identification
            ch.feed = local_feed.channel_url
            ch = await ch.save()
    return created, ch


async def add_generated_channels() -> int:
    """Run source adapters and add channels from generated RSS feeds.

    Returns the number of channels added.
    """
    logger.info("generating RSS feeds from source adapters")
    try:
        local_feeds = source_generator.generate_all_feeds()
    except Exception as e:
        logger.error(f"Source adapter generation failed: {e}")
        raise

    total = 0
    for local_feed in local_feeds:
        created, _ = await get_or_create_generated_channel(local_feed)
        total += 1 if created else 0

    logger.info(f"added {total} channel(s) from generated feeds")
    return total


async def _maybe_add_episode(
    channel: models.Channel, episode: models.Episode
) -> models.Episode | None:
    # add a new episode only if it doesn't exist yet (if exists, return None)
    existing = await models.Episode.objects.get_or_none(url=episode.url)
    if existing is not None:
        logger.debug(f"ignoring episode {episode.id} as it already exists")
        return None
    else:
        logger.info(f"creating episode {episode.title} in channel {channel.id}")
        # this will perform episode's save
        await channel.episodes.add(episode)
        return episode


async def update_channel(
    channel: models.Channel, max_new_episodes: int | None = None
) -> int:
    """Read a channel feed and store all the new added episodes.
    Return the number of episodes added.
    """
    logger.info(f"updating channel {channel.title}")
    if channel.local_folder != "":  # channel from local folder
        episodes = local.read_local_episodes(channel)
    else:  # channel from rss feed
        episodes = feed.read_episodes(channel)
    new_added = 0
    for ep in episodes:
        added = await _maybe_add_episode(channel, ep)
        new_added += 1 if added else 0
        if max_new_episodes and new_added == max_new_episodes:
            break
    return new_added
