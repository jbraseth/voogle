# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for LocationValidator class."""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from voogle.core.fragment import ContentType
from voogle.core.location import (
    ElementSelectorLocation,
    PageBboxLocation,
    SlideLocation,
    TimestampLocation,
)
from voogle.durability.archive import ArchiveSnapshot, ArchiveStatus
from voogle.durability.validation import (
    BrokenLocationReport,
    LocationStatus,
    LocationValidator,
    ValidationConfig,
    ValidationResult,
    run_scheduled_validation,
)

pytestmark = pytest.mark.unit


def _utcnow() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class TestLocationStatus:
    """Tests for LocationStatus enum."""

    @pytest.mark.description("LocationStatus has all expected values")
    def test_all_values(self) -> None:
        assert LocationStatus.VALID.value == "valid"
        assert LocationStatus.STALE.value == "stale"
        assert LocationStatus.BROKEN.value == "broken"


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    @pytest.mark.description("ValidationResult has correct default values")
    def test_default_values(self) -> None:
        now = _utcnow()
        result = ValidationResult(
            location_id="loc_123",
            status=LocationStatus.VALID,
            last_validated_at=now,
        )
        assert result.location_id == "loc_123"
        assert result.status == LocationStatus.VALID
        assert result.error is None
        assert result.fallback_url is None
        assert result.details == {}

    @pytest.mark.description("ValidationResult captures all fields correctly")
    def test_all_fields(self) -> None:
        now = _utcnow()
        result = ValidationResult(
            location_id="loc_123",
            status=LocationStatus.BROKEN,
            last_validated_at=now,
            error="HTTP 404",
            fallback_url="https://web.archive.org/web/123/https://example.com",
            details={"status_code": 404},
        )
        assert result.location_id == "loc_123"
        assert result.status == LocationStatus.BROKEN
        assert result.error == "HTTP 404"
        assert result.fallback_url is not None
        assert result.details["status_code"] == 404

    @pytest.mark.description("ValidationResult serializes to dict correctly")
    def test_to_dict(self) -> None:
        now = _utcnow()
        result = ValidationResult(
            location_id="loc_123",
            status=LocationStatus.VALID,
            last_validated_at=now,
            details={"key": "value"},
        )
        data = result.to_dict()
        assert data["location_id"] == "loc_123"
        assert data["status"] == "valid"
        assert data["last_validated_at"] == now.isoformat()
        assert data["error"] is None
        assert data["fallback_url"] is None
        assert data["details"] == {"key": "value"}


class TestBrokenLocationReport:
    """Tests for BrokenLocationReport dataclass."""

    @pytest.mark.description("BrokenLocationReport has correct default values")
    def test_default_values(self) -> None:
        now = _utcnow()
        report = BrokenLocationReport(
            location_id="loc_123",
            url="https://example.com/broken",
            content_type=ContentType.AUDIO,
            error="HTTP 404",
            first_detected_at=now,
            last_checked_at=now,
        )
        assert report.location_id == "loc_123"
        assert report.check_count == 1
        assert report.recovery_attempted is False
        assert report.recovered is False

    @pytest.mark.description("BrokenLocationReport serializes to dict correctly")
    def test_to_dict(self) -> None:
        now = _utcnow()
        report = BrokenLocationReport(
            location_id="loc_123",
            url="https://example.com/broken",
            content_type=ContentType.VIDEO,
            error="Connection refused",
            first_detected_at=now,
            last_checked_at=now,
            check_count=5,
            recovery_attempted=True,
            recovered=True,
        )
        data = report.to_dict()
        assert data["location_id"] == "loc_123"
        assert data["content_type"] == "video"
        assert data["check_count"] == 5
        assert data["recovered"] is True


