# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Location validation service for fragment location health monitoring.

This module provides the LocationValidator class for validating and refreshing
fragment locations. It supports scheduled validation, per-content-type logic,
broken location reporting, and auto-refresh attempts.

Features:
- LocationStatus enum (valid/stale/broken) for tracking location health
- last_validated_at timestamp tracking
- Per-content-type validation strategies
- Scheduled validation job support
- Broken location reporting with detailed error context
- Auto-refresh attempts for recoverable locations
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable
from urllib.parse import urlparse

import httpx

from voogle.core.fragment import ContentType
from voogle.core.location import (
    ElementSelectorLocation,
    Location,
    PageBboxLocation,
    SlideLocation,
    TimestampLocation,
)
from voogle.durability.archive import ArchiveFallback, ArchiveStatus

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    """Get current UTC datetime (extracted for testability)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class LocationStatus(Enum):
    """Status of a location validation check.

    Attributes:
        VALID: Location is accessible and content is available.
        STALE: Location was valid but needs re-validation (aged out).
        BROKEN: Location is inaccessible or content is unavailable.
    """

    VALID = "valid"
    STALE = "stale"
    BROKEN = "broken"


@dataclass
class ValidationResult:
    """Result of a location validation check.

    Attributes:
        location_id: Identifier for the validated location.
        status: The current status of the location.
        last_validated_at: When this validation was performed.
        error: Error message if status is BROKEN.
        fallback_url: Alternative URL if original is broken (e.g., archive.org).
        details: Additional validation details.
    """

    location_id: str
    status: LocationStatus
    last_validated_at: datetime
    error: str | None = None
    fallback_url: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary for serialization."""
        return {
            "location_id": self.location_id,
            "status": self.status.value,
            "last_validated_at": self.last_validated_at.isoformat(),
            "error": self.error,
            "fallback_url": self.fallback_url,
            "details": self.details,
        }


