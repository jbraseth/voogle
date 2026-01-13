# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Archive.org Wayback Machine fallback for broken web locations.

Provides ArchiveFallback class for checking Wayback Machine availability,
retrieving closest snapshots, rewriting URLs to archive.org deep links,
and gracefully degrading when archives are unavailable.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)

# Wayback Machine API endpoints
WAYBACK_AVAILABILITY_API = "https://archive.org/wayback/available"
WAYBACK_CDX_API = "https://web.archive.org/cdx/search/cdx"
WAYBACK_WEB_BASE = "https://web.archive.org/web"

# Rate limiting defaults
DEFAULT_MIN_REQUEST_INTERVAL = 1.0  # seconds between requests
DEFAULT_TIMEOUT = 30.0  # seconds for API requests
DEFAULT_MAX_RETRIES = 3


class ArchiveStatus(Enum):
    """Status of an archive lookup."""

    AVAILABLE = "available"  # Snapshot exists and is accessible
    NOT_FOUND = "not_found"  # No snapshot in archive
    RATE_LIMITED = "rate_limited"  # Hit rate limit, try again later
    TIMEOUT = "timeout"  # Request timed out
    ERROR = "error"  # Other error occurred


@dataclass
class ArchiveSnapshot:
    """Information about an archived snapshot.

    Attributes:
        url: The original URL that was archived.
        timestamp: When the snapshot was captured (YYYYMMDDHHMMSS format).
        archive_url: The full archive.org URL to access this snapshot.
        status: The status of the lookup.
        error: Error message if status is ERROR.
        captured_at: Parsed datetime of the snapshot capture.
    """

    url: str
    timestamp: str | None = None
    archive_url: str | None = None
    status: ArchiveStatus = ArchiveStatus.NOT_FOUND
    error: str | None = None

    @property
    def captured_at(self) -> datetime | None:
        """Parse timestamp into datetime."""
        if not self.timestamp:
            return None
        try:
            return datetime.strptime(self.timestamp, "%Y%m%d%H%M%S")
        except ValueError:
            return None


@dataclass
class RateLimiter:
    """Simple rate limiter for API requests.

    Attributes:
        min_interval: Minimum seconds between requests.
        last_request_time: Timestamp of last request.
    """

    min_interval: float = DEFAULT_MIN_REQUEST_INTERVAL
    last_request_time: float = field(default=0.0)

    async def wait(self) -> None:
        """Wait until enough time has passed since last request."""
        now = time.monotonic()
        elapsed = now - self.last_request_time
        if elapsed < self.min_interval:
            await asyncio.sleep(self.min_interval - elapsed)
        self.last_request_time = time.monotonic()