class TestValidationConfig:
    """Tests for ValidationConfig dataclass."""

    @pytest.mark.description("ValidationConfig has correct default values")
    def test_default_values(self) -> None:
        config = ValidationConfig()
        assert config.stale_threshold_hours == 24
        assert config.http_timeout == 30.0
        assert config.max_retries == 3
        assert config.enable_archive_fallback is True
        assert config.batch_size == 10
        assert config.retry_backoff_base == 2.0

    @pytest.mark.description("ValidationConfig accepts custom values")
    def test_custom_values(self) -> None:
        config = ValidationConfig(
            stale_threshold_hours=48,
            http_timeout=60.0,
            max_retries=5,
            enable_archive_fallback=False,
            batch_size=20,
        )
        assert config.stale_threshold_hours == 48
        assert config.http_timeout == 60.0
        assert config.max_retries == 5
        assert config.enable_archive_fallback is False
        assert config.batch_size == 20


class TestLocationValidatorInit:
    """Tests for LocationValidator initialization."""

    @pytest.mark.description("LocationValidator initializes with default config")
    def test_default_init(self) -> None:
        validator = LocationValidator()
        assert validator._config.stale_threshold_hours == 24
        assert validator._config.http_timeout == 30.0

    @pytest.mark.description("LocationValidator accepts custom config")
    def test_custom_init(self) -> None:
        config = ValidationConfig(stale_threshold_hours=12)
        validator = LocationValidator(config=config)
        assert validator._config.stale_threshold_hours == 12

    @pytest.mark.description("LocationValidator has correct str representation")
    def test_str(self) -> None:
        validator = LocationValidator()
        assert "LocationValidator" in str(validator)
        assert "24h" in str(validator)

    @pytest.mark.description("LocationValidator has correct repr")
    def test_repr(self) -> None:
        validator = LocationValidator()
        assert "LocationValidator" in repr(validator)
        assert "config" in repr(validator)


class TestLocationValidatorValidateLocation:
    """Tests for LocationValidator.validate_location method."""

    @pytest.mark.description("validate_location returns VALID for accessible URL")
    @pytest.mark.asyncio
    async def test_valid_url(self) -> None:
        validator = LocationValidator()

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "audio/mpeg"}

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.head = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            result = await validator.validate_location(
                location_id="loc_123",
                url="https://example.com/audio.mp3",
                content_type=ContentType.AUDIO,
            )

            assert result.status == LocationStatus.VALID
            assert result.error is None

    @pytest.mark.description("validate_location returns BROKEN for 404 error")
    @pytest.mark.asyncio
    async def test_broken_url_404(self) -> None:
        validator = LocationValidator(
            config=ValidationConfig(enable_archive_fallback=False)
        )

        mock_response = AsyncMock()
        mock_response.status_code = 404
        mock_response.headers = {}

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.head = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            result = await validator.validate_location(
                location_id="loc_123",
                url="https://example.com/missing.mp3",
                content_type=ContentType.AUDIO,
            )

            assert result.status == LocationStatus.BROKEN
            assert "404" in result.error

    @pytest.mark.description("validate_location returns BROKEN on timeout")
    @pytest.mark.asyncio
    async def test_timeout(self) -> None:
        validator = LocationValidator(
            config=ValidationConfig(enable_archive_fallback=False)
        )

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.head = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            result = await validator.validate_location(
                location_id="loc_123",
                url="https://slow.example.com/audio.mp3",
                content_type=ContentType.AUDIO,
            )

            assert result.status == LocationStatus.BROKEN
            assert "timed out" in result.error.lower()

    @pytest.mark.description("validate_location adds timestamp info for audio")
    @pytest.mark.asyncio
    async def test_audio_with_timestamp(self) -> None:
        validator = LocationValidator()

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "audio/mpeg"}

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.head = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            location = TimestampLocation(start_time=30.0, end_time=60.0)
            result = await validator.validate_location(
                location_id="loc_123",
                url="https://example.com/audio.mp3",
                content_type=ContentType.AUDIO,
                location=location,
            )

            assert result.status == LocationStatus.VALID
            assert result.details.get("timestamp_checked") is True
            assert result.details.get("start_time") == 30.0

    @pytest.mark.description("validate_location adds page info for documents")
    @pytest.mark.asyncio
    async def test_document_with_page(self) -> None:
        validator = LocationValidator()

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/pdf"}

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.head = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            location = PageBboxLocation(page=5)
            result = await validator.validate_location(
                location_id="loc_123",
                url="https://example.com/document.pdf",
                content_type=ContentType.DOCUMENT,
                location=location,
            )

            assert result.status == LocationStatus.VALID
            assert result.details.get("page_checked") is True
            assert result.details.get("page") == 5

    @pytest.mark.description("validate_location handles email:// scheme")
    @pytest.mark.asyncio
    async def test_email_scheme(self) -> None:
        validator = LocationValidator()

        result = await validator.validate_location(
            location_id="loc_123",
            url="email://message-id-123",
            content_type=ContentType.EMAIL,
        )

        assert result.status == LocationStatus.VALID
        assert result.details.get("reference_only") is True


