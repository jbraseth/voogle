# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Integration tests for local media route."""

from datetime import datetime, timezone
from pathlib import Path

import pytest
from starlette.testclient import TestClient
from voogle import embedding, models, storage, transcription, vector
from voogle.models.media import ChannelKind

pytestmark = pytest.mark.integration


@pytest.fixture(name="local_channel")
async def fixture_local_channel() -> models.media.Channel:
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

    Note: Most traversal patterns (e.g., /../) are normalized by the HTTP
    layer before reaching our handler. We verify that:
    1. Normalized requests return 404 (route not found)
    2. Patterns that reach our handler are rejected with our message
    """
    # Direct traversal gets normalized by HTTP layer to /etc/passwd
    # which doesn't match our route, so FastAPI returns generic 404
    response = client.get("/local/channel/../../../etc/passwd")
    assert response.status_code == 404

    # URL-encoded slashes in filename reach our handler and get validated
    response = client.get("/local/channel/..%2F..%2F..%2Fetc%2Fpasswd")
    assert response.status_code == 404
    assert response.json()["detail"] == "File not found"

    # Double-encoded stays as literal text, reaches handler, file not found
    response = client.get("/local/channel/..%252F..%252Fetc%252Fpasswd")
    assert response.status_code == 404
    assert response.json()["detail"] == "File not found"

    # Non-existent channel with suspicious filename
    response = client.get("/local/fake-channel/etc/passwd")
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


@pytest.mark.description("Query endpoint returns /local/ URLs for local channel episodes")
async def test_query_returns_local_url_for_local_channel(
    local_channel: models.media.Channel,
    local_episode: models.media.Episode,
    jobs_csv_path: Path,
    client: TestClient,
) -> None:
    """Test that querying a local channel episode returns a /local/ prefixed media_url.

    This verifies the presentation-layer URL rewriting works correctly for local channels.
    """
    # Create transcription file for the episode
    trans_file = await storage.transcription_file(local_episode)
    trans_file.parent.mkdir(parents=True, exist_ok=True)

    # Copy test transcription content
    import shutil

    shutil.copy(jobs_csv_path, trans_file)

    # Set up embeddings
    from voogle import settings
    provider = embedding.get_embeddings_provider()
    qdrant_client = vector.get_configured_client()
    collection_name = vector.get_collection_name(settings.settings.embeddings_provider)

    vector.ensure_collection(
        qdrant_client, collection_name, provider.get_embedding_dimension()
    )

    # Calculate and store embeddings
    tr = transcription.read_transcription(trans_file)
    embs, fragments = embedding._transcription_embeddings(
        tr, provider, embedding.DEFAULT_FRAGMENT_WORDS
    )
    await vector.add_episode(
        local_episode, qdrant_client, embs, collection_name, fragments
    )

    # Query for content from the Steve Jobs speech
    response = client.get("/media/query?query_text=stay+hungry&n_results=5")
    assert response.status_code == 200

    results = response.json()
    assert len(results) > 0, "Expected query results for local episode"

    # Find result from our local channel
    local_results = [r for r in results if r["channel"]["kind"] == "local"]
    assert len(local_results) > 0, "Expected results from local channel"

    # Verify media_url starts with /local/
    for result in local_results:
        assert result["media_url"].startswith("/local/"), (
            f"Expected media_url to start with '/local/', got: {result['media_url']}"
        )