class ArchiveFallback:
    """Wayback Machine fallback for broken web locations.

    Provides methods to check if archived versions exist, retrieve the
    closest snapshot to a given date, and rewrite URLs to archive.org
    deep links.

    Example:
        >>> fallback = ArchiveFallback()
        >>> snapshot = await fallback.check_availability("https://example.com/page")
        >>> if snapshot.status == ArchiveStatus.AVAILABLE:
        ...     print(f"Archived at: {snapshot.archive_url}")

    Rate Limiting:
        The Wayback Machine has rate limits. This class implements client-side
        rate limiting to avoid hitting those limits. By default, requests are
        spaced at least 1 second apart.

    Graceful Degradation:
        All methods handle errors gracefully and never raise exceptions.
        Check the status field of returned ArchiveSnapshot to determine
        if the operation succeeded.
    """

    def __init__(
        self,
        min_request_interval: float = DEFAULT_MIN_REQUEST_INTERVAL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        """Initialize the archive fallback.

        Args:
            min_request_interval: Minimum seconds between API requests.
            timeout: Timeout for HTTP requests in seconds.
            max_retries: Maximum number of retry attempts for failed requests.
        """
        self._rate_limiter = RateLimiter(min_interval=min_request_interval)
        self._timeout = timeout
        self._max_retries = max_retries

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"ArchiveFallback("
            f"min_request_interval={self._rate_limiter.min_interval}, "
            f"timeout={self._timeout}, "
            f"max_retries={self._max_retries})"
        )

    async def _make_request(
        self,
        url: str,
        params: dict[str, Any] | None = None,
    ) -> tuple[Any, str | None]:
        """Make an HTTP GET request with rate limiting and retries.

        Args:
            url: URL to request.
            params: Query parameters.

        Returns:
            Tuple of (json_response, error_message). Response can be dict or list.
        """
        await self._rate_limiter.wait()

        for attempt in range(self._max_retries):
            try:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    response = await client.get(url, params=params)

                    # Handle rate limiting
                    if response.status_code == 429:
                        wait_time = float(
                            response.headers.get("Retry-After", str(2**attempt))
                        )
                        logger.warning(
                            "Rate limited by archive.org, waiting %s seconds",
                            wait_time,
                        )
                        await asyncio.sleep(wait_time)
                        continue

                    response.raise_for_status()
                    return response.json(), None

            except httpx.TimeoutException:
                logger.warning(
                    "Request timeout (attempt %d/%d): %s",
                    attempt + 1,
                    self._max_retries,
                    url,
                )
                if attempt < self._max_retries - 1:
                    await asyncio.sleep(2**attempt)
                continue

            except httpx.HTTPStatusError as e:
                logger.error("HTTP error: %s", e)
                return None, str(e)

            except Exception as e:
                logger.error("Request failed: %s", e)
                return None, str(e)

        return None, "Request timed out after retries"

    async def check_availability(self, url: str) -> ArchiveSnapshot:
        """Check if an archived version of a URL exists.

        Uses the Wayback Availability API to check if any snapshot exists.

        Args:
            url: The URL to check.

        Returns:
            ArchiveSnapshot with availability status.
        """
        logger.debug("Checking archive availability for: %s", url)

        data, error = await self._make_request(
            WAYBACK_AVAILABILITY_API,
            params={"url": url},
        )

        if error:
            if "timed out" in error.lower():
                return ArchiveSnapshot(url=url, status=ArchiveStatus.TIMEOUT, error=error)
            return ArchiveSnapshot(url=url, status=ArchiveStatus.ERROR, error=error)

        if data is None:
            return ArchiveSnapshot(
                url=url, status=ArchiveStatus.ERROR, error="Empty response"
            )

        # Parse availability response
        try:
            archived = data.get("archived_snapshots", {})
            closest = archived.get("closest", {})

            if closest and closest.get("available"):
                timestamp = closest.get("timestamp", "")
                archive_url = closest.get("url", "")

                return ArchiveSnapshot(
                    url=url,
                    timestamp=timestamp,
                    archive_url=archive_url,
                    status=ArchiveStatus.AVAILABLE,
                )
            return ArchiveSnapshot(url=url, status=ArchiveStatus.NOT_FOUND)

        except Exception as e:
            logger.error("Failed to parse availability response: %s", e)
            return ArchiveSnapshot(url=url, status=ArchiveStatus.ERROR, error=str(e))

    async def get_closest_snapshot(
        self,
        url: str,
        target_date: datetime | None = None,
    ) -> ArchiveSnapshot:
        """Get the closest archived snapshot to a target date.

        If no target date is provided, returns the most recent snapshot.

        Args:
            url: The URL to look up.
            target_date: Target date for the snapshot. Defaults to now.

        Returns:
            ArchiveSnapshot with the closest available snapshot.
        """
        logger.debug("Getting closest snapshot for: %s", url)

        # Format target date for Wayback API
        if target_date is None:
            target_date = datetime.now()
        timestamp = target_date.strftime("%Y%m%d")

        # Use CDX API for more precise control
        data, error = await self._make_request(
            WAYBACK_CDX_API,
            params={
                "url": url,
                "closest": timestamp,
                "sort": "closest",
                "limit": 1,
                "output": "json",
            },
        )

        if error:
            if "timed out" in error.lower():
                return ArchiveSnapshot(url=url, status=ArchiveStatus.TIMEOUT, error=error)
            return ArchiveSnapshot(url=url, status=ArchiveStatus.ERROR, error=error)

        if data is None or not isinstance(data, list) or len(data) < 2:
            return ArchiveSnapshot(url=url, status=ArchiveStatus.NOT_FOUND)

        try:
            # CDX returns [header_row, data_row, ...]
            # Headers: ["urlkey","timestamp","original","mimetype","statuscode","digest","length"]
            row = list(data[1])  # First data row, cast to list for indexing
            snapshot_timestamp = str(row[1])
            original_url = str(row[2])

            archive_url = self.rewrite_to_archive_url(original_url, snapshot_timestamp)

            return ArchiveSnapshot(
                url=url,
                timestamp=snapshot_timestamp,
                archive_url=archive_url,
                status=ArchiveStatus.AVAILABLE,
            )

        except (IndexError, KeyError, TypeError) as e:
            logger.error("Failed to parse CDX response: %s", e)
            return ArchiveSnapshot(url=url, status=ArchiveStatus.ERROR, error=str(e))

    def rewrite_to_archive_url(
        self,
        url: str,
        timestamp: str | None = None,
        modifier: str = "",
    ) -> str:
        """Rewrite a URL to its archive.org deep link.

        Args:
            url: The original URL.
            timestamp: Wayback timestamp (YYYYMMDDHHMMSS). If None, uses "*" for latest.
            modifier: URL modifier (e.g., "id_" for original, "im_" for image).

        Returns:
            The archive.org URL.

        Example:
            >>> fallback = ArchiveFallback()
            >>> fallback.rewrite_to_archive_url("https://example.com", "20231015120000")
            'https://web.archive.org/web/20231015120000/https://example.com'
        """
        ts = timestamp or "*"
        # Normalize URL encoding
        parsed = urlparse(url)
        if not parsed.scheme:
            url = f"https://{url}"

        return f"{WAYBACK_WEB_BASE}/{ts}{modifier}/{url}"

    async def get_fallback_url(self, url: str) -> str | None:
        """Get an archive.org fallback URL if available.

        Convenience method that checks availability and returns the archive
        URL if found, or None otherwise.

        Args:
            url: The original URL that may be broken.

        Returns:
            Archive.org URL if available, None otherwise.
        """
        snapshot = await self.check_availability(url)
        if snapshot.status == ArchiveStatus.AVAILABLE:
            return snapshot.archive_url
        return None

    async def batch_check_availability(
        self,
        urls: list[str],
    ) -> list[ArchiveSnapshot]:
        """Check availability for multiple URLs with rate limiting.

        Args:
            urls: List of URLs to check.

        Returns:
            List of ArchiveSnapshot results in the same order as input.
        """
        results: list[ArchiveSnapshot] = []
        for url in urls:
            result = await self.check_availability(url)
            results.append(result)
        return results
