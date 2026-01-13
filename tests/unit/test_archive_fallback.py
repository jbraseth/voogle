# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for ArchiveFallback class."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from voogle.durability.archive import (
    ArchiveFallback,
    ArchiveSnapshot,
    ArchiveStatus,
    RateLimiter,
    WAYBACK_AVAILABILITY_API,
    WAYBACK_CDX_API,
    WAYBACK_WEB_BASE,
)

pytestmark = pytest.mark.unit


class TestArchiveSnapshot:
    """Tests for ArchiveSnapshot dataclass."""

    @pytest.mark.description("ArchiveSnapshot has correct default values")
    def test_default_values(self) -> None:
        snapshot = ArchiveSnapshot(url="https://example.com")
        assert snapshot.url == "https://example.com"
        assert snapshot.timestamp is None
        assert snapshot.archive_url is None
        assert snapshot.status == ArchiveStatus.NOT_FOUND
        assert snapshot.error is None

    @pytest.mark.description("ArchiveSnapshot captures all fields correctly")
    def test_all_fields(self) -> None:
        snapshot = ArchiveSnapshot(
            url="https://example.com/page",
            timestamp="20231015120000",
            archive_url="https://web.archive.org/web/20231015120000/https://example.com/page",
            status=ArchiveStatus.AVAILABLE,
            error=None,
        )
        assert snapshot.url == "https://example.com/page"
        assert snapshot.timestamp == "20231015120000"
        assert snapshot.status == ArchiveStatus.AVAILABLE

    @pytest.mark.description("captured_at parses timestamp correctly")
    def test_captured_at_parses_timestamp(self) -> None:
        snapshot = ArchiveSnapshot(
            url="https://example.com",
            timestamp="20231015120000",
        )
        captured = snapshot.captured_at
        assert captured is not None
        assert captured.year == 2023
        assert captured.month == 10
        assert captured.day == 15
        assert captured.hour == 12
        assert captured.minute == 0
        assert captured.second == 0

    @pytest.mark.description("captured_at returns None for invalid timestamp")
    def test_captured_at_invalid_timestamp(self) -> None:
        snapshot = ArchiveSnapshot(
            url="https://example.com",
            timestamp="invalid",
        )
        assert snapshot.captured_at is None

    @pytest.mark.description("captured_at returns None for missing timestamp")
    def test_captured_at_missing_timestamp(self) -> None:
        snapshot = ArchiveSnapshot(url="https://example.com")
        assert snapshot.captured_at is None


class TestArchiveStatus:
    """Tests for ArchiveStatus enum."""

    @pytest.mark.description("ArchiveStatus has all expected values")
    def test_all_values(self) -> None:
        assert ArchiveStatus.AVAILABLE.value == "available"
        assert ArchiveStatus.NOT_FOUND.value == "not_found"
        assert ArchiveStatus.RATE_LIMITED.value == "rate_limited"
        assert ArchiveStatus.TIMEOUT.value == "timeout"
        assert ArchiveStatus.ERROR.value == "error"


class TestRateLimiter:
    """Tests for RateLimiter class."""

    @pytest.mark.description("RateLimiter initializes with default interval")
    def test_default_interval(self) -> None:
        limiter = RateLimiter()
        assert limiter.min_interval == 1.0
        assert limiter.last_request_time == 0.0

    @pytest.mark.description("RateLimiter accepts custom interval")
    def test_custom_interval(self) -> None:
        limiter = RateLimiter(min_interval=2.5)
        assert limiter.min_interval == 2.5


