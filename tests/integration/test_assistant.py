# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Integration tests for local assistant endpoint."""

from unittest.mock import MagicMock, patch

import pytest
from starlette.testclient import TestClient
from voogle import embedding, models, storage, transcription, vector

pytestmark = pytest.mark.integration

# TestClient uses "testclient" as the client host, so we need to allowlist it
# for tests that need to pass the localhost check
TESTCLIENT_ALLOWLIST = "testclient"


@pytest.mark.description("Feature disabled returns 503")
def test_feature_disabled_returns_503(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When LOCAL_ASSISTANT_ENABLED=false, endpoint returns 503."""
    from voogle import settings as settings_module

    monkeypatch.setattr(settings_module.settings, "local_assistant_enabled", False)

    response = client.get("/assistant/answer_local?query_text=test")

    assert response.status_code == 503
    assert "not enabled" in response.json()["detail"]


@pytest.mark.description("Feature enabled but CLI not found returns 503")
def test_cli_not_found_returns_503(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When feature enabled but no CLI found, returns 503."""
    from voogle import settings as settings_module

    monkeypatch.setattr(settings_module.settings, "local_assistant_enabled", True)
    # Allowlist testclient to pass the localhost check
    monkeypatch.setattr(
        settings_module.settings, "local_assistant_allowlist", TESTCLIENT_ALLOWLIST
    )

    with patch("voogle.routers.assistant.shutil.which", return_value=None):
        response = client.get("/assistant/answer_local?query_text=test")

    assert response.status_code == 503
    assert "CLI" in response.json()["detail"]
    assert "PATH" in response.json()["detail"]


@pytest.mark.description("Full flow with mocked CLI execution")
async def test_answer_local_full_flow(
    fake_channel: models.media.Channel,
    fake_episode: models.media.Episode,
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test complete flow: search → prompt → mocked CLI → response."""
    from voogle import settings as settings_module

    # Enable feature and allowlist testclient
    monkeypatch.setattr(settings_module.settings, "local_assistant_enabled", True)
    monkeypatch.setattr(
        settings_module.settings, "local_assistant_allowlist", TESTCLIENT_ALLOWLIST
    )
    monkeypatch.setattr(settings_module.settings, "local_assistant_cli_timeout", 60)

    # Set up embeddings using configured client
    provider = embedding.get_embeddings_provider()
    qdrant_client = vector.get_configured_client()
    collection_name = vector.get_collection_name(
        settings_module.settings.embeddings_provider
    )

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

    # Mock CLI execution
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Based on the sources, golf is a sport played outdoors. [1]"
    mock_result.stderr = ""

    def mock_which(cmd: str) -> str | None:
        return "/usr/bin/claude" if cmd == "claude" else None

    with patch("voogle.routers.assistant.shutil.which", side_effect=mock_which):
        with patch("voogle.routers.assistant.subprocess.run", return_value=mock_result):
            response = client.get("/assistant/answer_local?query_text=golf&k=3")

    assert response.status_code == 200

    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert "cli_used" in data
    assert "query" in data

    assert data["cli_used"] == "claude"
    assert data["query"] == "golf"
    assert len(data["sources"]) > 0

    # Verify source structure
    source = data["sources"][0]
    assert "index" in source
    assert "episode_title" in source
    assert "channel_title" in source
    assert "start_secs" in source
    assert "end_secs" in source
    assert "text" in source
    assert "media_url" in source


@pytest.mark.description("Empty search results handled gracefully")
async def test_empty_search_results(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When search returns no results, response is still valid."""
    from voogle import settings as settings_module

    # Enable feature and allowlist testclient
    monkeypatch.setattr(settings_module.settings, "local_assistant_enabled", True)
    monkeypatch.setattr(
        settings_module.settings, "local_assistant_allowlist", TESTCLIENT_ALLOWLIST
    )
    monkeypatch.setattr(settings_module.settings, "local_assistant_cli_timeout", 60)

    # Mock CLI execution
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "No relevant sources found to answer this question."
    mock_result.stderr = ""

    def mock_which(cmd: str) -> str | None:
        return "/usr/bin/claude" if cmd == "claude" else None

    with patch("voogle.routers.assistant.shutil.which", side_effect=mock_which):
        with patch("voogle.routers.assistant.subprocess.run", return_value=mock_result):
            # Mock search to return empty results
            with patch("voogle.routers.assistant.tasks.search", return_value=[]):
                response = client.get(
                    "/assistant/answer_local?query_text=xyznonexistentquery123"
                )

    assert response.status_code == 200

    data = response.json()
    assert data["sources"] == []  # No sources found
    assert data["answer"] == "No relevant sources found to answer this question."


@pytest.mark.description("CLI timeout is enforced")
async def test_cli_timeout_enforced(
    fake_channel: models.media.Channel,
    fake_episode: models.media.Episode,
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that subprocess.TimeoutExpired is handled properly."""
    import subprocess

    from voogle import settings as settings_module

    # Enable feature with short timeout and allowlist testclient
    monkeypatch.setattr(settings_module.settings, "local_assistant_enabled", True)
    monkeypatch.setattr(
        settings_module.settings, "local_assistant_allowlist", TESTCLIENT_ALLOWLIST
    )
    monkeypatch.setattr(settings_module.settings, "local_assistant_cli_timeout", 1)

    # Set up embeddings
    provider = embedding.get_embeddings_provider()
    qdrant_client = vector.get_configured_client()
    collection_name = vector.get_collection_name(
        settings_module.settings.embeddings_provider
    )

    vector.ensure_collection(
        qdrant_client, collection_name, provider.get_embedding_dimension()
    )

    tr = transcription.read_transcription(await storage.transcription_file(fake_episode))
    embs, fragments = embedding._transcription_embeddings(
        tr, provider, embedding.DEFAULT_FRAGMENT_WORDS
    )
    await vector.add_episode(
        fake_episode, qdrant_client, embs, collection_name, fragments
    )

    def mock_which(cmd: str) -> str | None:
        return "/usr/bin/claude" if cmd == "claude" else None

    with patch("voogle.routers.assistant.shutil.which", side_effect=mock_which):
        with patch(
            "voogle.routers.assistant.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="claude", timeout=1),
        ):
            response = client.get("/assistant/answer_local?query_text=golf")

    assert response.status_code == 500
    assert "timed out" in response.json()["detail"]


@pytest.mark.description("Non-localhost without allowlist returns 403")
def test_non_localhost_returns_403(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When feature enabled but request is not from localhost or allowlist, returns 403."""
    from voogle import settings as settings_module

    monkeypatch.setattr(settings_module.settings, "local_assistant_enabled", True)
    # Empty allowlist - testclient should be rejected
    monkeypatch.setattr(settings_module.settings, "local_assistant_allowlist", "")

    response = client.get("/assistant/answer_local?query_text=test")

    assert response.status_code == 403
    assert "not localhost or allowlisted" in response.json()["detail"]


@pytest.mark.description("Allowlisted IP is accepted")
def test_allowlisted_ip_accepted(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When feature enabled and IP is in allowlist, request proceeds to CLI check."""
    from voogle import settings as settings_module

    # Enable feature with allowlist for testclient
    monkeypatch.setattr(settings_module.settings, "local_assistant_enabled", True)
    monkeypatch.setattr(
        settings_module.settings, "local_assistant_allowlist", TESTCLIENT_ALLOWLIST
    )

    with patch("voogle.routers.assistant.shutil.which", return_value=None):
        response = client.get("/assistant/answer_local?query_text=test")

    # Should reach CLI check (503), not IP check (403)
    assert response.status_code == 503
    assert "CLI" in response.json()["detail"]
    assert "PATH" in response.json()["detail"]