class TestLocationValidatorAutoRefresh:
    """Tests for auto-refresh and fallback functionality."""

    @pytest.mark.description("validate_location attempts auto-refresh on broken URL")
    @pytest.mark.asyncio
    async def test_auto_refresh_on_broken(self) -> None:
        validator = LocationValidator()

        mock_response = AsyncMock()
        mock_response.status_code = 404
        mock_response.headers = {}

        mock_snapshot = ArchiveSnapshot(
            url="https://example.com/broken",
            timestamp="20231015120000",
            archive_url="https://web.archive.org/web/20231015120000/https://example.com/broken",
            status=ArchiveStatus.AVAILABLE,
        )

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.head = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            with patch.object(
                validator.archive_fallback, "check_availability", new_callable=AsyncMock
            ) as mock_archive:
                mock_archive.return_value = mock_snapshot

                result = await validator.validate_location(
                    location_id="loc_123",
                    url="https://example.com/broken",
                    content_type=ContentType.TEXT,
                )

                assert result.status == LocationStatus.VALID
                assert result.fallback_url is not None
                assert "archive.org" in result.fallback_url
                assert result.details.get("recovered_from") == "archive.org"

    @pytest.mark.description("validate_location respects enable_archive_fallback=False")
    @pytest.mark.asyncio
    async def test_no_auto_refresh_when_disabled(self) -> None:
        config = ValidationConfig(enable_archive_fallback=False)
        validator = LocationValidator(config=config)

        mock_response = AsyncMock()
        mock_response.status_code = 404
        mock_response.headers = {}

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.head = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            result = await validator.validate_location(
                location_id="loc_123",
                url="https://example.com/broken",
                content_type=ContentType.TEXT,
            )

            assert result.status == LocationStatus.BROKEN
            assert result.fallback_url is None


class TestLocationValidatorBrokenReports:
    """Tests for broken location reporting."""

    @pytest.mark.description("Broken locations are tracked in reports")
    @pytest.mark.asyncio
    async def test_broken_location_tracked(self) -> None:
        validator = LocationValidator(
            config=ValidationConfig(enable_archive_fallback=False)
        )

        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_response.headers = {}

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.head = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            await validator.validate_location(
                location_id="loc_123",
                url="https://example.com/error",
                content_type=ContentType.VIDEO,
            )

            reports = validator.get_broken_reports()
            assert len(reports) == 1
            assert reports[0].location_id == "loc_123"
            assert reports[0].content_type == ContentType.VIDEO

    @pytest.mark.description("Multiple checks increment check_count")
    @pytest.mark.asyncio
    async def test_check_count_increments(self) -> None:
        validator = LocationValidator(
            config=ValidationConfig(enable_archive_fallback=False)
        )

        mock_response = AsyncMock()
        mock_response.status_code = 503
        mock_response.headers = {}

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.head = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            # Check multiple times
            for _ in range(3):
                await validator.validate_location(
                    location_id="loc_123",
                    url="https://example.com/error",
                    content_type=ContentType.VIDEO,
                )

            report = validator.get_broken_report("loc_123")
            assert report is not None
            assert report.check_count == 3

    @pytest.mark.description("clear_broken_reports clears all reports")
    @pytest.mark.asyncio
    async def test_clear_reports(self) -> None:
        validator = LocationValidator(
            config=ValidationConfig(enable_archive_fallback=False)
        )

        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_response.headers = {}

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.head = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            await validator.validate_location(
                location_id="loc_123",
                url="https://example.com/error",
                content_type=ContentType.VIDEO,
            )

            assert len(validator.get_broken_reports()) == 1

            cleared = validator.clear_broken_reports()
            assert cleared == 1
            assert len(validator.get_broken_reports()) == 0


