# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Integration tests for Qdrant indexing flow (S3 spec).

Tests the complete indexing pipeline:
1. Episodes with transcribed=True, embeddings=False are indexed
2. Collection is auto-created if it doesn't exist
3. Indexed episodes can be searched via semantic search

These tests use vector.add_episode directly (avoiding Redis dependency from tasks module).
"""

import pytest
from voogle import embedding, models, storage, transcription, vector


pytestmark = pytest.mark.integration


@pytest.mark.description("Tests indexing updates episode embeddings flag")
async def test_add_episode_updates_embeddings_flag(
    fake_episode: models.media.Episode,
) -> None:
    """Test vector.add_episode sets embeddings=True after indexing."""
    # Verify initial state: transcribed but not indexed
    assert fake_episode.transcribed is True
    assert fake_episode.embeddings is False

    # Setup: get provider and client
    provider = embedding.get_embeddings_provider()
    client = vector.get_client()  # In-memory client for tests
    collection_name = vector.DEFAULT_COLLECTION

    # Ensure collection exists
    vector.ensure_collection(client, collection_name, provider.get_embedding_dimension())

    # Calculate embeddings and store in Qdrant
    tr = transcription.read_transcription(await storage.transcription_file(fake_episode))
    embs, fragments = embedding._transcription_embeddings(
        tr, provider, embedding.DEFAULT_FRAGMENT_WORDS
    )
    await vector.add_episode(fake_episode, client, embs, collection_name, fragments, provider)

    # Verify episode is now indexed (add_episode sets embeddings=True)
    assert fake_episode.embeddings is True

    # Also verify from database
    updated_episode = await models.Episode.objects.get(pk=fake_episode.pk)
    assert updated_episode.embeddings is True


@pytest.mark.description("Tests that ensure_collection creates collection if missing")
async def test_ensure_collection_creates_collection_if_missing() -> None:
    """Test ensure_collection creates the collection on first call."""
    client = vector.get_client()  # In-memory client for tests
    collection_name = "test-ensure-collection"
    dimension = 384

    # Collection should not exist initially
    assert not client.collection_exists(collection_name)

    # Call ensure_collection
    vector.ensure_collection(client, collection_name, dimension)

    # Collection should now exist
    assert client.collection_exists(collection_name)


@pytest.mark.description("Tests that ensure_collection is idempotent")
async def test_ensure_collection_is_idempotent() -> None:
    """Test ensure_collection can be called multiple times safely."""
    client = vector.get_client()
    collection_name = "test-idempotent"
    dimension = 384

    # Call ensure_collection multiple times
    vector.ensure_collection(client, collection_name, dimension)
    vector.ensure_collection(client, collection_name, dimension)
    vector.ensure_collection(client, collection_name, dimension)

    # Collection should exist
    assert client.collection_exists(collection_name)


@pytest.mark.description("Tests end-to-end indexing and search flow")
async def test_indexed_episodes_are_searchable(
    fake_episode: models.media.Episode,
) -> None:
    """Test that indexed episodes appear in search results."""
    # Setup: get provider and client
    provider = embedding.get_embeddings_provider()
    client = vector.get_client()  # In-memory client for tests
    collection_name = vector.DEFAULT_COLLECTION

    # Ensure collection exists
    vector.ensure_collection(client, collection_name, provider.get_embedding_dimension())

    # Calculate embeddings and store in Qdrant
    tr = transcription.read_transcription(await storage.transcription_file(fake_episode))
    embs, fragments = embedding._transcription_embeddings(
        tr, provider, embedding.DEFAULT_FRAGMENT_WORDS
    )
    await vector.add_episode(fake_episode, client, embs, collection_name, fragments)

    # Search for content from the golf transcription
    query_embedding = embedding.text2embedding("playing golf tournament", provider)
    results = vector.search(client, query_embedding, collection_name, num_results=5)

    # Should find results
    assert len(results) > 0

    # Results should have valid structure
    for result in results:
        assert result.score > 0
        assert result.text
        assert result.start_secs >= 0
        assert result.end_secs > result.start_secs


@pytest.mark.description("Tests that collection name matches provider")
async def test_collection_name_matches_provider() -> None:
    """Test that collection name is derived from provider."""
    # Default collection for local provider
    local_collection = vector.get_collection_name("local")
    assert local_collection == "vectordb"

    # OpenAI collection has suffix
    openai_collection = vector.get_collection_name("openai")
    assert openai_collection == "vectordb-openai"


@pytest.mark.description("Tests indexing stores embedding metadata in payload")
async def test_indexing_stores_metadata(
    fake_episode: models.media.Episode,
) -> None:
    """Test that embedding metadata is stored in Qdrant payload."""
    # Setup: get provider and client
    provider = embedding.get_embeddings_provider()
    client = vector.get_client()  # In-memory client for tests
    # Use a unique collection name to ensure we only have our data
    collection_name = "test-metadata-collection"

    # Create fresh collection (deletes existing if present)
    vector.create_collection(client, collection_name, provider.get_embedding_dimension())

    # Calculate embeddings and store with metadata (passing provider adds metadata)
    tr = transcription.read_transcription(await storage.transcription_file(fake_episode))
    embs, fragments = embedding._transcription_embeddings(
        tr, provider, embedding.DEFAULT_FRAGMENT_WORDS
    )
    await vector.add_episode(fake_episode, client, embs, collection_name, fragments, provider)

    # Scroll through points and verify metadata
    results, _ = client.scroll(collection_name=collection_name, limit=1)
    assert len(results) > 0

    payload = results[0].payload
    assert payload is not None
    assert "episode" in payload
    assert "channel" in payload
    assert "text" in payload
    assert "start_secs" in payload
    assert "end_secs" in payload
    assert "embedding_model" in payload
    assert "embedding_provider" in payload
    assert "embedded_at" in payload
