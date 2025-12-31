# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""URL health checking and refresh utilities.

Provides functions to detect broken episode media URLs and refresh them
from updated RSS feeds without losing transcription or embedding work.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Callable

import requests
from requests.exceptions import ConnectionError, RequestException, Timeout

from voogle import models
from voogle.collection import feed

logger = logging.getLogger(__name__)

# Constants
HEAD_TIMEOUT = 10  # seconds for HEAD requests
GET_TIMEOUT = 30  # seconds for full feed fetch
BATCH_DELAY = 0.5  # seconds between requests to avoid rate limiting


class URLStatus(Enum):
    """Status codes for URL health checks."""

    OK = "ok"  # URL responds 200
    NOT_FOUND = "not_found"  # 404
    FORBIDDEN = "forbidden"  # 403
    SERVER_ERROR = "server_error"  # 5xx
    TIMEOUT = "timeout"  # Request timed out
    CONNECTION_ERROR = "connection_error"  # Host unreachable
    REDIRECT_LOOP = "redirect_loop"  # Too many redirects
    INVALID_URL = "invalid_url"  # Malformed URL


@dataclass
class URLHealthResult:
    """Result of checking a single episode URL."""

    episode_pk: int
    episode_title: str
    url: str
    status: URLStatus
    http_code: int | None  # Actual HTTP status code if available
    error_message: str | None  # Human-readable error
    checked_at: datetime


@dataclass
class URLRefreshResult:
    """Result of attempting to find an updated URL for an episode."""

    episode_pk: int
    episode_title: str
    old_url: str
    new_url: str | None  # None if no match found in RSS
    match_method: str | None  # "guid" or "title"
    new_url_valid: bool  # True if new URL responds 200
    error_message: str | None  # Why refresh failed (if applicable)


def check_url(url: str, timeout: int = HEAD_TIMEOUT) -> tuple[URLStatus, int | None, str | None]:
    """Check URL health via HEAD request.

    Args:
        url: URL to check
        timeout: Request timeout in seconds

    Returns:
        Tuple of (status, http_code, error_message)
    """
    try:
        response = requests.head(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers={"User-Agent": "Voogle/1.0 (URL Health Check)"},
        )
        response.raise_for_status()
        return URLStatus.OK, response.status_code, None

    except Timeout:
        return URLStatus.TIMEOUT, None, "Request timed out"
    except ConnectionError:
        return URLStatus.CONNECTION_ERROR, None, "Host unreachable"
    except requests.exceptions.TooManyRedirects:
        return URLStatus.REDIRECT_LOOP, None, "Too many redirects"
    except requests.HTTPError as e:
        code = e.response.status_code if e.response is not None else None
        if code == 404:
            return URLStatus.NOT_FOUND, code, "URL not found"
        elif code == 403:
            return URLStatus.FORBIDDEN, code, "Access forbidden"
        elif code is not None and 500 <= code < 600:
            return URLStatus.SERVER_ERROR, code, f"Server error ({code})"
        else:
            return URLStatus.SERVER_ERROR, code, f"HTTP error ({code})"
    except RequestException as e:
        return URLStatus.INVALID_URL, None, str(e)


async def check_episode_url(episode: models.Episode) -> URLHealthResult:
    """Check the health of an episode's media URL.

    Args:
        episode: Episode to check

    Returns:
        URLHealthResult with status and error details
    """
    status, http_code, error_message = check_url(str(episode.url))
    return URLHealthResult(
        episode_pk=episode.pk,
        episode_title=str(episode.title),
        url=str(episode.url),
        status=status,
        http_code=http_code,
        error_message=error_message,
        checked_at=datetime.now(timezone.utc),
    )


async def check_channel_urls(
    channel: models.Channel,
    on_progress: Callable[[int, int], None] | None = None,
) -> list[URLHealthResult]:
    """Check all episode URLs for a channel with rate limiting.

    Args:
        channel: Channel to check
        on_progress: Callback(checked_count, total_count) for progress

    Returns:
        List of URLHealthResult for all episodes
    """
    episodes = await models.Episode.objects.filter(channel=channel).all()
    total = len(episodes)
    results: list[URLHealthResult] = []

    for i, episode in enumerate(episodes):
        result = await check_episode_url(episode)
        results.append(result)

        if on_progress:
            on_progress(i + 1, total)

        # Rate limiting
        if i < total - 1:
            await asyncio.sleep(BATCH_DELAY)

    return results