class TestArchiveFallbackInit:
    """Tests for ArchiveFallback initialization."""

    @pytest.mark.description("ArchiveFallback initializes with default values")
    def test_default_init(self) -> None:
        fallback = ArchiveFallback()
        assert fallback._rate_limiter.min_interval == 1.0
        assert fallback._timeout == 30.0
        assert fallback._max_retries == 3

    @pytest.mark.description("ArchiveFallback accepts custom configuration")
    def test_custom_init(self) -> None:
        fallback = ArchiveFallback(
            min_request_interval=2.0,
            timeout=60.0,
            max_retries=5,
        )
        assert fallback._rate_limiter.min_interval == 2.0
        assert fallback._timeout == 60.0
        assert fallback._max_retries == 5

    @pytest.mark.description("ArchiveFallback has correct repr")
    def test_repr(self) -> None:
        fallback = ArchiveFallback()
        repr_str = repr(fallback)
        assert "ArchiveFallback" in repr_str
        assert "min_request_interval=1.0" in repr_str
        assert "timeout=30.0" in repr_str
        assert "max_retries=3" in repr_str


class TestArchiveFallbackCheckAvailability:
    """Tests for ArchiveFallback.check_availability method."""

    @pytest.mark.description("check_availability returns AVAILABLE for existing snapshot")
    @pytest.mark.asyncio
    async def test_available_snapshot(self) -> None:
        fallback = ArchiveFallback()

        mock_response = {
            "archived_snapshots": {
                "closest": {
                    "available": True,
                    "url": "https://web.archive.org/web/20231015120000/https://example.com",
                    "timestamp": "20231015120000",
                    "status": "200",
                }
            }
        }

        with patch.object(fallback, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = (mock_response, None)

            snapshot = await fallback.check_availability("https://example.com")

            assert snapshot.status == ArchiveStatus.AVAILABLE
            assert snapshot.timestamp == "20231015120000"
            assert snapshot.archive_url is not None
            mock_request.assert_called_once()

    @pytest.mark.description("check_availability returns NOT_FOUND when no snapshot exists")
    @pytest.mark.asyncio
    async def test_not_found(self) -> None:
        fallback = ArchiveFallback()

        mock_response = {"archived_snapshots": {}}

        with patch.object(fallback, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = (mock_response, None)

            snapshot = await fallback.check_availability("https://example.com/nonexistent")

            assert snapshot.status == ArchiveStatus.NOT_FOUND
            assert snapshot.archive_url is None

    @pytest.mark.description("check_availability returns ERROR on request failure")
    @pytest.mark.asyncio
    async def test_request_error(self) -> None:
        fallback = ArchiveFallback()

        with patch.object(fallback, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = (None, "Connection failed")

            snapshot = await fallback.check_availability("https://example.com")

            assert snapshot.status == ArchiveStatus.ERROR
            assert snapshot.error == "Connection failed"

    @pytest.mark.description("check_availability returns TIMEOUT on timeout error")
    @pytest.mark.asyncio
    async def test_timeout_error(self) -> None:
        fallback = ArchiveFallback()

        with patch.object(fallback, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = (None, "Request timed out after retries")

            snapshot = await fallback.check_availability("https://example.com")

            assert snapshot.status == ArchiveStatus.TIMEOUT


class TestArchiveFallbackGetClosestSnapshot:
    """Tests for ArchiveFallback.get_closest_snapshot method."""

    @pytest.mark.description("get_closest_snapshot returns snapshot for target date")
    @pytest.mark.asyncio
    async def test_closest_snapshot(self) -> None:
        fallback = ArchiveFallback()

        # CDX API response format: [headers, data_row, ...]
        mock_response = [
            ["urlkey", "timestamp", "original", "mimetype", "statuscode", "digest", "length"],
            ["com,example)/", "20231015120000", "https://example.com/", "text/html", "200", "ABC123", "1234"],
        ]

        with patch.object(fallback, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = (mock_response, None)

            target = datetime(2023, 10, 15)
            snapshot = await fallback.get_closest_snapshot("https://example.com", target)

            assert snapshot.status == ArchiveStatus.AVAILABLE
            assert snapshot.timestamp == "20231015120000"
            assert "web.archive.org" in snapshot.archive_url

    @pytest.mark.description("get_closest_snapshot returns NOT_FOUND for empty CDX response")
    @pytest.mark.asyncio
    async def test_empty_cdx_response(self) -> None:
        fallback = ArchiveFallback()

        # Empty response (only headers)
        mock_response = [
            ["urlkey", "timestamp", "original", "mimetype", "statuscode", "digest", "length"],
        ]

        with patch.object(fallback, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = (mock_response, None)

            snapshot = await fallback.get_closest_snapshot("https://example.com/missing")

            assert snapshot.status == ArchiveStatus.NOT_FOUND

    @pytest.mark.description("get_closest_snapshot uses current date when no target provided")
    @pytest.mark.asyncio
    async def test_default_target_date(self) -> None:
        fallback = ArchiveFallback()

        mock_response = [
            ["urlkey", "timestamp", "original", "mimetype", "statuscode", "digest", "length"],
            ["com,example)/", "20240101000000", "https://example.com/", "text/html", "200", "ABC123", "1234"],
        ]

        with patch.object(fallback, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = (mock_response, None)

            snapshot = await fallback.get_closest_snapshot("https://example.com")

            assert snapshot.status == ArchiveStatus.AVAILABLE
            mock_request.assert_called_once()
            # Verify that closest param was passed
            call_kwargs = mock_request.call_args
            assert "closest" in call_kwargs[1]["params"]


class TestArchiveFallbackRewriteToArchiveUrl:
    """Tests for ArchiveFallback.rewrite_to_archive_url method."""

    @pytest.mark.description("rewrite_to_archive_url creates correct archive URL")
    def test_basic_rewrite(self) -> None:
        fallback = ArchiveFallback()
        result = fallback.rewrite_to_archive_url(
            "https://example.com/page",
            "20231015120000",
        )
        assert result == "https://web.archive.org/web/20231015120000/https://example.com/page"

    @pytest.mark.description("rewrite_to_archive_url uses * for missing timestamp")
    def test_missing_timestamp(self) -> None:
        fallback = ArchiveFallback()
        result = fallback.rewrite_to_archive_url("https://example.com/page")
        assert result == "https://web.archive.org/web/*/https://example.com/page"

    @pytest.mark.description("rewrite_to_archive_url supports modifiers")
    def test_with_modifier(self) -> None:
        fallback = ArchiveFallback()
        result = fallback.rewrite_to_archive_url(
            "https://example.com/page",
            "20231015120000",
            modifier="id_",
        )
        assert result == "https://web.archive.org/web/20231015120000id_/https://example.com/page"

    @pytest.mark.description("rewrite_to_archive_url adds scheme if missing")
    def test_adds_scheme(self) -> None:
        fallback = ArchiveFallback()
        result = fallback.rewrite_to_archive_url(
            "example.com/page",
            "20231015120000",
        )
        assert "https://example.com" in result


class TestArchiveFallbackGetFallbackUrl:
    """Tests for ArchiveFallback.get_fallback_url method."""

    @pytest.mark.description("get_fallback_url returns archive URL when available")
    @pytest.mark.asyncio
    async def test_returns_url_when_available(self) -> None:
        fallback = ArchiveFallback()

        with patch.object(fallback, "check_availability", new_callable=AsyncMock) as mock_check:
            mock_check.return_value = ArchiveSnapshot(
                url="https://example.com",
                timestamp="20231015120000",
                archive_url="https://web.archive.org/web/20231015120000/https://example.com",
                status=ArchiveStatus.AVAILABLE,
            )

            result = await fallback.get_fallback_url("https://example.com")

            assert result == "https://web.archive.org/web/20231015120000/https://example.com"

    @pytest.mark.description("get_fallback_url returns None when not available")
    @pytest.mark.asyncio
    async def test_returns_none_when_not_available(self) -> None:
        fallback = ArchiveFallback()

        with patch.object(fallback, "check_availability", new_callable=AsyncMock) as mock_check:
            mock_check.return_value = ArchiveSnapshot(
                url="https://example.com",
                status=ArchiveStatus.NOT_FOUND,
            )

            result = await fallback.get_fallback_url("https://example.com")

            assert result is None


class TestArchiveFallbackBatchCheckAvailability:
    """Tests for ArchiveFallback.batch_check_availability method."""

    @pytest.mark.description("batch_check_availability checks multiple URLs")
    @pytest.mark.asyncio
    async def test_batch_check(self) -> None:
        fallback = ArchiveFallback()

        urls = [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/page3",
        ]

        with patch.object(fallback, "check_availability", new_callable=AsyncMock) as mock_check:
            mock_check.side_effect = [
                ArchiveSnapshot(url=urls[0], status=ArchiveStatus.AVAILABLE),
                ArchiveSnapshot(url=urls[1], status=ArchiveStatus.NOT_FOUND),
                ArchiveSnapshot(url=urls[2], status=ArchiveStatus.AVAILABLE),
            ]

            results = await fallback.batch_check_availability(urls)

            assert len(results) == 3
            assert results[0].status == ArchiveStatus.AVAILABLE
            assert results[1].status == ArchiveStatus.NOT_FOUND
            assert results[2].status == ArchiveStatus.AVAILABLE
            assert mock_check.call_count == 3

    @pytest.mark.description("batch_check_availability maintains URL order")
    @pytest.mark.asyncio
    async def test_maintains_order(self) -> None:
        fallback = ArchiveFallback()

        urls = ["https://a.com", "https://b.com", "https://c.com"]

        with patch.object(fallback, "check_availability", new_callable=AsyncMock) as mock_check:
            mock_check.side_effect = [
                ArchiveSnapshot(url=urls[0], status=ArchiveStatus.AVAILABLE),
                ArchiveSnapshot(url=urls[1], status=ArchiveStatus.AVAILABLE),
                ArchiveSnapshot(url=urls[2], status=ArchiveStatus.AVAILABLE),
            ]

            results = await fallback.batch_check_availability(urls)

            assert results[0].url == "https://a.com"
            assert results[1].url == "https://b.com"
            assert results[2].url == "https://c.com"


class TestConstants:
    """Tests for module constants."""

    @pytest.mark.description("API endpoint constants are valid URLs")
    def test_api_endpoints(self) -> None:
        assert WAYBACK_AVAILABILITY_API.startswith("https://")
        assert WAYBACK_CDX_API.startswith("https://")
        assert WAYBACK_WEB_BASE.startswith("https://")
        assert "archive.org" in WAYBACK_AVAILABILITY_API
        assert "archive.org" in WAYBACK_CDX_API
        assert "archive.org" in WAYBACK_WEB_BASE


class TestGracefulDegradation:
    """Tests for graceful degradation behavior."""

    @pytest.mark.description("Methods never raise exceptions")
    @pytest.mark.asyncio
    async def test_no_exceptions_on_error(self) -> None:
        fallback = ArchiveFallback()

        with patch.object(fallback, "_make_request", new_callable=AsyncMock) as mock_request:
            # Simulate various error conditions
            mock_request.return_value = (None, "Network error")

            # Should not raise, should return error status
            snapshot = await fallback.check_availability("https://example.com")
            assert snapshot.status in (ArchiveStatus.ERROR, ArchiveStatus.TIMEOUT)

            snapshot2 = await fallback.get_closest_snapshot("https://example.com")
            assert snapshot2.status in (ArchiveStatus.ERROR, ArchiveStatus.TIMEOUT)

    @pytest.mark.description("Empty response is handled gracefully")
    @pytest.mark.asyncio
    async def test_empty_response_handling(self) -> None:
        fallback = ArchiveFallback()

        with patch.object(fallback, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = (None, None)

            snapshot = await fallback.check_availability("https://example.com")
            assert snapshot.status == ArchiveStatus.ERROR
            assert snapshot.error == "Empty response"
