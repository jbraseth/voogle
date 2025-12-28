# Copyright (c) 2022 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

import os
import pathlib
import shutil
from datetime import datetime
from typing import Any, Generator

import pytest
import sqlalchemy
from starlette.testclient import TestClient
from voogle import auth, db, main, models, storage, transcription
from voogle.settings import settings

EXAMPLE_CHANNEL_FEED = "https://feeds.simplecast.com/5dXzywz5"


@pytest.fixture(autouse=True, name="create_test_database")
def fixture_create_test_database() -> Generator[None, Any, Any]:
    """Automatically create the test database and remove it at the
    end.
    """
    # ensure the correct tests env var exists
    assert os.environ["ENVIRONMENT"] == "test"
    engine = sqlalchemy.create_engine(
        db.get_db_url(), connect_args={"check_same_thread": False}
    )
    db.metadata.create_all(engine)
    yield
    db.metadata.drop_all(engine)


@pytest.fixture(name="client")
def fixture_client() -> TestClient:
    return TestClient(main.app)


@pytest.fixture(name="auth_client")
async def fixture_auth_client() -> TestClient:  # type: ignore
    client = TestClient(main.app)
    await models.users.User.objects.create(
        email="test@acme.com",
        username=settings.admin_username,
        hashed_password=auth.get_password_hash("examplepassword"),
        admin=True,
    )
    login_data = {
        "username": settings.admin_username,
        "password": "examplepassword",
    }
    response = client.post("/users/token/", data=login_data).json()
    token = response["access_token"]
    return TestClient(main.app, headers={"Authorization": f"Bearer {token}"})


@pytest.fixture(name="channel")
async def fixture_channel(aiolib) -> models.media.Channel:  # type: ignore
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


@pytest.fixture(name="tests_data_dir")
def fixture_tests_data_dir() -> pathlib.Path:
    # Use relative path that works locally and in Docker
    return pathlib.Path("tests/data")


@pytest.fixture(name="jobs_transcription")
def fixture_jobs_transcription() -> transcription.Transcription:
    return [
        (0.0, 3.2, " It was their farewell message as they signed off."),
        (3.2, 6.26, " Stay hungry, stay foolish."),
        (6.26, 9.78, " And I have always wished that for myself."),
        (9.78, 13.3, " And now, as you graduate to begin anew,"),
        (13.3, 15.1, " I wish that for you."),
        (15.1, 17.5, " Stay hungry, stay foolish."),
    ]


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
async def fixture_fake_episode(aiolib, fake_channel, tests_data_dir) -> models.media.Episode:
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
    src = tests_data_dir / "golf.csv"
    assert src.exists()
    dst = await storage.transcription_file(episode)
    dst.parent.mkdir(exist_ok=True, parents=True)
    shutil.copy(src, dst)
    return episode


@pytest.fixture(autouse=True, scope="session", name="clean_environment")
def fixture_clean_environment():
    yield
    data = settings.data_dir
    if "test" in str(data):
        shutil.rmtree(data, ignore_errors=True)
    else:
        assert False, "Not using test folder as data dir"