class TestLocationValidatorStaleDetection:
    """Tests for stale location detection."""

    @pytest.mark.description("is_stale returns True for old validations")
    def test_is_stale_true(self) -> None:
        config = ValidationConfig(stale_threshold_hours=24)
        validator = LocationValidator(config=config)

        old_time = _utcnow() - timedelta(hours=25)
        assert validator.is_stale(old_time) is True

    @pytest.mark.description("is_stale returns False for recent validations")
    def test_is_stale_false(self) -> None:
        config = ValidationConfig(stale_threshold_hours=24)
        validator = LocationValidator(config=config)

        recent_time = _utcnow() - timedelta(hours=1)
        assert validator.is_stale(recent_time) is False

    @pytest.mark.description("get_status_for_age returns STALE for None")
    def test_status_for_none(self) -> None:
        validator = LocationValidator()
        assert validator.get_status_for_age(None) == LocationStatus.STALE

    @pytest.mark.description("get_status_for_age returns correct status")
    def test_status_for_age(self) -> None:
        config = ValidationConfig(stale_threshold_hours=24)
        validator = LocationValidator(config=config)

        recent = _utcnow() - timedelta(hours=1)
        old = _utcnow() - timedelta(hours=25)

        assert validator.get_status_for_age(recent) == LocationStatus.VALID
        assert validator.get_status_for_age(old) == LocationStatus.STALE


class TestLocationValidatorBatchValidation:
    """Tests for batch validation."""

    @pytest.mark.description("validate_batch validates multiple locations")
    @pytest.mark.asyncio
    async def test_batch_validation(self) -> None:
        validator = LocationValidator()

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "text/html"}

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.head = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            locations = [
                {"location_id": "loc_1", "url": "https://example.com/1", "content_type": ContentType.TEXT},
                {"location_id": "loc_2", "url": "https://example.com/2", "content_type": ContentType.TEXT},
                {"location_id": "loc_3", "url": "https://example.com/3", "content_type": ContentType.TEXT},
            ]

            results = await validator.validate_batch(locations)

            assert len(results) == 3
            assert all(r.status == LocationStatus.VALID for r in results)


class TestLocationValidatorCache:
    """Tests for validation caching."""

    @pytest.mark.description("Validated results are cached")
    @pytest.mark.asyncio
    async def test_caching(self) -> None:
        validator = LocationValidator()

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "audio/mpeg"}

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.head = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            await validator.validate_location(
                location_id="loc_123",
                url="https://example.com/audio.mp3",
                content_type=ContentType.AUDIO,
            )

            cached = validator.get_cached_result("loc_123")
            assert cached is not None
            assert cached.status == LocationStatus.VALID

    @pytest.mark.description("clear_cache clears all cached results")
    @pytest.mark.asyncio
    async def test_clear_cache(self) -> None:
        validator = LocationValidator()

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "audio/mpeg"}

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.head = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            await validator.validate_location(
                location_id="loc_123",
                url="https://example.com/audio.mp3",
                content_type=ContentType.AUDIO,
            )

            assert validator.get_cached_result("loc_123") is not None

            cleared = validator.clear_cache()
            assert cleared == 1
            assert validator.get_cached_result("loc_123") is None


