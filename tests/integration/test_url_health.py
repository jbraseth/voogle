# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Integration tests for URL health checking and refresh logic."""

from unittest.mock import patch

import pytest
from voogle import models
from voogle.collection import url_health
from voogle.collection.url_health import URLStatus

pytestmark = pytest.mark.integration


@pytest.mark.description("check_episode_url returns URLHealthResult with episode info")
async def test_check_episode_url(channel: models.media.Channel) -> None:
    """Verify check_episode_url returns proper result structure."""
    _unused = channel  # Creates episodes in DB

    episode = await models.Episode.objects.first()
    assert episode is not None

    with patch("voogle.collection.url_health.check_url") as mock_check:
        mock_check.return_value = (URLStatus.OK, 200, None)

        result = await url_health.check_episode_url(episode)

        assert result.episode_pk == episode.pk
        assert result.episode_title == episode.title
        assert result.url == episode.url
        assert result.status == URLStatus.OK
        assert result.http_code == 200
        assert result.error_message is None
        assert result.checked_at is not None


@pytest.mark.description("check_episode_url captures errors correctly")
async def test_check_episode_url_error(channel: models.media.Channel) -> None:
    """Verify check_episode_url captures error details."""
    _unused = channel

    episode = await models.Episode.objects.first()
    assert episode is not None

    with patch("voogle.collection.url_health.check_url") as mock_check:
        mock_check.return_value = (URLStatus.NOT_FOUND, 404, "URL not found")

        result = await url_health.check_episode_url(episode)

        assert result.status == URLStatus.NOT_FOUND
        assert result.http_code == 404
        assert result.error_message == "URL not found"


@pytest.mark.description("check_channel_urls checks all episodes in channel")
async def test_check_channel_urls(channel: models.media.Channel) -> None:
    """Verify all channel episodes are checked."""
    episode_count = await models.Episode.objects.filter(channel=channel).count()

    with patch("voogle.collection.url_health.check_url") as mock_check:
        mock_check.return_value = (URLStatus.OK, 200, None)

        results = await url_health.check_channel_urls(channel)

        assert len(results) == episode_count
        assert mock_check.call_count == episode_count


@pytest.mark.description("check_channel_urls calls progress callback")
async def test_check_channel_urls_progress(channel: models.media.Channel) -> None:
    """Verify progress callback is called correctly."""
    episode_count = await models.Episode.objects.filter(channel=channel).count()
    progress_calls = []

    def on_progress(checked: int, total: int) -> None:
        progress_calls.append((checked, total))

    with patch("voogle.collection.url_health.check_url") as mock_check:
        mock_check.return_value = (URLStatus.OK, 200, None)

        await url_health.check_channel_urls(channel, on_progress=on_progress)

        assert len(progress_calls) == episode_count
        # Verify progress is incremental
        for i, (checked, total) in enumerate(progress_calls):
            assert checked == i + 1
            assert total == episode_count


@pytest.mark.description("check_all_broken_urls returns only broken episodes")
async def test_check_all_broken_urls(channel: models.media.Channel) -> None:
    """Verify only broken URLs are returned."""
    _unused = channel
    episode_count = await models.Episode.objects.count()
    call_count = 0

    def mock_check_side_effect(url: str, timeout: int = 10) -> tuple:
        nonlocal call_count
        call_count += 1
        # Make first episode broken, rest OK
        if call_count == 1:
            return (URLStatus.NOT_FOUND, 404, "URL not found")
        return (URLStatus.OK, 200, None)

    with patch("voogle.collection.url_health.check_url") as mock_check:
        mock_check.side_effect = mock_check_side_effect

        results = await url_health.check_all_broken_urls()

        # Should only return the one broken URL
        assert len(results) == 1
        assert results[0].status == URLStatus.NOT_FOUND
        # But all episodes should have been checked
        assert mock_check.call_count == episode_count