async def check_all_broken_urls(
    on_progress: Callable[[int, int], None] | None = None,
) -> list[URLHealthResult]:
    """Check all episode URLs across all channels.

    Args:
        on_progress: Callback(checked_count, total_count) for progress

    Returns:
        List of URLHealthResult for episodes with non-OK status only
    """
    episodes = await models.Episode.objects.all()
    total = len(episodes)
    broken: list[URLHealthResult] = []

    for i, episode in enumerate(episodes):
        result = await check_episode_url(episode)
        if result.status != URLStatus.OK:
            broken.append(result)

        if on_progress:
            on_progress(i + 1, total)

        # Rate limiting
        if i < total - 1:
            await asyncio.sleep(BATCH_DELAY)

    return broken


def find_episode_in_rss(
    episode: models.Episode,
    rss_items: list[dict],
) -> tuple[dict | None, str | None]:
    """Match an episode to an RSS item by GUID (preferred) or title (fallback).

    Args:
        episode: Episode to match
        rss_items: List of RSS item dicts from parsed feed

    Returns:
        Tuple of (matching_item, match_method) where match_method is "guid" or "title"
    """
    episode_guid = str(episode.guid)
    episode_title = str(episode.title).lower().strip()

    # First pass: match by GUID
    for item in rss_items:
        item_guid = feed._episode_guid(item.get("guid", ""))
        if item_guid == episode_guid:
            return item, "guid"

    # Second pass: match by title (fallback)
    for item in rss_items:
        item_title = (item.get("title") or "").lower().strip()
        if item_title == episode_title:
            logger.warning(f"Episode {episode.pk} matched by title, not GUID")
            return item, "title"

    return None, None


async def find_updated_url(
    episode: models.Episode,
    channel: models.Channel,
) -> URLRefreshResult:
    """Re-fetch channel RSS and find updated URL for episode.

    Strategy:
    1. Fetch current RSS feed for channel
    2. Match episode by GUID (preferred) or title (fallback)
    3. Compare enclosure URL to stored URL
    4. If different, validate new URL responds 200
    5. Return result with old URL, new URL, and validation status

    Args:
        episode: Episode to find updated URL for
        channel: Channel containing the episode

    Returns:
        URLRefreshResult with old/new URLs and validation status
    """
    old_url = str(episode.url)

    # Fetch current RSS feed
    feed_data = feed._read_channel_feed(str(channel.feed))
    if feed_data is None:
        return URLRefreshResult(
            episode_pk=episode.pk,
            episode_title=str(episode.title),
            old_url=old_url,
            new_url=None,
            match_method=None,
            new_url_valid=False,
            error_message="Failed to fetch RSS feed",
        )

    # Get RSS items
    try:
        rss_items = feed_data["rss"]["channel"]["item"]
        # Handle single item case (xmltodict returns dict instead of list)
        if isinstance(rss_items, dict):
            rss_items = [rss_items]
    except (KeyError, TypeError):
        return URLRefreshResult(
            episode_pk=episode.pk,
            episode_title=str(episode.title),
            old_url=old_url,
            new_url=None,
            match_method=None,
            new_url_valid=False,
            error_message="Invalid RSS feed structure",
        )

    # Find matching item
    matching_item, match_method = find_episode_in_rss(episode, rss_items)
    if matching_item is None:
        return URLRefreshResult(
            episode_pk=episode.pk,
            episode_title=str(episode.title),
            old_url=old_url,
            new_url=None,
            match_method=None,
            new_url_valid=False,
            error_message="Episode not found in current RSS feed",
        )

    # Extract new URL
    try:
        new_url = matching_item["enclosure"]["@url"]
    except (KeyError, TypeError):
        return URLRefreshResult(
            episode_pk=episode.pk,
            episode_title=str(episode.title),
            old_url=old_url,
            new_url=None,
            match_method=match_method,
            new_url_valid=False,
            error_message="No enclosure URL in RSS item",
        )

    # Check if URL changed
    if new_url == old_url:
        return URLRefreshResult(
            episode_pk=episode.pk,
            episode_title=str(episode.title),
            old_url=old_url,
            new_url=new_url,
            match_method=match_method,
            new_url_valid=True,
            error_message="URL unchanged",
        )

    # Validate new URL
    status, _, error = check_url(new_url)
    new_url_valid = status == URLStatus.OK

    return URLRefreshResult(
        episode_pk=episode.pk,
        episode_title=str(episode.title),
        old_url=old_url,
        new_url=new_url,
        match_method=match_method,
        new_url_valid=new_url_valid,
        error_message=None if new_url_valid else f"New URL not accessible: {error}",
    )


