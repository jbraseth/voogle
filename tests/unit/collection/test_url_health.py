# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for URL health checking and refresh logic."""

from unittest.mock import MagicMock, patch

import pytest
import requests
from voogle.collection.url_health import (
    URLStatus,
    check_url,
    find_episode_in_rss,
)

pytestmark = pytest.mark.unit


class TestCheckUrl:
    """Tests for the check_url function."""

    @pytest.mark.description("check_url returns OK for accessible URLs")
    def test_accessible_url(self) -> None:
        """Accessible URL should return OK status."""
        with patch("voogle.collection.url_health.requests.head") as mock_head:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_head.return_value = mock_response

            status, code, error = check_url("https://example.com/file.mp3")

            assert status == URLStatus.OK
            assert code == 200
            assert error is None
            mock_head.assert_called_once()

    @pytest.mark.description("check_url returns NOT_FOUND for 404 responses")
    def test_not_found_url(self) -> None:
        """404 response should return NOT_FOUND status."""
        with patch("voogle.collection.url_health.requests.head") as mock_head:
            mock_response = MagicMock()
            mock_response.status_code = 404
            error = requests.HTTPError(response=mock_response)
            mock_head.side_effect = error

            status, code, error_msg = check_url("https://example.com/missing.mp3")

            assert status == URLStatus.NOT_FOUND
            assert code == 404
            assert error_msg == "URL not found"

    @pytest.mark.description("check_url returns FORBIDDEN for 403 responses")
    def test_forbidden_url(self) -> None:
        """403 response should return FORBIDDEN status."""
        with patch("voogle.collection.url_health.requests.head") as mock_head:
            mock_response = MagicMock()
            mock_response.status_code = 403
            error = requests.HTTPError(response=mock_response)
            mock_head.side_effect = error

            status, code, error_msg = check_url("https://example.com/private.mp3")

            assert status == URLStatus.FORBIDDEN
            assert code == 403
            assert error_msg == "Access forbidden"

    @pytest.mark.description("check_url returns SERVER_ERROR for 5xx responses")
    def test_server_error_url(self) -> None:
        """5xx response should return SERVER_ERROR status."""
        with patch("voogle.collection.url_health.requests.head") as mock_head:
            mock_response = MagicMock()
            mock_response.status_code = 503
            error = requests.HTTPError(response=mock_response)
            mock_head.side_effect = error

            status, code, error_msg = check_url("https://example.com/file.mp3")

            assert status == URLStatus.SERVER_ERROR
            assert code == 503
            assert "503" in error_msg

    @pytest.mark.description("check_url returns TIMEOUT when request times out")
    def test_timeout(self) -> None:
        """Timeout should return TIMEOUT status."""
        with patch("voogle.collection.url_health.requests.head") as mock_head:
            mock_head.side_effect = requests.exceptions.Timeout()

            status, code, error_msg = check_url("https://slow.example.com/file.mp3")

            assert status == URLStatus.TIMEOUT
            assert code is None
            assert error_msg == "Request timed out"

    @pytest.mark.description("check_url returns CONNECTION_ERROR when host unreachable")
    def test_connection_error(self) -> None:
        """Connection error should return CONNECTION_ERROR status."""
        with patch("voogle.collection.url_health.requests.head") as mock_head:
            mock_head.side_effect = requests.exceptions.ConnectionError()

            status, code, error_msg = check_url("https://unreachable.example.com/file.mp3")

            assert status == URLStatus.CONNECTION_ERROR
            assert code is None
            assert error_msg == "Host unreachable"

    @pytest.mark.description("check_url returns REDIRECT_LOOP for too many redirects")
    def test_redirect_loop(self) -> None:
        """Too many redirects should return REDIRECT_LOOP status."""
        with patch("voogle.collection.url_health.requests.head") as mock_head:
            mock_head.side_effect = requests.exceptions.TooManyRedirects()

            status, code, error_msg = check_url("https://loop.example.com/file.mp3")

            assert status == URLStatus.REDIRECT_LOOP
            assert code is None
            assert error_msg == "Too many redirects"

    @pytest.mark.description("check_url uses correct timeout and headers")
    def test_request_parameters(self) -> None:
        """Verify correct request parameters are used."""
        with patch("voogle.collection.url_health.requests.head") as mock_head:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_head.return_value = mock_response

            check_url("https://example.com/file.mp3", timeout=15)

            mock_head.assert_called_once_with(
                "https://example.com/file.mp3",
                timeout=15,
                allow_redirects=True,
                headers={"User-Agent": "Voogle/1.0 (URL Health Check)"},
            )


