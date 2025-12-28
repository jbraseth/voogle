# Copyright (c) 2022 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Model fixtures for testing."""

import pathlib
import shutil
from datetime import datetime

import pytest
from voogle import models, storage

EXAMPLE_CHANNEL_FEED = "https://feeds.simplecast.com/5dXzywz5"


@pytest.fixture(name="channel")
async def fixture_channel(aiolib) -> models.media.Channel:  # type: ignore[misc]
    # Don't fetch real RSS feed in tests - create mock channel instead
    ch = await models.Channel.objects.create(
        kind=models.media.ChannelKind.podcast.value,
        title="test-channel",
        description="test podcast channel",
        language="en",
        url="https://example.com/podcast",
        feed=EXAMPLE_CHANNEL_FEED,
        image="https://example.com/image.jpg",
        local_folder="test-channel",
    )
    # Create 5 mock episodes for tests that need them
    for i in range(5):
        await models.Episode.objects.create(
            channel=ch,
            title=f"test-episode-{i}",
            description=f"test episode {i}",
            date=datetime.now(),
            url=f"https://example.com/episode{i}.mp3",
            guid=f"episode-{i}",
        )
    return ch


@pytest.fixture(name="fake_channel")
async def fixture_fake_channel() -> models.Channel:
    return await models.Channel.objects.create(
        kind=models.media.ChannelKind.podcast.value,
        title="golf-channel",
        description="golf channel",
        language="en",
        url="foo",
        feed="foo",
        image="foo",
        local_folder="",
    )


@pytest.fixture(name="fake_episode")
async def fixture_fake_episode(
    aiolib, fake_channel, golf_csv_path: pathlib.Path
) -> models.media.Episode:
    episode = await models.media.Episode.objects.create(
        channel=fake_channel,
        title="golf-episode",
        description="example episode",
        date=datetime.now(),
        url="bar",
        guid="bar",
        transcribed=True,
    )
    # move transcription file to the data dir
    assert golf_csv_path.exists()
    dst = await storage.transcription_file(episode)
    dst.parent.mkdir(exist_ok=True, parents=True)
    shutil.copy(golf_csv_path, dst)
    return episode
