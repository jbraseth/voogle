# Copyright (c) 2022 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

from typing import Any
from unittest.mock import patch

import pytest
from starlette.testclient import TestClient
from voogle import embedding, models, storage, transcription, vector

pytestmark = pytest.mark.integration


@pytest.mark.description("Lists episodes via API and validates response structure")
def test_crud_episodes(channel: models.media.Channel, auth_client: TestClient) -> None:
    _unused = channel  # list all episodes (channel fixture creates 5 episodes)
    response = auth_client.get("/media/episode").json()
    assert response["total"] > 0
    assert response["items"][0]["id"]
    assert response["items"][0]["title"]


@pytest.mark.description(
    "Full CRUD operations for channels: list, filter, get, delete, and create"
)
async def test_crud_channels(
    channel: models.media.Channel, auth_client: TestClient
) -> None:
    # list all channels
    response = auth_client.get("/media/channel").json()
    assert response["total"] == 1
    assert len(response["items"]) > 0
    assert response["items"][0]["id"]
    assert response["items"][0]["title"]
    assert response["items"][0]["image"]
    # filter channels by title
    title = str(channel.title)
    response = auth_client.get(f"/media/channel?title__icontains={title[:10]}").json()
    assert response["total"] == 1
    cid = response["items"][0]["id"]
    assert "pk" not in response["items"][0]
    # get channel by its id
    response = auth_client.get(f"/media/channel/{cid}").json()
    assert response["id"] == cid
    # delete channel by its id
    response = auth_client.delete(f"/media/channel/{cid}").json()
    assert response["deleted_rows"] == 1
    response = auth_client.get("/media/channel").json()
    assert response["total"] == 0

    # create a new channel (mocked to avoid fetching real RSS feed)
    with patch("voogle.collection.crawler.get_or_create_channel") as mock_get_channel:
        # Create a new mock channel for this test
        new_channel = await models.Channel.objects.create(
            kind=models.media.ChannelKind.podcast.value,
            title=title,
            description="recreated test channel",
            language="en",
            url="https://example.com/podcast2",
            feed="https://example.com/mock-feed.xml",
            image="https://example.com/image2.jpg",
            local_folder="test-channel-2",
        )
        mock_get_channel.return_value = (True, new_channel)

        data = {"feed_url": "https://example.com/mock-feed.xml"}
        response = auth_client.post("/media/channel", json=data).json()
        assert response["id"]
        assert "pk" not in response


@pytest.mark.description("Query endpoint returns results with media_url field")
async def test_query_endpoint(
    aiolib: Any,  # noqa: ANN401
    fake_channel: models.media.Channel,
    fake_episode: models.media.Episode,
    client: TestClient,
) -> None:
    """Test that the query endpoint returns properly serialized results.

    This test creates embeddings inline (avoiding Redis dependency) and verifies:
    1. Query endpoint returns valid JSON
    2. Results include media_url field
    3. Episode and channel data are properly serialized (no pk field exposed)
    """
    # Set up embeddings using configured client (same as endpoint will use)
    from voogle import settings
    provider = embedding.get_embeddings_provider()
    qdrant_client = vector.get_configured_client()
    collection_name = vector.get_collection_name(settings.settings.embeddings_provider)

    vector.ensure_collection(
        qdrant_client, collection_name, provider.get_embedding_dimension()
    )

    # Calculate and store embeddings
    tr = transcription.read_transcription(await storage.transcription_file(fake_episode))
    embs, fragments = embedding._transcription_embeddings(
        tr, provider, embedding.DEFAULT_FRAGMENT_WORDS
    )
    await vector.add_episode(
        fake_episode, qdrant_client, embs, collection_name, fragments
    )

    response = client.get("/media/query?query_text=golf&n_results=5")
    assert response.status_code == 200

    results = response.json()
    assert isinstance(results, list)
    assert len(results) > 0

    # Verify result structure
    result = results[0]
    assert "text" in result
    assert "episode" in result
    assert "channel" in result
    assert "similarity" in result
    assert "start" in result
    assert "media_url" in result

    # Verify media_url is a string (either external URL or /local/ path)
    assert isinstance(result["media_url"], str)
    assert len(result["media_url"]) > 0

    # Verify pk is not exposed
    assert "pk" not in result["episode"]
    assert "pk" not in result["channel"]
