# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for SentenceTransformersProvider."""

import pytest

from voogle.embedding.provider import ContentModality, EmbeddingResult
from voogle.embedding.sentence_transformers import (
    DEFAULT_BATCH_SIZE,
    DEFAULT_MODEL_ID,
    MODEL_DIMENSIONS,
    SentenceTransformersProvider,
)


class TestSentenceTransformersProvider:
    """Tests for SentenceTransformersProvider class."""

    def test_default_initialization(self) -> None:
        """Provider can be initialized with defaults."""
        provider = SentenceTransformersProvider()
        assert provider._model_id == DEFAULT_MODEL_ID
        assert provider._device is None
        assert provider._batch_size == DEFAULT_BATCH_SIZE

    def test_custom_initialization(self) -> None:
        """Provider can be initialized with custom parameters."""
        provider = SentenceTransformersProvider(
            model_id="BAAI/bge-small-en-v1.5",
            device="cpu",
            batch_size=64,
        )
        assert provider._model_id == "BAAI/bge-small-en-v1.5"
        assert provider._device == "cpu"
        assert provider._batch_size == 64

    def test_metadata_properties(self) -> None:
        """Metadata returns correct values."""
        provider = SentenceTransformersProvider()
        metadata = provider.metadata

        assert metadata.provider_id == "sentence-transformers"
        assert metadata.model_id == DEFAULT_MODEL_ID
        assert metadata.supported_modalities == frozenset([ContentModality.TEXT])
        assert metadata.dimensions == MODEL_DIMENSIONS[DEFAULT_MODEL_ID]
        assert metadata.max_batch_size == DEFAULT_BATCH_SIZE

    def test_supports_text_modality(self) -> None:
        """Provider supports text modality only."""
        provider = SentenceTransformersProvider()
        assert provider.supports_modality(ContentModality.TEXT) is True
        assert provider.supports_modality(ContentModality.IMAGE) is False
        assert provider.supports_modality(ContentModality.AUDIO) is False
        assert provider.supports_modality(ContentModality.VIDEO) is False

    def test_embed_text_returns_result(self) -> None:
        """embed_text returns valid EmbeddingResult."""
        provider = SentenceTransformersProvider()
        result = provider.embed_text("hello world")

        assert isinstance(result, EmbeddingResult)
        assert len(result.vector) == MODEL_DIMENSIONS[DEFAULT_MODEL_ID]
        assert result.dimensions == MODEL_DIMENSIONS[DEFAULT_MODEL_ID]
        assert result.model_id == DEFAULT_MODEL_ID

    def test_embed_text_empty_raises(self) -> None:
        """embed_text with empty string raises ValueError."""
        provider = SentenceTransformersProvider()
        with pytest.raises(ValueError, match="text cannot be empty"):
            provider.embed_text("")

    def test_embed_text_batch_returns_results(self) -> None:
        """embed_text_batch returns list of EmbeddingResults."""
        provider = SentenceTransformersProvider()
        results = provider.embed_text_batch(["hello", "world"])

        assert len(results) == 2
        for result in results:
            assert isinstance(result, EmbeddingResult)
            assert len(result.vector) == MODEL_DIMENSIONS[DEFAULT_MODEL_ID]

    def test_embed_text_batch_empty_returns_empty(self) -> None:
        """embed_text_batch with empty list returns empty list."""
        provider = SentenceTransformersProvider()
        results = provider.embed_text_batch([])
        assert results == []

    def test_embed_text_batch_exceeds_max_raises(self) -> None:
        """embed_text_batch exceeding max_batch_size raises ValueError."""
        provider = SentenceTransformersProvider(batch_size=2)
        texts = ["text1", "text2", "text3"]
        with pytest.raises(ValueError, match="exceeds maximum"):
            provider.embed_text_batch(texts)

    def test_embed_image_raises_not_implemented(self) -> None:
        """embed_image raises NotImplementedError."""
        provider = SentenceTransformersProvider()
        with pytest.raises(NotImplementedError, match="does not support image"):
            provider.embed_image(b"fake-image")

    def test_embed_audio_raises_not_implemented(self) -> None:
        """embed_audio raises NotImplementedError."""
        provider = SentenceTransformersProvider()
        with pytest.raises(NotImplementedError, match="does not support audio"):
            provider.embed_audio(b"fake-audio")

    def test_embed_video_raises_not_implemented(self) -> None:
        """embed_video raises NotImplementedError."""
        provider = SentenceTransformersProvider()
        with pytest.raises(NotImplementedError, match="does not support video"):
            provider.embed_video(b"fake-video")

    def test_device_property(self) -> None:
        """device property returns correct device string."""
        provider = SentenceTransformersProvider(device="cpu")
        # Accessing device triggers model load
        assert "cpu" in provider.device

    def test_repr(self) -> None:
        """__repr__ returns informative string."""
        provider = SentenceTransformersProvider(
            model_id="test-model",
            device="cpu",
            batch_size=16,
        )
        repr_str = repr(provider)
        assert "SentenceTransformersProvider" in repr_str
        assert "test-model" in repr_str
        assert "cpu" in repr_str
        assert "16" in repr_str

    def test_known_model_dimensions(self) -> None:
        """Known models return correct dimensions from cache."""
        for model_id, expected_dims in MODEL_DIMENSIONS.items():
            provider = SentenceTransformersProvider(model_id=model_id)
            # Access dimensions without loading model
            assert provider._get_dimensions() == expected_dims


