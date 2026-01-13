# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Integration tests for test infrastructure.

These tests verify that the test infrastructure itself works correctly:
- Content fixtures are accessible and valid
- Qdrant fixtures provide isolated test environments
- Embedding mocks produce consistent, deterministic results
- The complete indexing and search pipeline works with mock data

Run with: cd backend && pytest tests/integration/test_infrastructure.py -v
"""

from pathlib import Path

import pytest
import qdrant_client

from fixtures.content_fixtures import ContentSample
from fixtures.infrastructure import MockEmbeddingsProvider


pytestmark = pytest.mark.integration


class TestContentFixtures:
    """Tests for content fixtures availability and validity."""

    @pytest.mark.description("Verifies content fixtures directory exists")
    def test_content_fixtures_dir_exists(self, content_fixtures_dir: Path) -> None:
        """Test that the content fixtures directory exists."""
        assert content_fixtures_dir.exists()
        assert content_fixtures_dir.is_dir()

    @pytest.mark.description("Verifies sample audio transcription file exists and is valid")
    def test_sample_audio_transcription_exists(
        self, sample_audio_transcription: ContentSample
    ) -> None:
        """Test that sample audio transcription file exists and has valid format."""
        assert sample_audio_transcription.path.exists()
        assert sample_audio_transcription.content_type == "audio/transcription"

        # Verify file format (pipe-delimited CSV)
        content = sample_audio_transcription.path.read_text()
        lines = content.strip().split("\n")
        assert len(lines) > 0

        # Check format of first line
        first_line = lines[0]
        parts = first_line.split("|")
        assert len(parts) >= 3, "Expected at least 3 pipe-delimited fields"

        # Verify timestamps are valid floats
        start_time = float(parts[0])
        end_time = float(parts[1])
        assert start_time >= 0
        assert end_time > start_time

    @pytest.mark.description("Verifies sample document file exists")
    def test_sample_document_exists(self, sample_document: ContentSample) -> None:
        """Test that sample document file exists and has content."""
        assert sample_document.path.exists()
        content = sample_document.path.read_text()
        assert len(content) > 100  # Meaningful content

    @pytest.mark.description("Verifies sample webpage file exists")
    def test_sample_webpage_exists(self, sample_webpage: ContentSample) -> None:
        """Test that sample webpage file exists and is valid HTML."""
        assert sample_webpage.path.exists()
        content = sample_webpage.path.read_text()
        assert "<!DOCTYPE html>" in content
        assert "<html" in content
        assert "</html>" in content

    @pytest.mark.description("Verifies sample code file exists")
    def test_sample_code_exists(self, sample_code: ContentSample) -> None:
        """Test that sample code file exists and is valid Python."""
        assert sample_code.path.exists()
        content = sample_code.path.read_text()
        assert "def " in content  # Has function definitions
        assert "class " in content  # Has class definitions

    @pytest.mark.description("Verifies all content samples fixture returns multiple samples")
    def test_all_content_samples_fixture(
        self, all_content_samples: list[ContentSample]
    ) -> None:
        """Test that all_content_samples fixture provides all sample files."""
        assert len(all_content_samples) == 4
        content_types = {s.content_type for s in all_content_samples}
        assert "audio/transcription" in content_types
        assert "text/plain" in content_types
        assert "text/html" in content_types
        assert "text/x-python" in content_types


class TestQdrantFixtures:
    """Tests for Qdrant test infrastructure."""

    @pytest.mark.description("Verifies in-memory Qdrant client is created correctly")
    def test_qdrant_memory_client_creation(
        self, qdrant_memory_client: qdrant_client.QdrantClient
    ) -> None:
        """Test that in-memory Qdrant client is properly initialized."""
        # Client should be usable
        collections = qdrant_memory_client.get_collections()
        assert collections is not None

    @pytest.mark.description("Verifies test collection is created and cleaned up")
    def test_qdrant_test_collection_lifecycle(
        self,
        qdrant_memory_client: qdrant_client.QdrantClient,
        qdrant_test_collection: str,
    ) -> None:
        """Test that test collection is created correctly."""
        # Collection should exist
        assert qdrant_memory_client.collection_exists(qdrant_test_collection)

        # Collection should have correct configuration
        info = qdrant_memory_client.get_collection(qdrant_test_collection)
        assert info.config.params.vectors is not None

    @pytest.mark.description("Verifies seeded collection contains expected data")
    def test_seeded_qdrant_collection(
        self,
        qdrant_memory_client: qdrant_client.QdrantClient,
        seeded_qdrant_collection: str,
    ) -> None:
        """Test that seeded collection has points with correct structure."""
        # Collection should have points
        info = qdrant_memory_client.get_collection(seeded_qdrant_collection)
        assert info.points_count > 0

        # Scroll through points and verify structure
        results, _ = qdrant_memory_client.scroll(
            collection_name=seeded_qdrant_collection,
            limit=5,
        )
        assert len(results) > 0

        # Verify payload structure
        first_point = results[0]
        assert first_point.payload is not None
        assert "episode" in first_point.payload
        assert "channel" in first_point.payload
        assert "text" in first_point.payload
        assert "start_secs" in first_point.payload
        assert "end_secs" in first_point.payload


class TestEmbeddingMocks:
    """Tests for embedding mock infrastructure."""

    @pytest.mark.description("Verifies mock provider produces deterministic embeddings")
    def test_mock_provider_deterministic(
        self, mock_embeddings_provider: MockEmbeddingsProvider
    ) -> None:
        """Test that mock provider produces consistent embeddings for same input."""
        text = "Test text for embedding"

        # Encode same text twice
        emb1 = mock_embeddings_provider.encode_texts([text])
        emb2 = mock_embeddings_provider.encode_texts([text])

        # Should produce identical results
        assert emb1.shape == emb2.shape
        assert (emb1 == emb2).all()

    @pytest.mark.description("Verifies mock provider returns correct dimensions")
    def test_mock_provider_dimensions(
        self, mock_embeddings_provider: MockEmbeddingsProvider
    ) -> None:
        """Test that mock provider returns embeddings with correct dimensions."""
        expected_dim = mock_embeddings_provider.get_embedding_dimension()

        embeddings = mock_embeddings_provider.encode_texts(["test text"])

        assert embeddings.shape == (1, expected_dim)

    @pytest.mark.description("Verifies mock provider handles batch encoding")
    def test_mock_provider_batch_encoding(
        self, mock_embeddings_provider: MockEmbeddingsProvider
    ) -> None:
        """Test that mock provider handles multiple texts correctly."""
        texts = ["First text", "Second text", "Third text"]

        embeddings = mock_embeddings_provider.encode_texts(texts)

        assert embeddings.shape[0] == len(texts)

    @pytest.mark.description("Verifies mock provider tracks encoding calls")
    def test_mock_provider_call_tracking(
        self, mock_embeddings_provider: MockEmbeddingsProvider
    ) -> None:
        """Test that mock provider tracks encode_texts calls."""
        mock_embeddings_provider.reset_calls()

        mock_embeddings_provider.encode_texts(["text1"])
        mock_embeddings_provider.encode_texts(["text2", "text3"])

        calls = mock_embeddings_provider.get_encode_calls()
        assert len(calls) == 2
        assert calls[0] == ["text1"]
        assert calls[1] == ["text2", "text3"]

    @pytest.mark.description("Verifies mock provider encode_single works")
    def test_mock_provider_encode_single(
        self, mock_embeddings_provider: MockEmbeddingsProvider
    ) -> None:
        """Test that encode_single returns correct shape."""
        embedding = mock_embeddings_provider.encode_single("query text")

        # Should return array with shape (1, dimension)
        assert len(embedding.shape) == 2
        assert embedding.shape[0] == 1
        assert embedding.shape[1] == mock_embeddings_provider.get_embedding_dimension()


class TestSearchIntegration:
    """Tests for end-to-end search using test infrastructure."""

    @pytest.mark.description("Verifies search works with seeded test data")
    def test_search_with_mock_data(
        self,
        qdrant_memory_client: qdrant_client.QdrantClient,
        seeded_qdrant_collection: str,
        mock_embeddings_provider: MockEmbeddingsProvider,
    ) -> None:
        """Test that search returns results from seeded collection."""
        # Create a query embedding
        query_embedding = mock_embeddings_provider.encode_single(
            "artificial intelligence and machine learning"
        )

        # Perform search
        results = qdrant_memory_client.query_points(
            collection_name=seeded_qdrant_collection,
            query=query_embedding[0].tolist(),
            limit=5,
        ).points

        # Should find results
        assert len(results) > 0

        # Results should have valid scores (cosine similarity)
        for result in results:
            assert -1.0 <= result.score <= 1.0

    @pytest.mark.description("Verifies audio fragments fixture is parseable")
    def test_audio_fragments_fixture(
        self, audio_fragments: list[tuple[float, float, str]]
    ) -> None:
        """Test that audio_fragments fixture provides valid fragment data."""
        assert len(audio_fragments) > 0

        for start, end, text in audio_fragments:
            assert isinstance(start, float)
            assert isinstance(end, float)
            assert isinstance(text, str)
            assert end > start
            assert len(text) > 0
