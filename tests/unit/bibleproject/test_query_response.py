# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for QueryResponse schema with BibleProject episode info.

N1: Tests that QueryResponse includes episode_id, stream_url, and channel_type
fields for slide-enabled playback navigation.
"""

import pytest
from starlette.testclient import TestClient

pytestmark = pytest.mark.unit


@pytest.fixture
def api_client() -> TestClient:
    """Create a test client for the API."""
    from voogle import main

    return TestClient(main.app)


class TestQueryResponseSchema:
    """Tests for QueryResponse schema fields."""

    @pytest.mark.description("QueryResponse schema includes episode info fields")
    def test_query_response_schema_has_episode_fields(self) -> None:
        """Verify QueryResponse model has episode_id, stream_url, channel_type."""
        from voogle.schemas.media import QueryResponse

        # Check that the model fields exist
        field_names = set(QueryResponse.model_fields.keys())

        assert "episode_id" in field_names, "QueryResponse missing episode_id field"
        assert "stream_url" in field_names, "QueryResponse missing stream_url field"
        assert "channel_type" in field_names, "QueryResponse missing channel_type field"

    @pytest.mark.description("QueryResponse can be instantiated with episode info")
    def test_query_response_with_episode_info(self) -> None:
        """Verify QueryResponse can include episode info fields."""
        from voogle.schemas.media import QueryResponse

        response = QueryResponse(
            text="Test transcript text",
            similarity=0.85,
            episode=None,
            channel=None,
            start=120.5,
            media_url="https://example.com/audio.mp3",
            episode_id="550e8400-e29b-41d4-a716-446655440000",
            stream_url="https://stream.mux.com/abc123.m3u8",
            channel_type="bibleproject",
        )

        assert response.episode_id == "550e8400-e29b-41d4-a716-446655440000"
        assert response.stream_url == "https://stream.mux.com/abc123.m3u8"
        assert response.channel_type == "bibleproject"

    @pytest.mark.description("QueryResponse fields are optional with None defaults")
    def test_query_response_optional_fields(self) -> None:
        """Verify episode info fields are optional with None defaults."""
        from voogle.schemas.media import QueryResponse

        response = QueryResponse(
            text="Test transcript text",
            similarity=0.85,
            episode=None,
            channel=None,
            start=120.5,
            media_url="https://example.com/audio.mp3",
        )

        assert response.episode_id is None
        assert response.stream_url is None
        assert response.channel_type is None

    @pytest.mark.description("QueryResponse serializes episode info to JSON")
    def test_query_response_json_serialization(self) -> None:
        """Verify episode info fields are included in JSON output."""
        from voogle.schemas.media import QueryResponse

        response = QueryResponse(
            text="Test transcript text",
            similarity=0.85,
            episode=None,
            channel=None,
            start=120.5,
            media_url="https://example.com/audio.mp3",
            episode_id="test-uuid",
            stream_url="https://stream.mux.com/test.m3u8",
            channel_type="bibleproject",
        )

        json_data = response.model_dump()

        assert json_data["episode_id"] == "test-uuid"
        assert json_data["stream_url"] == "https://stream.mux.com/test.m3u8"
        assert json_data["channel_type"] == "bibleproject"


class TestEpisodeStreamUrl:
    """Tests for Episode.stream_url property."""

    @pytest.mark.description("Episode.stream_url returns Mux HLS URL when playback_id exists")
    def test_stream_url_with_mux_id(self) -> None:
        """Verify stream_url property generates correct Mux HLS URL."""
        from voogle.models.media import Episode

        # Create episode instance with mux_playback_id (not saved to DB)
        episode = Episode(
            title="Test Episode",
            description="",
            guid="test:episode:1",
            url="https://example.com/episode",
            mux_playback_id="abc123xyz",
        )

        assert episode.stream_url == "https://stream.mux.com/abc123xyz.m3u8"

    @pytest.mark.description("Episode.stream_url returns None when no playback_id")
    def test_stream_url_without_mux_id(self) -> None:
        """Verify stream_url returns None for non-Mux episodes."""
        from voogle.models.media import Episode

        episode = Episode(
            title="Test Episode",
            description="",
            guid="test:episode:2",
            url="https://example.com/episode",
            mux_playback_id=None,
        )

        assert episode.stream_url is None
