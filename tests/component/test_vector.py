# Copyright (c) 2023 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

from collections.abc import Generator
from unittest.mock import Mock, patch

import numpy as np
import pytest
from voogle import embedding, models, storage, transcription, vector
from voogle.chunking import ChunkingConfig

pytestmark = pytest.mark.component


@pytest.fixture(name="local_provider")
def fixture_local_provider() -> embedding.LocalEmbeddingsProvider:
    """Fixture for local embeddings provider."""
    model = embedding.load_embeddings_model(embedding.DEFAULT_EMBEDDINGS_MODEL)
    return embedding.LocalEmbeddingsProvider(model, model_name=embedding.DEFAULT_EMBEDDINGS_MODEL)


@pytest.fixture(name="mock_openai_provider")
def fixture_mock_openai_provider() -> Generator[embedding.OpenAIEmbeddingsProvider, None, None]:
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


@pytest.mark.description("Tests fragment overlap creates more fragments with overlapping text")
async def test_calculate_fragments_with_overlap(
    fake_episode: models.media.Episode,
) -> None:
    tr = transcription.read_transcription(
        await storage.transcription_file(fake_episode)
    )
    # Without overlap
    config_no_overlap = ChunkingConfig(
        chunk_size_words=40,
        chunk_overlap_words=0,
        min_chunk_length_words=1,
    )
    fragments_no_overlap = embedding.calculate_fragments(tr, config_no_overlap)

    # With overlap - should create more fragments
    config_with_overlap = ChunkingConfig(
        chunk_size_words=40,
        chunk_overlap_words=20,
        min_chunk_length_words=1,
    )
    fragments_with_overlap = embedding.calculate_fragments(tr, config_with_overlap)

    # With overlap we get more fragments due to repeated text
    assert len(fragments_with_overlap) > len(fragments_no_overlap)


@pytest.mark.description("Tests minimum chunk length filtering")
def test_calculate_fragments_min_length() -> None:
    # Create a transcription with short final segment
    tr: transcription.Transcription = [
        (0.0, 10.0, "This is a sentence with enough words to make a fragment. "),
        (10.0, 20.0, "Another sentence with many words that extends the text. "),
        (20.0, 30.0, "More content here for the transcription to continue. "),
        (30.0, 35.0, "Short. "),  # Only 1 word - should be filtered
    ]

    # Low min length - includes final fragment
    config_low_min = ChunkingConfig(
        chunk_size_words=20,
        chunk_overlap_words=0,
        min_chunk_length_words=1,
    )
    fragments_low = embedding.calculate_fragments(tr, config_low_min)

    # High min length - may filter final fragment
    config_high_min = ChunkingConfig(
        chunk_size_words=20,
        chunk_overlap_words=0,
        min_chunk_length_words=5,
    )
    fragments_high = embedding.calculate_fragments(tr, config_high_min)

    # The high min length should filter out tiny fragments
    assert len(fragments_low) >= len(fragments_high)


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


@pytest.mark.description("Tests that LocalEmbeddingsProvider exposes correct properties")
def test_local_provider_properties(
    local_provider: embedding.LocalEmbeddingsProvider,
) -> None:
    """Verify protocol properties are implemented."""
    assert local_provider.model_name == embedding.DEFAULT_EMBEDDINGS_MODEL
    assert local_provider.provider_name == "local"
    assert local_provider.get_embedding_dimension() == 384


@pytest.mark.description("Tests that OpenAI provider exposes correct properties")
def test_openai_provider_properties(
    mock_openai_provider: embedding.OpenAIEmbeddingsProvider,
) -> None:
    """Verify OpenAI provider properties."""
    assert mock_openai_provider.model_name == "text-embedding-3-small"
    assert mock_openai_provider.provider_name == "openai"
    assert mock_openai_provider.get_embedding_dimension() == 1536


@pytest.mark.description("Tests that embedding metadata is added to Qdrant payload")
async def test_metadata_in_payload(
    fake_episode: models.media.Episode,
    local_provider: embedding.LocalEmbeddingsProvider,
) -> None:
    """Verify embedding metadata is stored in Qdrant payload."""
    from datetime import datetime

    client = vector.get_client()
    dbname = "test-metadata"

    tr = transcription.read_transcription(
        await storage.transcription_file(fake_episode)
    )
    embs, fragments = embedding._transcription_embeddings(
        tr, local_provider, embedding.DEFAULT_FRAGMENT_WORDS
    )

    vector.ensure_collection(client, dbname, local_provider.get_embedding_dimension())
    await vector.add_episode(
        fake_episode, client, embs, dbname, fragments, local_provider
    )

    # Verify metadata
    results, _ = client.scroll(collection_name=dbname, limit=1)
    assert len(results) > 0
    payload = results[0].payload

    assert payload["embedding_model"] == embedding.DEFAULT_EMBEDDINGS_MODEL
    assert payload["embedding_provider"] == "local"
    assert "embedded_at" in payload
    # Verify timestamp is valid ISO format
    datetime.fromisoformat(payload["embedded_at"])


@pytest.mark.description("Tests explicit provider factory function")
def test_get_embeddings_provider_by_name_local() -> None:
    """Verify explicit local provider creation works."""
    provider = embedding.get_embeddings_provider_by_name("local")
    assert provider.provider_name == "local"
    assert provider.model_name == embedding.DEFAULT_EMBEDDINGS_MODEL