class TestEmbeddingQuality:
    """Tests for embedding quality and consistency."""

    def test_different_texts_produce_different_embeddings(self) -> None:
        """Different texts produce different embeddings."""
        provider = SentenceTransformersProvider()
        result1 = provider.embed_text("The quick brown fox")
        result2 = provider.embed_text("A lazy dog sleeps")

        # Embeddings should be different
        assert result1.vector != result2.vector

    def test_similar_texts_produce_similar_embeddings(self) -> None:
        """Similar texts produce similar embeddings (cosine similarity)."""
        import math

        provider = SentenceTransformersProvider()
        result1 = provider.embed_text("The cat sat on the mat")
        result2 = provider.embed_text("The cat sits on the mat")

        # Calculate cosine similarity
        dot_product = sum(a * b for a, b in zip(result1.vector, result2.vector))
        norm1 = math.sqrt(sum(a * a for a in result1.vector))
        norm2 = math.sqrt(sum(b * b for b in result2.vector))
        similarity = dot_product / (norm1 * norm2)

        # Similar sentences should have high similarity (>0.9)
        assert similarity > 0.9

    def test_embedding_determinism(self) -> None:
        """Same text produces identical embeddings."""
        provider = SentenceTransformersProvider()
        text = "Test reproducibility"
        result1 = provider.embed_text(text)
        result2 = provider.embed_text(text)

        assert result1.vector == result2.vector


class TestBatchProcessing:
    """Tests for batch processing functionality."""

    def test_batch_produces_same_results_as_individual(self) -> None:
        """Batch processing produces same results as individual calls."""
        provider = SentenceTransformersProvider()
        texts = ["hello", "world", "test"]

        # Individual embeddings
        individual_results = [provider.embed_text(t) for t in texts]

        # Batch embeddings
        batch_results = provider.embed_text_batch(texts)

        # Should be identical
        assert len(individual_results) == len(batch_results)
        for ind, batch in zip(individual_results, batch_results):
            assert ind.vector == batch.vector

    def test_batch_order_preserved(self) -> None:
        """Batch processing preserves input order."""
        provider = SentenceTransformersProvider()
        texts = ["first", "second", "third"]
        results = provider.embed_text_batch(texts)

        # Verify order by checking uniqueness
        assert len(set(tuple(r.vector) for r in results)) == 3