@pytest.mark.description("find_updated_url finds new URL from RSS feed")
async def test_find_updated_url(channel: models.media.Channel) -> None:
    """Verify finding updated URL from RSS feed."""
    episode = await models.Episode.objects.filter(channel=channel).first()
    assert episode is not None

    new_url = "https://new-cdn.example.com/episode.mp3"

    with patch("voogle.collection.url_health.feed._read_channel_feed") as mock_feed:
        mock_feed.return_value = {
            "rss": {
                "channel": {
                    "item": [
                        {
                            "guid": episode.guid,
                            "title": episode.title,
                            "enclosure": {"@url": new_url},
                        }
                    ]
                }
            }
        }

        with patch("voogle.collection.url_health.check_url") as mock_check:
            mock_check.return_value = (URLStatus.OK, 200, None)

            result = await url_health.find_updated_url(episode, channel)

            assert result.episode_pk == episode.pk
            assert result.old_url == episode.url
            assert result.new_url == new_url
            assert result.match_method == "guid"
            assert result.new_url_valid is True
            assert result.error_message is None


@pytest.mark.description("find_updated_url handles RSS feed fetch failure")
async def test_find_updated_url_feed_failure(channel: models.media.Channel) -> None:
    """Verify handling of RSS feed fetch failure."""
    episode = await models.Episode.objects.filter(channel=channel).first()
    assert episode is not None

    with patch("voogle.collection.url_health.feed._read_channel_feed") as mock_feed:
        mock_feed.return_value = None

        result = await url_health.find_updated_url(episode, channel)

        assert result.new_url is None
        assert result.new_url_valid is False
        assert "Failed to fetch RSS feed" in result.error_message


@pytest.mark.description("find_updated_url handles episode not found in RSS")
async def test_find_updated_url_episode_not_found(channel: models.media.Channel) -> None:
    """Verify handling when episode is not in current RSS."""
    episode = await models.Episode.objects.filter(channel=channel).first()
    assert episode is not None

    with patch("voogle.collection.url_health.feed._read_channel_feed") as mock_feed:
        mock_feed.return_value = {
            "rss": {
                "channel": {
                    "item": [
                        {
                            "guid": "different-guid",
                            "title": "Different Episode",
                            "enclosure": {"@url": "https://other.mp3"},
                        }
                    ]
                }
            }
        }

        result = await url_health.find_updated_url(episode, channel)

        assert result.new_url is None
        assert "not found in current RSS feed" in result.error_message


@pytest.mark.description("apply_url_refresh updates episode URL in database")
async def test_apply_url_refresh(channel: models.media.Channel) -> None:
    """Verify URL refresh updates database correctly."""
    episode = await models.Episode.objects.filter(channel=channel).first()
    assert episode is not None

    old_url = episode.url
    new_url = "https://new-cdn.example.com/updated.mp3"

    with patch("voogle.collection.url_health.check_url") as mock_check:
        mock_check.return_value = (URLStatus.OK, 200, None)

        await url_health.apply_url_refresh(episode, new_url)

    # Reload from database
    updated_episode = await models.Episode.objects.get(pk=episode.pk)
    assert updated_episode.url == new_url
    assert updated_episode.url != old_url


@pytest.mark.description("apply_url_refresh preserves transcription status")
async def test_apply_url_refresh_preserves_status(channel: models.media.Channel) -> None:
    """Verify URL refresh preserves transcription and embeddings status."""
    episode = await models.Episode.objects.filter(channel=channel).first()
    assert episode is not None

    # Set transcribed and embeddings flags
    await episode.update(transcribed=True, embeddings=True)

    new_url = "https://new-cdn.example.com/updated.mp3"

    with patch("voogle.collection.url_health.check_url") as mock_check:
        mock_check.return_value = (URLStatus.OK, 200, None)

        await url_health.apply_url_refresh(episode, new_url)

    # Reload and verify status preserved
    updated_episode = await models.Episode.objects.get(pk=episode.pk)
    assert updated_episode.url == new_url
    assert updated_episode.transcribed is True
    assert updated_episode.embeddings is True


@pytest.mark.description("apply_url_refresh rejects inaccessible new URL")
async def test_apply_url_refresh_rejects_bad_url(channel: models.media.Channel) -> None:
    """Verify URL refresh rejects inaccessible new URLs."""
    episode = await models.Episode.objects.filter(channel=channel).first()
    assert episode is not None

    old_url = episode.url
    new_url = "https://broken.example.com/404.mp3"

    with patch("voogle.collection.url_health.check_url") as mock_check:
        mock_check.return_value = (URLStatus.NOT_FOUND, 404, "URL not found")

        with pytest.raises(ValueError, match="not accessible"):
            await url_health.apply_url_refresh(episode, new_url)

    # Verify URL was NOT changed
    unchanged_episode = await models.Episode.objects.get(pk=episode.pk)
    assert unchanged_episode.url == old_url
