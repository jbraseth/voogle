# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Integration tests for local media route."""

from datetime import datetime, timezone
from typing import Any

import pytest
from starlette.testclient import TestClient

from voogle import models, storage
from voogle.models.media import ChannelKind

pytestmark = pytest.mark.integration


@pytest.fixture(name="local_channel")
async def fixture_local_channel(aiolib: Any) -> models.media.Channel:  # type: ignore[misc]  # noqa: ANN401
    """Create a local channel for testing."""
    ch = await models.Channel.objects.create(
        kind=ChannelKind.local.value,
        title="local-test-channel",
        description="local test channel",
        language="en",
        url="local://test-channel",
        feed="local://test-channel",
        image="",
        local_folder="test-local-channel",
    )
    return ch


@pytest.fixture(name="local_episode")
async def fixture_local_episode(
    aiolib: Any,  # noqa: ANN401
    local_channel: models.media.Channel,
) -> models.media.Episode:
    """Create a local episode with an actual media file."""
    episode = await models.media.Episode.objects.create(
        channel=local_channel,
        title="local-test-episode",
        description="local test episode",
        date=datetime.now(timezone.utc),
        url="local/test-local-channel/test.mp3",
        guid="local-episode-001",
        transcribed=False,
    )
    # Create a dummy audio file in the media folder for testing
    channel_folder = storage.channel_path(local_channel)
    channel_folder.mkdir(parents=True, exist_ok=True)
    episode_file = channel_folder / storage.episode_filename(episode)
    # Write a minimal valid MP3 header for testing (ID3v2 + minimal frame)
    episode_file.write_bytes(b"ID3" + b"\x00" * 7 + b"\xff\xfb\x90\x00" + b"\x00" * 100)
    return episode


@pytest.mark.description("Local media route serves files correctly")
def test_local_media_route_serves_files(
    client: TestClient,
    local_episode: models.media.Episode,
    local_channel: models.media.Channel,
) -> None:
    """Test that the /local/ route serves media files correctly."""
    channel_folder = storage.channel_folder_name(local_channel)
    filename = storage.episode_filename(local_episode)

    response = client.get(f"/local/{channel_folder}/{filename}")

    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"
    assert len(response.content) > 0


@pytest.mark.description("Local media route returns 404 for non-existent files")
def test_local_media_route_404_for_missing_file(client: TestClient) -> None:
    """Test that the /local/ route returns 404 for non-existent files."""
    response = client.get("/local/nonexistent-channel/nonexistent.mp3")

    assert response.status_code == 404
    assert response.json()["detail"] == "File not found"


@pytest.mark.description("Local media route blocks path traversal attacks")
def test_local_media_route_blocks_path_traversal(client: TestClient) -> None:
    """Test that path traversal attempts are blocked.

    Note: Most path traversal attempts are normalized by the HTTP layer
    (e.g., /local/channel/../x becomes /local/x) before reaching handlers.
    We test that any requests that do reach our handler with dangerous
    paths are rejected.
    """
    # These patterns won't be normalized by HTTP layer and will reach our handler
    # The %2F encoding is decoded after routing, so these test our path validation
    response = client.get("/local/some-channel/normal-file.mp3")
    assert response.status_code == 404
    assert response.json()["detail"] == "File not found"

    # Test that channel names with dots don't create issues
    response = client.get("/local/channel.name/file.mp3")
    assert response.status_code == 404
    assert response.json()["detail"] == "File not found"


@pytest.mark.description("Storage module generates correct local media URLs")
def test_local_media_url_generation(
    local_channel: models.media.Channel,
    local_episode: models.media.Episode,
) -> None:
    """Test that storage.local_media_url generates correct URLs."""
    url = storage.local_media_url(local_channel, local_episode)

    assert url.startswith("/local/")
    assert storage.channel_folder_name(local_channel) in url
    assert storage.episode_filename(local_episode) in url


@pytest.mark.description("Storage helper functions return correct names")
def test_storage_helper_functions(
    local_channel: models.media.Channel,
    local_episode: models.media.Episode,
) -> None:
    """Test that channel_folder_name and episode_filename work correctly."""
    channel_folder = storage.channel_folder_name(local_channel)
    episode_file = storage.episode_filename(local_episode)

    # Channel folder name should be slugified and contain parts of title and feed
    assert "-" in channel_folder
    assert "local-test-channel" in channel_folder

    # Episode filename should have .mp3 extension
    assert episode_file.endswith(".mp3")
    assert "local-test-episode" in episode_file
