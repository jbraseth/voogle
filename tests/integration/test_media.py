# Copyright (c) 2022 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

from unittest.mock import patch

import pytest

from starlette.testclient import TestClient
from voogle import models

pytestmark = pytest.mark.integration


@pytest.mark.description("Lists episodes via API and validates response structure")
def test_crud_episodes(channel: models.media.Channel, auth_client: TestClient) -> None:
    _unused = channel  # list all episodes (channel fixture creates 5 episodes)
    response = auth_client.get("/media/episode").json()
    assert response["total"] > 0
    assert response["items"][0]["id"]
    assert response["items"][0]["title"]


@pytest.mark.description("Full CRUD operations for channels: list, filter, get, delete, and create")
async def test_crud_channels(channel: models.media.Channel, auth_client: TestClient) -> None:
    # list all channels
    response = auth_client.get("/media/channel").json()
    assert response["total"] == 1
    assert len(response["items"]) > 0
    assert response["items"][0]["id"]
    assert response["items"][0]["title"]
    assert response["items"][0]["image"]
    # filter channels by title
    title = channel.title
    response = auth_client.get(
        f"/media/channel?title__icontains={title[:10]}"
    ).json()
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
