# Copyright (c) 2023 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

import pytest
from unittest.mock import Mock, patch

from voogle import embedding, models, storage, transcription, vector

pytestmark = pytest.mark.component


@pytest.fixture
def local_provider() -> embedding.LocalEmbeddingsProvider:
    """Fixture for local embeddings provider."""
    model = embedding.load_embeddings_model(embedding.DEFAULT_EMBEDDINGS_MODEL)
    return embedding.LocalEmbeddingsProvider(model)


@pytest.fixture
def mock_openai_provider() -> embedding.OpenAIEmbeddingsProvider:
    """Fixture for mocked OpenAI provider."""
    with patch("openai.OpenAI") as mock_client:
        # Mock response for batch of embeddings
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1] * 1536) for _ in range(100)]
        mock_response.usage = Mock(total_tokens=100)
        mock_client.return_value.embeddings.create.return_value = mock_response

        provider = embedding.OpenAIEmbeddingsProvider(
            api_key="test-key",
            model="text-embedding-3-small",
        )
        yield provider


@pytest.mark.description("Tests text fragmentation into embeddings with different word counts")
async def test_calculate_fragments(
    jobs_transcription: transcription.Transcription,
    fake_episode: models.media.Episode,
) -> None:
    embs = embedding.calculate_fragments(jobs_transcription, 20)
    assert len(embs) == 2
    tr = transcription.read_transcription(
        await storage.transcription_file(fake_episode)
    )
    embs = embedding.calculate_fragments(tr, 20)
    assert len(embs) == 101

    embs = embedding.calculate_fragments(tr, 40)
    assert len(embs) == 54


@pytest.mark.description("Tests full embedding pipeline: calculate, store, and semantic search in vector DB")
async def test_store_embeddings(
    fake_episode: models.media.Episode,
    local_provider: embedding.LocalEmbeddingsProvider,
) -> None:
    # load vector database
    client = vector.get_client()

    # load episode and calculate its embeddings
    tr = transcription.read_transcription(
        await storage.transcription_file(fake_episode)
    )
    embs, fragments = embedding._transcription_embeddings(
        tr, local_provider, embedding.DEFAULT_FRAGMENT_WORDS
    )
    assert len(fragments) == 54
    assert len(embs) == 54
    assert embs[0].shape == (384,)  # Local model dimension

    # store embeddings
    dbname = "test-local"
    vector.ensure_collection(client, dbname, local_provider.get_embedding_dimension())
    vector.ensure_collection(client, dbname, local_provider.get_embedding_dimension())
    await vector.add_episode(fake_episode, client, embs, dbname, fragments)

    # example query
    query = embedding.text2embedding("playing golf with other people", local_provider)
    results = vector.search(client, query, dbname, 3)
    assert len(results) == 3
    for r in results:
        assert r.text
        assert r.score
        assert r.start_secs
        assert r.end_secs
