# Copyright (c) 2023 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

import pytest
from voogle import models, storage

pytestmark = pytest.mark.component


@pytest.mark.description("Verifies storage path generation for channels and episodes")
async def test_episodes(channel: models.media.Channel) -> None:
    # Verify channel path is generated correctly (no longer checking for old 'kaizen' name)
    channel_path = storage.channel_path(channel)
    assert "test-channel" in str(channel_path)

    # Verify we have episodes
    assert await channel.episodes.count() == 5

    # Test path generation for episodes (component test - no need to access actual files)
    ep = await channel.episodes.first()
    trfile = await storage.transcription_file(ep)
    assert ".csv" in str(trfile)
    epfile = await storage.episode_file(ep)
    assert ".mp3" in str(epfile)
    assert trfile.stem == epfile.stem
    # Note: Not testing file.exists() since these are mock episodes without actual files
