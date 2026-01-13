# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for graceful degradation UI hints.

Tests the LocationConfidence enum and graceful degradation fields
on Fragment and SearchResult dataclasses.
"""
from datetime import datetime, timezone

import pytest
from voogle.core import ContentType, Fragment, LocationConfidence
from voogle.services.search import SearchResult

pytestmark = pytest.mark.unit


class TestLocationConfidence:
    """Tests for LocationConfidence enum."""

    @pytest.mark.description("All location confidence levels have string values")
    def test_location_confidence_values(self) -> None:
        assert LocationConfidence.HIGH.value == "high"
        assert LocationConfidence.MEDIUM.value == "medium"
        assert LocationConfidence.LOW.value == "low"
        assert LocationConfidence.UNAVAILABLE.value == "unavailable"

    @pytest.mark.description("LocationConfidence can be created from string value")
    def test_location_confidence_from_value(self) -> None:
        assert LocationConfidence("high") == LocationConfidence.HIGH
        assert LocationConfidence("medium") == LocationConfidence.MEDIUM
        assert LocationConfidence("low") == LocationConfidence.LOW
        assert LocationConfidence("unavailable") == LocationConfidence.UNAVAILABLE

    @pytest.mark.description("Invalid LocationConfidence value raises ValueError")
    def test_invalid_location_confidence_raises(self) -> None:
        with pytest.raises(ValueError):
            LocationConfidence("invalid")


class TestFragmentGracefulDegradation:
    """Tests for graceful degradation fields on Fragment."""

    @pytest.mark.description("Fragment defaults location_confidence to HIGH")
    def test_default_location_confidence(self) -> None:
        fragment = Fragment(
            id="test-123",
            text="Hello world",
            score=0.9,
            source_id="src-1",
            source_type=ContentType.AUDIO,
        )
        assert fragment.location_confidence == LocationConfidence.HIGH

    @pytest.mark.description("Fragment defaults fallback_url to None")
    def test_default_fallback_url(self) -> None:
        fragment = Fragment(
            id="test-123",
            text="Hello world",
            score=0.9,
            source_id="src-1",
            source_type=ContentType.AUDIO,
        )
        assert fragment.fallback_url is None

    @pytest.mark.description("Fragment defaults archive_url to None")
    def test_default_archive_url(self) -> None:
        fragment = Fragment(
            id="test-123",
            text="Hello world",
            score=0.9,
            source_id="src-1",
            source_type=ContentType.AUDIO,
        )
        assert fragment.archive_url is None

    @pytest.mark.description("Fragment defaults last_known_good to None")
    def test_default_last_known_good(self) -> None:
        fragment = Fragment(
            id="test-123",
            text="Hello world",
            score=0.9,
            source_id="src-1",
            source_type=ContentType.AUDIO,
        )
        assert fragment.last_known_good is None

    @pytest.mark.description("Fragment accepts custom location_confidence")
    def test_custom_location_confidence(self) -> None:
        fragment = Fragment(
            id="test-123",
            text="Hello world",
            score=0.9,
            source_id="src-1",
            source_type=ContentType.AUDIO,
            location_confidence=LocationConfidence.LOW,
        )
        assert fragment.location_confidence == LocationConfidence.LOW

    @pytest.mark.description("Fragment accepts fallback_url")
    def test_fallback_url(self) -> None:
        fragment = Fragment(
            id="test-123",
            text="Hello world",
            score=0.9,
            source_id="src-1",
            source_type=ContentType.AUDIO,
            fallback_url="https://cdn.example.com/backup.mp3",
        )
        assert fragment.fallback_url == "https://cdn.example.com/backup.mp3"

    @pytest.mark.description("Fragment accepts archive_url")
    def test_archive_url(self) -> None:
        fragment = Fragment(
            id="test-123",
            text="Hello world",
            score=0.9,
            source_id="src-1",
            source_type=ContentType.AUDIO,
            archive_url="https://web.archive.org/web/20250101/example.com/audio.mp3",
        )
        assert fragment.archive_url == "https://web.archive.org/web/20250101/example.com/audio.mp3"

    @pytest.mark.description("Fragment accepts last_known_good timestamp")
    def test_last_known_good(self) -> None:
        now = datetime.now(timezone.utc)
        fragment = Fragment(
            id="test-123",
            text="Hello world",
            score=0.9,
            source_id="src-1",
            source_type=ContentType.AUDIO,
            last_known_good=now,
        )
        assert fragment.last_known_good == now

    @pytest.mark.description("Fragment with all graceful degradation fields")
    def test_all_graceful_degradation_fields(self) -> None:
        now = datetime.now(timezone.utc)
        fragment = Fragment(
            id="test-123",
            text="Hello world",
            score=0.9,
            source_id="src-1",
            source_type=ContentType.VIDEO,
            location={"start": 30.0, "end": 45.0},
            deep_link="https://example.com/video?t=30",
            location_confidence=LocationConfidence.MEDIUM,
            fallback_url="https://cdn.example.com/video.mp4",
            archive_url="https://web.archive.org/web/20250101/example.com/video.mp4",
            last_known_good=now,
        )
        assert fragment.location_confidence == LocationConfidence.MEDIUM
        assert fragment.fallback_url == "https://cdn.example.com/video.mp4"
        assert fragment.archive_url == "https://web.archive.org/web/20250101/example.com/video.mp4"
        assert fragment.last_known_good == now

    @pytest.mark.description("Fragment with UNAVAILABLE confidence indicates broken location")
    def test_unavailable_confidence(self) -> None:
        fragment = Fragment(
            id="test-123",
            text="Hello world",
            score=0.9,
            source_id="src-1",
            source_type=ContentType.DOCUMENT,
            location_confidence=LocationConfidence.UNAVAILABLE,
            archive_url="https://web.archive.org/web/20250101/example.com/doc.pdf",
        )
        assert fragment.location_confidence == LocationConfidence.UNAVAILABLE
        assert fragment.archive_url is not None


class TestSearchResultGracefulDegradation:
    """Tests for graceful degradation fields on SearchResult."""

    @pytest.mark.description("SearchResult defaults location_confidence to HIGH")
    def test_default_location_confidence(self) -> None:
        result = SearchResult(
            id="result-1",
            score=0.95,
            text="Fragment text",
            source_id="episode-123",
        )
        assert result.location_confidence == LocationConfidence.HIGH

    @pytest.mark.description("SearchResult defaults fallback_url to None")
    def test_default_fallback_url(self) -> None:
        result = SearchResult(
            id="result-1",
            score=0.95,
            text="Fragment text",
            source_id="episode-123",
        )
        assert result.fallback_url is None

    @pytest.mark.description("SearchResult defaults archive_url to None")
    def test_default_archive_url(self) -> None:
        result = SearchResult(
            id="result-1",
            score=0.95,
            text="Fragment text",
            source_id="episode-123",
        )
        assert result.archive_url is None

    @pytest.mark.description("SearchResult defaults last_known_good to None")
    def test_default_last_known_good(self) -> None:
        result = SearchResult(
            id="result-1",
            score=0.95,
            text="Fragment text",
            source_id="episode-123",
        )
        assert result.last_known_good is None

    @pytest.mark.description("SearchResult accepts custom graceful degradation fields")
    def test_all_graceful_degradation_fields(self) -> None:
        result = SearchResult(
            id="result-1",
            score=0.95,
            text="Fragment text",
            source_id="episode-123",
            source_type="audio",
            start_time=30.0,
            end_time=45.0,
            location_confidence=LocationConfidence.LOW,
            fallback_url="https://cdn.example.com/backup.mp3",
            archive_url="https://web.archive.org/web/20250101/example.com/audio.mp3",
            last_known_good="2025-01-01T12:00:00Z",
        )
        assert result.location_confidence == LocationConfidence.LOW
        assert result.fallback_url == "https://cdn.example.com/backup.mp3"
        assert result.archive_url == "https://web.archive.org/web/20250101/example.com/audio.mp3"
        assert result.last_known_good == "2025-01-01T12:00:00Z"

    @pytest.mark.description("SearchResult with UNAVAILABLE confidence for broken source")
    def test_unavailable_confidence(self) -> None:
        result = SearchResult(
            id="result-1",
            score=0.95,
            text="Fragment text",
            source_id="episode-123",
            location_confidence=LocationConfidence.UNAVAILABLE,
            archive_url="https://web.archive.org/web/20250101/example.com/episode.mp3",
        )
        assert result.location_confidence == LocationConfidence.UNAVAILABLE
        assert result.archive_url is not None


class TestLocationConfidenceUseCases:
    """Tests demonstrating graceful degradation use cases."""

    @pytest.mark.description("High confidence indicates recently verified location")
    def test_high_confidence_scenario(self) -> None:
        """A location verified within 24 hours should have HIGH confidence."""
        recent_check = datetime(2025, 1, 13, 10, 0, 0, tzinfo=timezone.utc)
        fragment = Fragment(
            id="test-1",
            text="Recently verified content",
            score=0.9,
            source_id="src-1",
            source_type=ContentType.VIDEO,
            location_confidence=LocationConfidence.HIGH,
            last_known_good=recent_check,
        )
        assert fragment.location_confidence == LocationConfidence.HIGH
        # Client can confidently show play button

    @pytest.mark.description("Medium confidence indicates stale but likely valid location")
    def test_medium_confidence_scenario(self) -> None:
        """A location not verified for a few days should have MEDIUM confidence."""
        older_check = datetime(2025, 1, 7, 10, 0, 0, tzinfo=timezone.utc)
        fragment = Fragment(
            id="test-1",
            text="Older verified content",
            score=0.9,
            source_id="src-1",
            source_type=ContentType.VIDEO,
            location_confidence=LocationConfidence.MEDIUM,
            last_known_good=older_check,
        )
        assert fragment.location_confidence == LocationConfidence.MEDIUM
        # Client may show play button with "may not be available" tooltip

    @pytest.mark.description("Low confidence indicates unreliable location")
    def test_low_confidence_scenario(self) -> None:
        """A location with intermittent failures should have LOW confidence."""
        fragment = Fragment(
            id="test-1",
            text="Unreliable content",
            score=0.9,
            source_id="src-1",
            source_type=ContentType.VIDEO,
            location_confidence=LocationConfidence.LOW,
            fallback_url="https://cdn.example.com/backup.mp4",
        )
        assert fragment.location_confidence == LocationConfidence.LOW
        # Client should show warning and possibly try fallback first

    @pytest.mark.description("Unavailable confidence indicates broken location with archive fallback")
    def test_unavailable_with_archive_scenario(self) -> None:
        """A broken location should have UNAVAILABLE confidence with archive URL."""
        fragment = Fragment(
            id="test-1",
            text="Content from broken source",
            score=0.9,
            source_id="src-1",
            source_type=ContentType.VIDEO,
            location_confidence=LocationConfidence.UNAVAILABLE,
            archive_url="https://web.archive.org/web/20250101/example.com/video.mp4",
        )
        assert fragment.location_confidence == LocationConfidence.UNAVAILABLE
        assert fragment.archive_url is not None
        # Client should disable play button but offer archive link

    @pytest.mark.description("Unavailable confidence without fallback")
    def test_unavailable_without_fallback_scenario(self) -> None:
        """A broken location with no fallback should clearly indicate unavailability."""
        fragment = Fragment(
            id="test-1",
            text="Content from broken source",
            score=0.9,
            source_id="src-1",
            source_type=ContentType.VIDEO,
            location_confidence=LocationConfidence.UNAVAILABLE,
        )
        assert fragment.location_confidence == LocationConfidence.UNAVAILABLE
        assert fragment.fallback_url is None
        assert fragment.archive_url is None
        # Client should disable play button and show "source unavailable"
