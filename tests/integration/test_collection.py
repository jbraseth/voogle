# Copyright (c) 2023 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

import pytest
from voogle import collection

pytestmark = pytest.mark.integration


@pytest.mark.description(
    "Validates default podcast channels can be read and have episodes"
)
def test_default_channels() -> None:
    channels = collection.default_channels()
    assert len(channels) > 0
    for ch in channels[-5:]:
        channel = collection.read_channel(ch["url"])
        assert channel is not None
        episodes = collection.read_episodes(channel)
        assert len(episodes) > 0


@pytest.mark.description(
    "Tests channel creation, retrieval, and episode updates from RSS feeds"
)
async def test_read_channel_and_its_episodes() -> None:
    for i, podcast in enumerate(collection.default_channels()[:5]):
        created, retrieved = await collection.get_or_create_channel(podcast["url"])
        assert created
        assert retrieved is not None
        assert retrieved.kind == "podcast"
        created, retrieved = await collection.get_or_create_channel(podcast["url"])
        assert not created
        assert retrieved is not None
        for f in [
            retrieved.title,
            retrieved.description,
            retrieved.url,
            retrieved.feed,
            retrieved.image,
        ]:
            assert len(str(f)) > 0
        if i == 0:
            assert (await collection.update_channel(retrieved)) > 0
            assert (await collection.update_channel(retrieved)) == 0
