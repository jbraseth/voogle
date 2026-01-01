# Copyright (c) 2022-2024 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Utilities to parse podcasts RSS feeds

Functions from this module return Channel or Episode objects, but they
don't interact with the database.
"""

from __future__ import annotations

import logging
import xml.parsers.expat
from dataclasses import dataclass
from datetime import datetime

import dateutil.parser
import requests
import xmltodict

from voogle import models

IGNORE_EPISODES_TYPES: list[str] = ["bonus", "trailer"]

# MIME types that indicate a resource (not an episode)
RESOURCE_MIME_TYPES: set[str] = {"application/pdf"}

LANGUAGES_MAP = {
    "es-ES": "es",
    "en-US": "en",
    "en-es": "es",
    "en-us": "en",
}
logger = logging.getLogger(__name__)


@dataclass
class ResourceData:
    """Data for a resource extracted from an RSS feed.

    This is not a database model - just a container for parsed data.
    """

    guid: str
    title: str
    description: str
    original_url: str
    mime_type: str
    date: datetime | None = None


def _is_resource_item(item: dict) -> bool:
    """Check if an RSS item is a resource (PDF, etc.) rather than an episode."""
    enclosure = item.get("enclosure", {})
    if not enclosure:
        return False
    mime_type = enclosure.get("@type", "")
    return mime_type in RESOURCE_MIME_TYPES


def _channel_img(channel_info: dict) -> str:
    image = channel_info.get("image", None)
    if not image:
        image = channel_info["itunes:image"]
        return image["@href"]
    if isinstance(image, list):
        image = image[0]
    return image["url"]


def _episode_date(date: str) -> datetime:
    return dateutil.parser.parse(date)


def _episode_duration(duration: str | None) -> int:
    hours, minutes, secs = "0", "0", "0"
    if not duration:
        return -1
    if ":" in duration:
        parts = duration.split(":")
        if len(parts) == 3:
            hours, minutes, secs = parts
        elif len(parts) == 2:
            minutes, secs = parts
        return int(hours) * 3600 + int(minutes) * 60 + int(secs)
    return int(duration)


def _episode_guid(guid: dict | str) -> str:
    return guid["#text"] if isinstance(guid, dict) else guid


def _normalize_items(channel_info: dict) -> list[dict]:
    """Normalize RSS items to a list.

    xmltodict returns a dict for single <item>, list for multiple.
    This normalizes both cases to always return a list.
    """
    items = channel_info.get("item", [])
    if isinstance(items, dict):
        return [items]
    return items


def _read_channel_feed(url: str) -> dict | None:
    try:
        channel_info = xmltodict.parse(requests.get(url).content)
    except xml.parsers.expat.ExpatError:
        channel_info = None
    return channel_info


def read_channel(url: str, language: str | None = None) -> models.Channel | None:
    """Read a feed url and return a channel object (not stored yet in
    db). This function won't read channel episodes, just some basic
    metadata about channels.
    """
    logger.info(f"reading channel from url: {url}")
    if parsed_channel := _read_channel_feed(url):
        channel_info = parsed_channel["rss"]["channel"]
        language = language or channel_info["language"].lower()
        return models.Channel(
            kind=models.ChannelKind.podcast.value,
            title=channel_info["title"],
            description=channel_info["description"],
            language=LANGUAGES_MAP.get(language, ""),
            url=channel_info["link"],
            feed=url,
            local_folder="",
            image=_channel_img(channel_info),
        )


def read_episodes(channel: models.Channel) -> list[models.Episode]:
    """Return a list with all the episodes (not stored yet in db) from
    a given channel.

    Note: Resource items (PDFs, etc.) are skipped. Use read_resources() for those.
    """
    logger.info(f"reading episodes from channel: {channel.id}: {channel.title}")
    feed = _read_channel_feed(str(channel.feed))
    if feed is None:
        return []
    episodes: list[models.Episode] = []
    for ep in _normalize_items(feed["rss"]["channel"]):
        # Skip resource items (PDFs) - those are handled by read_resources()
        if _is_resource_item(ep):
            continue
        if ep.get("itunes:episodeType", None) not in ["bonus", "trailer"]:
            title = ep.get("title", None)
            if title:
                episode = models.Episode(
                    title=title,
                    guid=_episode_guid(ep["guid"]),
                    description=ep.get("description", "") or "",
                    date=_episode_date(ep["pubDate"]),
                    url=ep["enclosure"]["@url"],
                    episode=int(ep.get("itunes:episode", -1)),
                    season=int(ep.get("itunes:season", -1)),
                    duration=_episode_duration(ep.get("itunes:duration", None)),
                    transcribed=False,
                    embeddings=False,
                )
                episodes.append(episode)
            else:
                logger.warning(f"episode without title: {ep} won't be stored")
    logger.info(f"{len(episodes)} episodes parsed from channel {channel.title}")
    return episodes


def read_resources(channel: models.Channel) -> list[ResourceData]:
    """Return a list of resources (PDFs, etc.) from a channel's feed.

    Resources are non-audio items like PDFs that should be stored
    separately from episodes.
    """
    logger.info(f"reading resources from channel: {channel.id}: {channel.title}")
    feed = _read_channel_feed(str(channel.feed))
    if feed is None:
        return []

    resources: list[ResourceData] = []
    for item in _normalize_items(feed["rss"]["channel"]):
        if not _is_resource_item(item):
            continue

        title = item.get("title")
        if not title:
            logger.warning(f"resource without title: {item} won't be stored")
            continue

        enclosure = item.get("enclosure", {})
        resource = ResourceData(
            guid=_episode_guid(item.get("guid", title)),
            title=title,
            description=item.get("description", "") or "",
            original_url=enclosure.get("@url", ""),
            mime_type=enclosure.get("@type", "application/pdf"),
            date=_episode_date(item["pubDate"]) if item.get("pubDate") else None,
        )
        resources.append(resource)

    logger.info(f"{len(resources)} resources parsed from channel {channel.title}")
    return resources