async def preview_channel_refresh(
    channel: models.Channel,
    broken_only: bool = True,
) -> list[URLRefreshResult]:
    """Preview URL refreshes for a channel without applying changes.

    Args:
        channel: Channel to check
        broken_only: If True, only check episodes with broken URLs

    Returns:
        List of URLRefreshResult showing potential changes
    """
    episodes = await models.Episode.objects.filter(channel=channel).all()
    results: list[URLRefreshResult] = []

    for episode in episodes:
        if broken_only:
            # Check if URL is broken first
            health = await check_episode_url(episode)
            if health.status == URLStatus.OK:
                continue
            await asyncio.sleep(BATCH_DELAY)

        # Find updated URL
        result = await find_updated_url(episode, channel)

        # Only include if URL actually changed and is different
        if result.new_url and result.new_url != result.old_url:
            results.append(result)

        await asyncio.sleep(BATCH_DELAY)

    return results


async def apply_url_refresh(
    episode: models.Episode,
    new_url: str,
) -> None:
    """Apply a URL refresh to an episode.

    - Validates new URL responds 200 before updating
    - Logs old URL for audit trail
    - Updates episode.url in database
    - Preserves transcription and embeddings status

    Args:
        episode: Episode to update
        new_url: New URL to set

    Raises:
        ValueError: If new URL is not accessible
    """
    old_url = str(episode.url)

    # Validate new URL is accessible
    status, _code, error = check_url(new_url)
    if status != URLStatus.OK:
        raise ValueError(f"New URL not accessible: {error}")

    # Log for audit trail
    logger.info(
        "Refreshing episode URL",
        extra={
            "episode_pk": episode.pk,
            "episode_title": str(episode.title),
            "old_url": old_url,
            "new_url": new_url,
        },
    )

    # Update database (preserves transcription/embeddings)
    await episode.update(url=new_url)


async def refresh_broken_urls(
    channel: models.Channel,
    dry_run: bool = True,
) -> list[URLRefreshResult]:
    """Refresh all broken URLs for a channel from its RSS feed.

    Args:
        channel: Channel to refresh
        dry_run: If True, preview only (don't apply changes)

    Returns:
        List of URLRefreshResult for all broken episodes
    """
    # Get preview of changes
    results = await preview_channel_refresh(channel, broken_only=True)

    if dry_run:
        return results

    # Apply changes for valid new URLs
    applied_results: list[URLRefreshResult] = []
    for result in results:
        if result.new_url and result.new_url_valid:
            try:
                episode = await models.Episode.objects.get(pk=result.episode_pk)
                await apply_url_refresh(episode, result.new_url)
                applied_results.append(result)
            except Exception as e:
                logger.error(
                    f"Failed to apply URL refresh for episode {result.episode_pk}: {e}"
                )
                # Update result with error
                applied_results.append(
                    URLRefreshResult(
                        episode_pk=result.episode_pk,
                        episode_title=result.episode_title,
                        old_url=result.old_url,
                        new_url=result.new_url,
                        match_method=result.match_method,
                        new_url_valid=False,
                        error_message=f"Failed to apply: {e}",
                    )
                )
        else:
            applied_results.append(result)

    return applied_results
