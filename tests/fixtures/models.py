# Copyright (c) 2022 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Model fixtures for testing."""

import pathlib
import shutil
from datetime import datetime, timezone
from typing import Any

import pytest
from voogle import embedding, models, storage, tasks, vector

EXAMPLE_CHANNEL_FEED = "https://feeds.simplecast.com/5dXzywz5"


@pytest.fixture(name="channel")
async def fixture_channel(aiolib: Any) -> models.media.Channel:  # type: ignore[misc]  # noqa: ANN401
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
            date=datetime.now(timezone.utc),
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
    aiolib: Any,  # noqa: ANN401
    fake_channel: models.Channel,
    golf_csv_path: pathlib.Path,
) -> models.media.Episode:
    episode = await models.media.Episode.objects.create(
        channel=fake_channel,
        title="golf-episode",
        description="example episode",
        date=datetime.now(timezone.utc),
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


@pytest.fixture(name="fake_episode_with_embeddings")
async def fixture_fake_episode_with_embeddings(
    aiolib: Any,  # noqa: ANN401
    fake_channel: models.Channel,
    golf_csv_path: pathlib.Path,
) -> models.media.Episode:
    """Create an episode with transcription AND embeddings calculated.

    This fixture is required for E2E tests that need search to return results.
    It:
    1. Creates a channel and episode
    2. Copies the transcription CSV file
    3. Calculates embeddings from the transcription
    4. Stores embeddings in Qdrant (in-memory for tests)

    After this fixture runs, queries like "golf" will return results.
    """
    episode = await models.media.Episode.objects.create(
        channel=fake_channel,
        title="golf-episode",
        description="example episode",
        date=datetime.now(timezone.utc),
        url="https://example.com/golf.mp3",  # Valid URL for player
        guid="golf-episode-001",
        transcribed=True,
    )

    # Copy transcription file to the data dir
    assert golf_csv_path.exists()
    dst = await storage.transcription_file(episode)
    dst.parent.mkdir(exist_ok=True, parents=True)
    shutil.copy(golf_csv_path, dst)

    # Calculate and store embeddings
    provider = embedding.get_embeddings_provider()
    client = vector.get_client()  # In-memory client for tests
    collection_name = vector.DEFAULT_COLLECTION

    # Ensure collection exists
    vector.ensure_collection(client, collection_name, provider.get_embedding_dimension())

    # Store embeddings for this episode
    await tasks.store_episode_embeddings(episode, provider, client, collection_name)

    return episode


@pytest.fixture(name="multi_channel_test_data")
async def fixture_multi_channel_test_data(
    aiolib: Any,  # noqa: ANN401
    golf_csv_path: pathlib.Path,
    jobs_csv_path: pathlib.Path,
) -> list[models.media.Episode]:
    """Create multiple channels with different transcription data for E2E tests.

    This fixture creates 2 channels with different content:
    1. Golf channel - episode with golf.csv transcription (about golf tournaments)
    2. Jobs channel - episode with jobs.csv transcription (Steve Jobs speech)

    Both episodes have embeddings calculated so they appear in search results.
    Use query "golf" to get golf results, "stay hungry" for jobs results.
    """
    # Get embedding provider and vector client
    provider = embedding.get_embeddings_provider()
    client = vector.get_client()  # In-memory client for tests
    collection_name = vector.DEFAULT_COLLECTION

    # Ensure collection exists
    vector.ensure_collection(client, collection_name, provider.get_embedding_dimension())

    episodes: list[models.media.Episode] = []

    # Channel 1: Golf podcast
    golf_channel = await models.Channel.objects.create(
        kind=models.media.ChannelKind.podcast.value,
        title="Golf Podcast",
        description="Podcast about golf tournaments and playing",
        language="en",
        url="https://example.com/golf-podcast",
        feed="https://example.com/golf-podcast/feed",
        image="https://example.com/golf-image.jpg",
        local_folder="golf-podcast",
    )

    golf_episode = await models.media.Episode.objects.create(
        channel=golf_channel,
        title="The Open Championship Discussion",
        description="Discussing the Open Championship golf tournament",
        date=datetime.now(timezone.utc),
        url="https://example.com/golf-podcast/episode1.mp3",
        guid="golf-episode-001",
        transcribed=True,
    )

    # Copy golf transcription
    assert golf_csv_path.exists()
    dst = await storage.transcription_file(golf_episode)
    dst.parent.mkdir(exist_ok=True, parents=True)
    shutil.copy(golf_csv_path, dst)

    # Store golf embeddings
    await tasks.store_episode_embeddings(golf_episode, provider, client, collection_name)
    episodes.append(golf_episode)

    # Channel 2: Jobs podcast (Steve Jobs speech)
    jobs_channel = await models.Channel.objects.create(
        kind=models.media.ChannelKind.podcast.value,
        title="Inspirational Speeches",
        description="Famous speeches and life lessons",
        language="en",
        url="https://example.com/speeches-podcast",
        feed="https://example.com/speeches-podcast/feed",
        image="https://example.com/speeches-image.jpg",
        local_folder="speeches-podcast",
    )

    jobs_episode = await models.media.Episode.objects.create(
        channel=jobs_channel,
        title="Steve Jobs Commencement Speech",
        description="Stay hungry, stay foolish - Stanford 2005",
        date=datetime.now(timezone.utc),
        url="https://example.com/speeches-podcast/jobs.mp3",
        guid="jobs-episode-001",
        transcribed=True,
    )

    # Copy jobs transcription
    assert jobs_csv_path.exists()
    dst = await storage.transcription_file(jobs_episode)
    dst.parent.mkdir(exist_ok=True, parents=True)
    shutil.copy(jobs_csv_path, dst)

    # Store jobs embeddings
    await tasks.store_episode_embeddings(jobs_episode, provider, client, collection_name)
    episodes.append(jobs_episode)

    return episodes
