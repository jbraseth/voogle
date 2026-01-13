# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Infrastructure fixtures for integration testing.

Provides pytest fixtures for:
- Qdrant vector database (in-memory for isolation)
- Embedding provider mocks (deterministic, fast)
- Collection management helpers

These fixtures enable integration tests to run without external dependencies
while still exercising the full indexing and search pipeline.
"""

from typing import Generator

import numpy as np
import pytest
import qdrant_client
from qdrant_client import models

from voogle import embedding, vector


class MockEmbeddingsProvider:
    """Deterministic mock embeddings provider for testing.

    Generates reproducible embeddings based on text hash, enabling
    tests to verify search behavior without model loading overhead.

    Implements the EmbeddingsProvider protocol from voogle.embedding.
    """

    def __init__(self, dimension: int = 384):
        self._dimension = dimension
        self._model_name = "mock-embeddings"
        self._provider_name = "mock"
        self._encode_calls: list[list[str]] = []

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def provider_name(self) -> str:
        return self._provider_name

    def get_embedding_dimension(self) -> int:
        return self._dimension

    def encode_texts(self, texts: list[str]) -> np.ndarray:
        """Generate deterministic embeddings from text hashes."""
        self._encode_calls.append(texts)
        embeddings = []
        for text in texts:
            # Create deterministic embedding from text hash
            emb = self._text_to_embedding(text)
            embeddings.append(emb)
        return np.array(embeddings)

    def _text_to_embedding(self, text: str) -> np.ndarray:
        """Convert text to deterministic embedding vector."""
        import hashlib

        # Use SHA256 for longer hash, then convert to float values
        h = hashlib.sha256(text.encode()).digest()

        # Expand hash to fill dimension
        values = []
        for i in range(self._dimension):
            byte_idx = i % len(h)
            values.append((h[byte_idx] + i) / 255.0 - 0.5)

        # Normalize to unit vector
        arr = np.array(values)
        norm = np.linalg.norm(arr)
        if norm > 0:
            arr = arr / norm
        return arr

    def get_encode_calls(self) -> list[list[str]]:
        """Return history of encode_texts calls for verification."""
        return self._encode_calls

    def encode_single(self, text: str) -> np.ndarray:
        """Encode a single text into an embedding (used for queries)."""
        return self.encode_texts([text])

    def reset_calls(self) -> None:
        """Reset call history."""
        self._encode_calls = []


@pytest.fixture(name="mock_embeddings_provider")
def fixture_mock_embeddings_provider() -> MockEmbeddingsProvider:
    """Return a mock embeddings provider for deterministic testing."""
    return MockEmbeddingsProvider()


@pytest.fixture(name="qdrant_memory_client")
def fixture_qdrant_memory_client() -> Generator[qdrant_client.QdrantClient, None, None]:
    """Return an in-memory Qdrant client for isolated testing.

    Each test gets a fresh in-memory instance to ensure isolation.
    """
    # Clear the cached client to ensure fresh instance
    vector.get_client.cache_clear()

    client = qdrant_client.QdrantClient(":memory:")
    yield client

    # Clean up
    vector.get_client.cache_clear()


@pytest.fixture(name="qdrant_test_collection")
def fixture_qdrant_test_collection(
    qdrant_memory_client: qdrant_client.QdrantClient,
    mock_embeddings_provider: MockEmbeddingsProvider,
) -> Generator[str, None, None]:
    """Create a test collection and return its name.

    The collection is automatically cleaned up after the test.
    """
    collection_name = "test-collection"
    dimension = mock_embeddings_provider.get_embedding_dimension()

    # Create collection
    qdrant_memory_client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=dimension,
            distance=models.Distance.COSINE,
        ),
    )

    yield collection_name

    # Cleanup
    if qdrant_memory_client.collection_exists(collection_name):
        qdrant_memory_client.delete_collection(collection_name)


@pytest.fixture(name="seeded_qdrant_collection")
def fixture_seeded_qdrant_collection(
    qdrant_memory_client: qdrant_client.QdrantClient,
    mock_embeddings_provider: MockEmbeddingsProvider,
    audio_fragments: list[tuple[float, float, str]],
) -> Generator[str, None, None]:
    """Create and seed a test collection with sample content.

    Seeds the collection with audio fragment embeddings for search testing.
    """
    collection_name = "seeded-test-collection"
    dimension = mock_embeddings_provider.get_embedding_dimension()

    # Create collection
    qdrant_memory_client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=dimension,
            distance=models.Distance.COSINE,
        ),
    )

    # Extract texts and compute embeddings
    texts = [text for _, _, text in audio_fragments]
    embeddings = mock_embeddings_provider.encode_texts(texts)

    # Create points
    points = []
    for i, ((start, end, text), emb) in enumerate(zip(audio_fragments, embeddings)):
        points.append(
            models.PointStruct(
                id=i,
                vector=emb.tolist(),
                payload={
                    "episode": 1,
                    "channel": 1,
                    "text": text,
                    "start_secs": int(start),
                    "end_secs": int(end),
                },
            )
        )

    # Insert points
    qdrant_memory_client.upsert(collection_name=collection_name, points=points)

    yield collection_name

    # Cleanup
    if qdrant_memory_client.collection_exists(collection_name):
        qdrant_memory_client.delete_collection(collection_name)


@pytest.fixture(name="embedding_provider_mock")
def fixture_embedding_provider_mock(
    monkeypatch: pytest.MonkeyPatch,
    mock_embeddings_provider: MockEmbeddingsProvider,
) -> MockEmbeddingsProvider:
    """Patch the global embeddings provider with the mock.

    This allows integration tests to use the mock provider without
    loading the real model.
    """
    # Patch the get_embeddings_provider function
    monkeypatch.setattr(
        embedding,
        "get_embeddings_provider",
        lambda: mock_embeddings_provider,
    )
    return mock_embeddings_provider