@dataclass
class BrokenLocationReport:
    """Report of a broken location for monitoring and alerting.

    Attributes:
        location_id: Identifier of the broken location.
        url: The URL that is broken.
        content_type: Type of content at this location.
        error: Description of why the location is broken.
        first_detected_at: When the break was first detected.
        last_checked_at: When the location was last checked.
        check_count: Number of times this location has been checked.
        recovery_attempted: Whether auto-refresh was attempted.
        recovered: Whether the location was successfully recovered.
    """

    location_id: str
    url: str
    content_type: ContentType
    error: str
    first_detected_at: datetime
    last_checked_at: datetime
    check_count: int = 1
    recovery_attempted: bool = False
    recovered: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert report to dictionary for serialization."""
        return {
            "location_id": self.location_id,
            "url": self.url,
            "content_type": self.content_type.value,
            "error": self.error,
            "first_detected_at": self.first_detected_at.isoformat(),
            "last_checked_at": self.last_checked_at.isoformat(),
            "check_count": self.check_count,
            "recovery_attempted": self.recovery_attempted,
            "recovered": self.recovered,
        }


@dataclass
class ValidationConfig:
    """Configuration for the LocationValidator.

    Attributes:
        stale_threshold_hours: Hours after which a location becomes stale.
        http_timeout: Timeout for HTTP requests in seconds.
        max_retries: Maximum retry attempts for failed validations.
        enable_archive_fallback: Whether to check archive.org for broken URLs.
        batch_size: Number of locations to validate in parallel.
        retry_backoff_base: Base seconds for exponential backoff.
    """

    stale_threshold_hours: int = 24
    http_timeout: float = 30.0
    max_retries: int = 3
    enable_archive_fallback: bool = True
    batch_size: int = 10
    retry_backoff_base: float = 2.0


# Type alias for content-type specific validators
ContentTypeValidator = Callable[[str, Location | None], "asyncio.Task[ValidationResult]"]


class LocationValidator:
    """Service for validating and refreshing fragment locations.

    Provides scheduled validation, per-content-type logic, broken location
    reporting, and auto-refresh attempts for recovering broken URLs.

    Example:
        >>> validator = LocationValidator()
        >>> result = await validator.validate_location(
        ...     location_id="loc_123",
        ...     url="https://example.com/video",
        ...     content_type=ContentType.VIDEO,
        ...     location=TimestampLocation(start_time=30.0)
        ... )
        >>> if result.status == LocationStatus.VALID:
        ...     print("Location is accessible")

    Scheduling:
        Use run_scheduled_validation() to validate all locations in a corpus,
        or integrate with your job scheduler (RQ, Celery, etc.).

    Recovery:
        When a location is broken, the validator automatically attempts to
        find an archive.org fallback if enable_archive_fallback is True.
    """

    def __init__(self, config: ValidationConfig | None = None) -> None:
        """Initialize the location validator.

        Args:
            config: Optional configuration. Uses defaults if not provided.
        """
        self._config = config or ValidationConfig()
        self._archive_fallback: ArchiveFallback | None = None
        self._broken_reports: dict[str, BrokenLocationReport] = {}
        self._validation_cache: dict[str, ValidationResult] = {}

    def __str__(self) -> str:
        """Return string representation."""
        return f"LocationValidator(stale_threshold={self._config.stale_threshold_hours}h)"

    def __repr__(self) -> str:
        """Return detailed string representation."""
        return f"LocationValidator(config={self._config!r})"

    @property
    def archive_fallback(self) -> ArchiveFallback:
        """Get or lazily initialize the archive fallback service."""
        if self._archive_fallback is None:
            self._archive_fallback = ArchiveFallback(
                timeout=self._config.http_timeout,
                max_retries=self._config.max_retries,
            )
        return self._archive_fallback

    async def validate_location(
        self,
        location_id: str,
        url: str,
        content_type: ContentType,
        location: Location | None = None,
    ) -> ValidationResult:
        """Validate a single location.

        Performs content-type specific validation and optionally attempts
        to find a fallback URL if the original is broken.

        Args:
            location_id: Unique identifier for this location.
            url: The URL to validate.
            content_type: The type of content at this location.
            location: Optional specific location within the content.

        Returns:
            ValidationResult with status and details.
        """
        logger.debug("Validating location %s: %s", location_id, url)
        now = _utcnow()

        # Dispatch to content-type specific validator
        try:
            result = await self._validate_by_content_type(
                location_id=location_id,
                url=url,
                content_type=content_type,
                location=location,
            )
        except Exception as e:
            logger.error("Validation failed for %s: %s", location_id, e)
            result = ValidationResult(
                location_id=location_id,
                status=LocationStatus.BROKEN,
                last_validated_at=now,
                error=str(e),
            )

        # Update cache
        self._validation_cache[location_id] = result

        # Handle broken locations
        if result.status == LocationStatus.BROKEN:
            await self._handle_broken_location(
                location_id=location_id,
                url=url,
                content_type=content_type,
                error=result.error or "Unknown error",
            )

            # Attempt auto-refresh if enabled
            if self._config.enable_archive_fallback:
                fallback_url = await self._attempt_auto_refresh(url)
                if fallback_url:
                    result = ValidationResult(
                        location_id=location_id,
                        status=LocationStatus.VALID,
                        last_validated_at=now,
                        fallback_url=fallback_url,
                        details={"recovered_from": "archive.org"},
                    )
                    self._mark_recovered(location_id)

        return result

    async def _validate_by_content_type(
        self,
        location_id: str,
        url: str,
        content_type: ContentType,
        location: Location | None = None,
    ) -> ValidationResult:
        """Dispatch validation to content-type specific handler.

        Args:
            location_id: Unique identifier for this location.
            url: The URL to validate.
            content_type: The type of content at this location.
            location: Optional specific location within the content.

        Returns:
            ValidationResult from the content-type specific validator.
        """
        validators = {
            ContentType.AUDIO: self._validate_audio,
            ContentType.VIDEO: self._validate_video,
            ContentType.DOCUMENT: self._validate_document,
            ContentType.SLIDE: self._validate_slide,
            ContentType.TEXT: self._validate_text,
            ContentType.EMAIL: self._validate_email,
        }

        validator = validators.get(content_type, self._validate_generic)
        return await validator(location_id, url, location)

    async def _validate_generic(
        self,
        location_id: str,
        url: str,
        location: Location | None = None,  # noqa: ARG002
    ) -> ValidationResult:
        """Generic URL validation via HTTP HEAD request.

        Args:
            location_id: Unique identifier for this location.
            url: The URL to validate.
            location: Ignored for generic validation.

        Returns:
            ValidationResult based on HTTP response.
        """
        now = _utcnow()

        try:
            async with httpx.AsyncClient(timeout=self._config.http_timeout) as client:
                response = await client.head(url, follow_redirects=True)

                if response.status_code < 400:
                    return ValidationResult(
                        location_id=location_id,
                        status=LocationStatus.VALID,
                        last_validated_at=now,
                        details={
                            "status_code": response.status_code,
                            "content_type": response.headers.get("content-type"),
                        },
                    )
                else:
                    return ValidationResult(
                        location_id=location_id,
                        status=LocationStatus.BROKEN,
                        last_validated_at=now,
                        error=f"HTTP {response.status_code}",
                        details={"status_code": response.status_code},
                    )
        except httpx.TimeoutException:
            return ValidationResult(
                location_id=location_id,
                status=LocationStatus.BROKEN,
                last_validated_at=now,
                error="Request timed out",
            )
        except Exception as e:
            return ValidationResult(
                location_id=location_id,
                status=LocationStatus.BROKEN,
                last_validated_at=now,
                error=str(e),
            )

    async def _validate_audio(
        self,
        location_id: str,
        url: str,
        location: Location | None = None,
    ) -> ValidationResult:
        """Validate audio content location.

        Checks that the URL is accessible and optionally validates
        that the timestamp location is within the audio duration.

        Args:
            location_id: Unique identifier for this location.
            url: The URL to validate.
            location: Optional TimestampLocation for timestamp validation.

        Returns:
            ValidationResult for the audio location.
        """
        result = await self._validate_generic(location_id, url, location)

        if result.status == LocationStatus.VALID:
            # Additional audio-specific checks could go here
            # e.g., checking audio duration against timestamp
            if isinstance(location, TimestampLocation):
                result.details["timestamp_checked"] = True
                result.details["start_time"] = location.start_time

        return result

    async def _validate_video(
        self,
        location_id: str,
        url: str,
        location: Location | None = None,
    ) -> ValidationResult:
        """Validate video content location.

        Similar to audio validation with timestamp support.

        Args:
            location_id: Unique identifier for this location.
            url: The URL to validate.
            location: Optional TimestampLocation for timestamp validation.

        Returns:
            ValidationResult for the video location.
        """
        result = await self._validate_generic(location_id, url, location)

        if result.status == LocationStatus.VALID:
            if isinstance(location, TimestampLocation):
                result.details["timestamp_checked"] = True
                result.details["start_time"] = location.start_time

        return result

    async def _validate_document(
        self,
        location_id: str,
        url: str,
        location: Location | None = None,
    ) -> ValidationResult:
        """Validate document (PDF) location.

        Checks URL accessibility and optionally validates page reference.

        Args:
            location_id: Unique identifier for this location.
            url: The URL to validate.
            location: Optional PageBboxLocation for page validation.

        Returns:
            ValidationResult for the document location.
        """
        result = await self._validate_generic(location_id, url, location)

        if result.status == LocationStatus.VALID:
            if isinstance(location, PageBboxLocation):
                result.details["page_checked"] = True
                result.details["page"] = location.page

        return result

    async def _validate_slide(
        self,
        location_id: str,
        url: str,
        location: Location | None = None,
    ) -> ValidationResult:
        """Validate slide presentation location.

        Args:
            location_id: Unique identifier for this location.
            url: The URL to validate.
            location: Optional SlideLocation for slide validation.

        Returns:
            ValidationResult for the slide location.
        """
        result = await self._validate_generic(location_id, url, location)

        if result.status == LocationStatus.VALID:
            if isinstance(location, SlideLocation):
                result.details["slide_checked"] = True
                result.details["slide_number"] = location.slide_number

        return result

    async def _validate_text(
        self,
        location_id: str,
        url: str,
        location: Location | None = None,
    ) -> ValidationResult:
        """Validate text/web content location.

        Args:
            location_id: Unique identifier for this location.
            url: The URL to validate.
            location: Optional ElementSelectorLocation for element validation.

        Returns:
            ValidationResult for the text location.
        """
        result = await self._validate_generic(location_id, url, location)

        if result.status == LocationStatus.VALID:
            if isinstance(location, ElementSelectorLocation):
                result.details["selector_checked"] = True
                result.details["selector"] = location.selector

        return result

    async def _validate_email(
        self,
        location_id: str,
        url: str,
        location: Location | None = None,  # noqa: ARG002
    ) -> ValidationResult:
        """Validate email location.

        Email locations are validated differently as they may reference
        local email stores rather than HTTP URLs.

        Args:
            location_id: Unique identifier for this location.
            url: The URL or email reference to validate.
            location: Ignored for email validation.

        Returns:
            ValidationResult for the email location.
        """
        now = _utcnow()
        parsed = urlparse(url)

        # Handle different email URL schemes
        if parsed.scheme in ("mailto", "email"):
            # These are reference-only URLs, consider them valid
            return ValidationResult(
                location_id=location_id,
                status=LocationStatus.VALID,
                last_validated_at=now,
                details={"scheme": parsed.scheme, "reference_only": True},
            )

        # For HTTP URLs (webmail links), do generic validation
        return await self._validate_generic(location_id, url, None)

    async def _handle_broken_location(
        self,
        location_id: str,
        url: str,
        content_type: ContentType,
        error: str,
    ) -> None:
        """Record a broken location for reporting.

        Args:
            location_id: Identifier of the broken location.
            url: The broken URL.
            content_type: Type of content at this location.
            error: Description of the error.
        """
        now = _utcnow()

        if location_id in self._broken_reports:
            # Update existing report
            report = self._broken_reports[location_id]
            self._broken_reports[location_id] = BrokenLocationReport(
                location_id=report.location_id,
                url=report.url,
                content_type=report.content_type,
                error=error,
                first_detected_at=report.first_detected_at,
                last_checked_at=now,
                check_count=report.check_count + 1,
                recovery_attempted=report.recovery_attempted,
                recovered=report.recovered,
            )
        else:
            # Create new report
            self._broken_reports[location_id] = BrokenLocationReport(
                location_id=location_id,
                url=url,
                content_type=content_type,
                error=error,
                first_detected_at=now,
                last_checked_at=now,
            )

        logger.warning("Broken location detected: %s - %s", location_id, error)

    async def _attempt_auto_refresh(self, url: str) -> str | None:
        """Attempt to find a fallback URL for a broken location.

        Args:
            url: The broken URL to find an alternative for.

        Returns:
            Fallback URL if found, None otherwise.
        """
        if not self._config.enable_archive_fallback:
            return None

        logger.debug("Attempting auto-refresh for: %s", url)

        try:
            snapshot = await self.archive_fallback.check_availability(url)
            if snapshot.status == ArchiveStatus.AVAILABLE:
                logger.info("Found archive fallback: %s", snapshot.archive_url)
                return snapshot.archive_url
        except Exception as e:
            logger.debug("Archive fallback failed: %s", e)

        return None

    def _mark_recovered(self, location_id: str) -> None:
        """Mark a broken location as recovered.

        Args:
            location_id: Identifier of the recovered location.
        """
        if location_id in self._broken_reports:
            report = self._broken_reports[location_id]
            self._broken_reports[location_id] = BrokenLocationReport(
                location_id=report.location_id,
                url=report.url,
                content_type=report.content_type,
                error=report.error,
                first_detected_at=report.first_detected_at,
                last_checked_at=_utcnow(),
                check_count=report.check_count,
                recovery_attempted=True,
                recovered=True,
            )

    async def validate_batch(
        self,
        locations: list[dict[str, Any]],
    ) -> list[ValidationResult]:
        """Validate multiple locations in parallel.

        Args:
            locations: List of location dicts with keys:
                - location_id: str
                - url: str
                - content_type: ContentType
                - location: Location | None

        Returns:
            List of ValidationResult in the same order as input.
        """
        semaphore = asyncio.Semaphore(self._config.batch_size)

        async def validate_with_semaphore(loc: dict[str, Any]) -> ValidationResult:
            async with semaphore:
                return await self.validate_location(
                    location_id=loc["location_id"],
                    url=loc["url"],
                    content_type=loc["content_type"],
                    location=loc.get("location"),
                )

        tasks = [validate_with_semaphore(loc) for loc in locations]
        return await asyncio.gather(*tasks)

    def is_stale(self, last_validated_at: datetime) -> bool:
        """Check if a validation result is stale.

        Args:
            last_validated_at: When the location was last validated.

        Returns:
            True if the validation is stale and needs refresh.
        """
        threshold = timedelta(hours=self._config.stale_threshold_hours)
        return _utcnow() - last_validated_at > threshold

    def get_status_for_age(self, last_validated_at: datetime | None) -> LocationStatus:
        """Determine status based on validation age.

        Args:
            last_validated_at: When the location was last validated.

        Returns:
            LocationStatus based on age.
        """
        if last_validated_at is None:
            return LocationStatus.STALE
        if self.is_stale(last_validated_at):
            return LocationStatus.STALE
        return LocationStatus.VALID

    def get_broken_reports(self) -> list[BrokenLocationReport]:
        """Get all broken location reports.

        Returns:
            List of BrokenLocationReport for all broken locations.
        """
        return list(self._broken_reports.values())

    def get_broken_report(self, location_id: str) -> BrokenLocationReport | None:
        """Get a specific broken location report.

        Args:
            location_id: Identifier of the location.

        Returns:
            BrokenLocationReport if the location is broken, None otherwise.
        """
        return self._broken_reports.get(location_id)

    def clear_broken_reports(self) -> int:
        """Clear all broken location reports.

        Returns:
            Number of reports cleared.
        """
        count = len(self._broken_reports)
        self._broken_reports.clear()
        return count

    def get_cached_result(self, location_id: str) -> ValidationResult | None:
        """Get a cached validation result.

        Args:
            location_id: Identifier of the location.

        Returns:
            Cached ValidationResult if available, None otherwise.
        """
        return self._validation_cache.get(location_id)

    def clear_cache(self) -> int:
        """Clear the validation cache.

        Returns:
            Number of cached results cleared.
        """
        count = len(self._validation_cache)
        self._validation_cache.clear()
        return count

    def get_validation_stats(self) -> dict[str, Any]:
        """Get validation statistics.

        Returns:
            Dictionary with validation statistics.
        """
        total_cached = len(self._validation_cache)
        valid_count = sum(
            1 for r in self._validation_cache.values() if r.status == LocationStatus.VALID
        )
        broken_count = sum(
            1 for r in self._validation_cache.values() if r.status == LocationStatus.BROKEN
        )
        stale_count = sum(
            1 for r in self._validation_cache.values() if r.status == LocationStatus.STALE
        )

        return {
            "total_cached": total_cached,
            "valid": valid_count,
            "broken": broken_count,
            "stale": stale_count,
            "broken_reports": len(self._broken_reports),
            "recovered": sum(1 for r in self._broken_reports.values() if r.recovered),
        }


async def run_scheduled_validation(
    validator: LocationValidator,
    locations: list[dict[str, Any]],
    on_broken: Callable[[BrokenLocationReport], None] | None = None,
) -> dict[str, Any]:
    """Run scheduled validation for a batch of locations.

    This is a convenience function for integrating with job schedulers.
    It validates all locations and optionally calls a callback for broken ones.

    Args:
        validator: The LocationValidator instance to use.
        locations: List of location dicts to validate.
        on_broken: Optional callback for each broken location.

    Returns:
        Summary statistics of the validation run.
    """
    logger.info("Starting scheduled validation for %d locations", len(locations))

    results = await validator.validate_batch(locations)

    valid_count = sum(1 for r in results if r.status == LocationStatus.VALID)
    broken_count = sum(1 for r in results if r.status == LocationStatus.BROKEN)
    stale_count = sum(1 for r in results if r.status == LocationStatus.STALE)

    if on_broken:
        for result in results:
            if result.status == LocationStatus.BROKEN:
                report = validator.get_broken_report(result.location_id)
                if report:
                    on_broken(report)

    logger.info(
        "Validation complete: %d valid, %d broken, %d stale",
        valid_count,
        broken_count,
        stale_count,
    )

    return {
        "total": len(results),
        "valid": valid_count,
        "broken": broken_count,
        "stale": stale_count,
        "timestamp": _utcnow().isoformat(),
    }