class TestFindEpisodeInRss:
    """Tests for the find_episode_in_rss function."""

    @pytest.mark.description("find_episode_in_rss matches by GUID first")
    def test_match_by_guid(self) -> None:
        """Episode should match by GUID."""
        episode = MagicMock()
        episode.guid = "unique-guid-123"
        episode.title = "Episode Title"

        rss_items = [
            {"guid": "other-guid", "title": "Other Episode"},
            {"guid": "unique-guid-123", "title": "Different Title", "enclosure": {"@url": "new-url"}},
        ]

        result, method = find_episode_in_rss(episode, rss_items)

        assert result is not None
        assert result["guid"] == "unique-guid-123"
        assert method == "guid"

    @pytest.mark.description("find_episode_in_rss falls back to title match")
    def test_fallback_to_title(self) -> None:
        """When GUID doesn't match, should fall back to title."""
        episode = MagicMock()
        episode.guid = "old-guid"
        episode.title = "Episode Title"

        rss_items = [
            {"guid": "new-guid", "title": "Episode Title", "enclosure": {"@url": "new-url"}},
        ]

        result, method = find_episode_in_rss(episode, rss_items)

        assert result is not None
        assert result["title"] == "Episode Title"
        assert method == "title"

    @pytest.mark.description("find_episode_in_rss returns None when no match")
    def test_no_match(self) -> None:
        """No match should return None."""
        episode = MagicMock()
        episode.guid = "my-guid"
        episode.title = "My Episode"

        rss_items = [
            {"guid": "other-guid", "title": "Other Episode"},
            {"guid": "another-guid", "title": "Another Episode"},
        ]

        result, method = find_episode_in_rss(episode, rss_items)

        assert result is None
        assert method is None

    @pytest.mark.description("find_episode_in_rss handles case-insensitive title match")
    def test_case_insensitive_title(self) -> None:
        """Title matching should be case-insensitive."""
        episode = MagicMock()
        episode.guid = "no-match-guid"
        episode.title = "EPISODE TITLE"

        rss_items = [
            {"guid": "other-guid", "title": "episode title", "enclosure": {"@url": "url"}},
        ]

        result, method = find_episode_in_rss(episode, rss_items)

        assert result is not None
        assert method == "title"

    @pytest.mark.description("find_episode_in_rss handles dict GUID format")
    def test_dict_guid_format(self) -> None:
        """Should handle GUID as dict with #text key (xmltodict format)."""
        episode = MagicMock()
        episode.guid = "unique-guid-123"
        episode.title = "Episode Title"

        rss_items = [
            {"guid": {"#text": "unique-guid-123", "@isPermaLink": "false"}, "title": "Title"},
        ]

        result, method = find_episode_in_rss(episode, rss_items)

        assert result is not None
        assert method == "guid"

    @pytest.mark.description("find_episode_in_rss handles empty RSS items")
    def test_empty_rss_items(self) -> None:
        """Empty RSS items list should return None."""
        episode = MagicMock()
        episode.guid = "guid"
        episode.title = "Title"

        result, method = find_episode_in_rss(episode, [])

        assert result is None
        assert method is None

    @pytest.mark.description("find_episode_in_rss handles missing guid in RSS item")
    def test_missing_guid_in_item(self) -> None:
        """Should handle RSS items without GUID and fall back to title."""
        episode = MagicMock()
        episode.guid = "my-guid"
        episode.title = "My Episode"

        rss_items = [
            {"title": "My Episode", "enclosure": {"@url": "url"}},  # No guid
        ]

        result, method = find_episode_in_rss(episode, rss_items)

        assert result is not None
        assert method == "title"