@pytest.mark.description("Tests that unknown provider raises ValueError")
def test_get_embeddings_provider_by_name_invalid() -> None:
    """Verify invalid provider name raises error."""
    with pytest.raises(ValueError, match="Unknown provider"):
        embedding.get_embeddings_provider_by_name("invalid")


# --- 2D Projection Tests ---


@pytest.mark.description("Tests 2D projection with typical result set")
def test_project_embeddings_2d_basic() -> None:
    """Test basic 2D projection with mock embeddings."""
    # Create mock query embedding
    query_emb = np.random.randn(1, 384).astype(np.float32)

    # Create mock result embeddings (5 results)
    result_embs = [np.random.randn(384).astype(np.float32) for _ in range(5)]

    # Create mock QueryResponse objects
    results = [
        vector.QueryResponse(
            score=0.9 - i * 0.1,
            episode=i,
            channel=1,
            start_secs=i * 60,
            end_secs=i * 60 + 30,
            text=f"This is the text for result {i} with some content.",
        )
        for i in range(5)
    ]

    projection = vector.project_embeddings_2d(query_emb, result_embs, results)

    # Verify structure
    assert len(projection.points) == 5
    assert projection.query_point is not None
    assert len(projection.query_point) == 2

    # Verify each point has correct structure
    for i, point in enumerate(projection.points):
        assert isinstance(point.x, float)
        assert isinstance(point.y, float)
        assert point.fragment_id == f"{i}_{i * 60}"
        assert point.score == results[i].score


@pytest.mark.description("Tests projection fails with fewer than 2 results")
def test_project_embeddings_2d_too_few_results() -> None:
    """Test projection raises error with fewer than 2 results."""
    query_emb = np.random.randn(1, 384).astype(np.float32)
    result_embs = [np.random.randn(384).astype(np.float32)]
    results = [
        vector.QueryResponse(
            score=0.9,
            episode=1,
            channel=1,
            start_secs=0,
            end_secs=30,
            text="Single result text.",
        )
    ]

    with pytest.raises(ValueError, match="At least 2 result embeddings required"):
        vector.project_embeddings_2d(query_emb, result_embs, results)


@pytest.mark.description("Tests projection fails when all embeddings are identical")
def test_project_embeddings_2d_identical_embeddings() -> None:
    """Test projection raises error when all embeddings are identical."""
    # Create identical embeddings
    identical = np.ones(384).astype(np.float32)
    query_emb = identical.reshape(1, -1)
    result_embs = [identical.copy() for _ in range(3)]

    results = [
        vector.QueryResponse(
            score=0.9 - i * 0.1,
            episode=i,
            channel=1,
            start_secs=i * 60,
            end_secs=i * 60 + 30,
            text=f"Result {i}",
        )
        for i in range(3)
    ]

    with pytest.raises(ValueError, match="All embeddings are identical"):
        vector.project_embeddings_2d(query_emb, result_embs, results)


@pytest.mark.description("Tests projection with 20 results (typical use case)")
def test_project_embeddings_2d_typical_size() -> None:
    """Test projection with 20 results (typical visualization size)."""
    query_emb = np.random.randn(1, 384).astype(np.float32)
    result_embs = [np.random.randn(384).astype(np.float32) for _ in range(20)]
    results = [
        vector.QueryResponse(
            score=0.9 - i * 0.02,
            episode=i,
            channel=1,
            start_secs=i * 60,
            end_secs=i * 60 + 30,
            text=f"Result text number {i} with more content here.",
        )
        for i in range(20)
    ]

    projection = vector.project_embeddings_2d(query_emb, result_embs, results)

    assert len(projection.points) == 20
    assert projection.query_point is not None


@pytest.mark.description("Tests projection with exactly 2 results (edge case)")
def test_project_embeddings_2d_minimum_results() -> None:
    """Test projection with exactly 2 results (minimum required)."""
    query_emb = np.random.randn(1, 384).astype(np.float32)
    result_embs = [np.random.randn(384).astype(np.float32) for _ in range(2)]
    results = [
        vector.QueryResponse(
            score=0.9 - i * 0.1,
            episode=i,
            channel=1,
            start_secs=i * 60,
            end_secs=i * 60 + 30,
            text=f"Result {i}",
        )
        for i in range(2)
    ]

    projection = vector.project_embeddings_2d(query_emb, result_embs, results)

    assert len(projection.points) == 2
    assert projection.query_point is not None
    # All points should have valid coordinates
    for point in projection.points:
        assert not np.isnan(point.x)
        assert not np.isnan(point.y)


@pytest.mark.description("Tests that search_with_vectors returns embedding vectors")
async def test_search_with_vectors(
    fake_episode: models.media.Episode,
    local_provider: embedding.LocalEmbeddingsProvider,
) -> None:
    """Test that search_with_vectors returns result vectors for visualization."""
    client = vector.get_client()
    dbname = "test-vectors"

    # Load and store embeddings
    tr = transcription.read_transcription(
        await storage.transcription_file(fake_episode)
    )
    embs, fragments = embedding._transcription_embeddings(
        tr, local_provider, embedding.DEFAULT_FRAGMENT_WORDS
    )

    vector.ensure_collection(client, dbname, local_provider.get_embedding_dimension())
    await vector.add_episode(fake_episode, client, embs, dbname, fragments)

    # Search with vectors
    query = embedding.text2embedding("playing golf with other people", local_provider)
    results = vector.search_with_vectors(client, query, dbname, 3)

    assert len(results) == 3
    for r in results:
        assert r.response.text
        assert r.response.score
        assert isinstance(r.vector, np.ndarray)
        assert r.vector.shape == (384,)  # Local model dimension