class TestLocationValidatorStats:
    """Tests for validation statistics."""

    @pytest.mark.description("get_validation_stats returns correct counts")
    @pytest.mark.asyncio
    async def test_validation_stats(self) -> None:
        validator = LocationValidator(
            config=ValidationConfig(enable_archive_fallback=False)
        )

        # Create responses for different scenarios
        success_response = AsyncMock()
        success_response.status_code = 200
        success_response.headers = {"content-type": "text/html"}

        error_response = AsyncMock()
        error_response.status_code = 500
        error_response.headers = {}

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            call_count = [0]

            def mock_head(*args: object, **kwargs: object) -> AsyncMock:
                _ = args, kwargs  # Suppress unused warnings
                call_count[0] += 1
                if call_count[0] <= 2:
                    return success_response
                return error_response

            mock_instance.head = AsyncMock(side_effect=mock_head)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            # Validate some locations
            await validator.validate_location("loc_1", "https://example.com/1", ContentType.TEXT)
            await validator.validate_location("loc_2", "https://example.com/2", ContentType.TEXT)
            await validator.validate_location("loc_3", "https://example.com/3", ContentType.TEXT)

            stats = validator.get_validation_stats()
            assert stats["total_cached"] == 3
            assert stats["valid"] == 2
            assert stats["broken"] == 1
            assert stats["broken_reports"] == 1


class TestRunScheduledValidation:
    """Tests for run_scheduled_validation function."""

    @pytest.mark.description("run_scheduled_validation validates all locations")
    @pytest.mark.asyncio
    async def test_scheduled_validation(self) -> None:
        validator = LocationValidator()

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "text/html"}

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.head = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            locations = [
                {"location_id": "loc_1", "url": "https://example.com/1", "content_type": ContentType.TEXT},
                {"location_id": "loc_2", "url": "https://example.com/2", "content_type": ContentType.TEXT},
            ]

            summary = await run_scheduled_validation(validator, locations)

            assert summary["total"] == 2
            assert summary["valid"] == 2
            assert summary["broken"] == 0
            assert "timestamp" in summary

    @pytest.mark.description("run_scheduled_validation calls on_broken callback")
    @pytest.mark.asyncio
    async def test_on_broken_callback(self) -> None:
        validator = LocationValidator(
            config=ValidationConfig(enable_archive_fallback=False)
        )

        mock_response = AsyncMock()
        mock_response.status_code = 404
        mock_response.headers = {}

        broken_reports = []

        def on_broken(report: BrokenLocationReport) -> None:
            broken_reports.append(report)

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.head = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            locations = [
                {"location_id": "loc_1", "url": "https://example.com/broken", "content_type": ContentType.TEXT},
            ]

            await run_scheduled_validation(validator, locations, on_broken=on_broken)

            assert len(broken_reports) == 1
            assert broken_reports[0].location_id == "loc_1"


class TestContentTypeValidation:
    """Tests for content-type specific validation."""

    @pytest.mark.description("Video validation includes timestamp info")
    @pytest.mark.asyncio
    async def test_video_validation(self) -> None:
        validator = LocationValidator()

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "video/mp4"}

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.head = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            location = TimestampLocation(start_time=120.0)
            result = await validator.validate_location(
                location_id="loc_123",
                url="https://example.com/video.mp4",
                content_type=ContentType.VIDEO,
                location=location,
            )

            assert result.status == LocationStatus.VALID
            assert result.details.get("timestamp_checked") is True
            assert result.details.get("start_time") == 120.0

    @pytest.mark.description("Slide validation includes slide number")
    @pytest.mark.asyncio
    async def test_slide_validation(self) -> None:
        validator = LocationValidator()

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/vnd.ms-powerpoint"}

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.head = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            location = SlideLocation(slide_number=10)
            result = await validator.validate_location(
                location_id="loc_123",
                url="https://example.com/slides.pptx",
                content_type=ContentType.SLIDE,
                location=location,
            )

            assert result.status == LocationStatus.VALID
            assert result.details.get("slide_checked") is True
            assert result.details.get("slide_number") == 10

    @pytest.mark.description("Text validation includes selector info")
    @pytest.mark.asyncio
    async def test_text_with_selector(self) -> None:
        validator = LocationValidator()

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "text/html"}

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.head = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            location = ElementSelectorLocation(selector="#main-content")
            result = await validator.validate_location(
                location_id="loc_123",
                url="https://example.com/page.html",
                content_type=ContentType.TEXT,
                location=location,
            )

            assert result.status == LocationStatus.VALID
            assert result.details.get("selector_checked") is True
            assert result.details.get("selector") == "#main-content"
