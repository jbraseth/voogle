# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for embedding provider abstraction layer."""

from pathlib import Path
from typing import Union

import pytest

from voogle.embedding.provider import (
    ContentModality,
    CostInfo,
    EmbeddingProvider,
    EmbeddingResult,
    ProviderMetadata,
)


class TestEmbeddingResult:
    """Tests for EmbeddingResult dataclass."""

    def test_create_valid_result(self) -> None:
        """Valid embedding result can be created."""
        result = EmbeddingResult(
            vector=[0.1, 0.2, 0.3],
            dimensions=3,
            model_id="test-model",
        )
        assert result.vector == [0.1, 0.2, 0.3]
        assert result.dimensions == 3
        assert result.model_id == "test-model"
        assert result.tokens_used is None

    def test_create_result_with_tokens(self) -> None:
        """Embedding result with token count can be created."""
        result = EmbeddingResult(
            vector=[0.1, 0.2],
            dimensions=2,
            model_id="test-model",
            tokens_used=100,
        )
        assert result.tokens_used == 100

    def test_vector_dimension_mismatch_raises(self) -> None:
        """Mismatched vector length and dimensions raises ValueError."""
        with pytest.raises(ValueError, match="Vector length.*does not match"):
            EmbeddingResult(
                vector=[0.1, 0.2, 0.3],
                dimensions=5,
                model_id="test-model",
            )

    def test_zero_dimensions_raises(self) -> None:
        """Zero dimensions raises ValueError."""
        with pytest.raises(ValueError, match="Dimensions must be positive"):
            EmbeddingResult(
                vector=[],
                dimensions=0,
                model_id="test-model",
            )

    def test_negative_dimensions_raises(self) -> None:
        """Negative dimensions raises ValueError."""
        # Note: Vector length mismatch is checked before dimensions positivity,
        # so we need a vector that matches the negative dimension to test this.
        # Since that's impossible, we check that any negative dimension fails validation.
        with pytest.raises(ValueError, match="does not match|Dimensions must be positive"):
            EmbeddingResult(
                vector=[],
                dimensions=-1,
                model_id="test-model",
            )

    def test_result_is_frozen(self) -> None:
        """EmbeddingResult is immutable."""
        result = EmbeddingResult(
            vector=[0.1],
            dimensions=1,
            model_id="test-model",
        )
        with pytest.raises(AttributeError):
            result.model_id = "new-model"  # type: ignore[misc]


class TestCostInfo:
    """Tests for CostInfo dataclass."""

    def test_create_empty_cost_info(self) -> None:
        """CostInfo with no values can be created."""
        cost = CostInfo()
        assert cost.cost_per_token is None
        assert cost.cost_per_image is None
        assert cost.cost_per_second_audio is None
        assert cost.cost_per_second_video is None

    def test_create_text_cost_info(self) -> None:
        """CostInfo with text pricing can be created."""
        cost = CostInfo(cost_per_token=0.00002)
        assert cost.cost_per_token == 0.00002

    def test_create_full_cost_info(self) -> None:
        """CostInfo with all pricing can be created."""
        cost = CostInfo(
            cost_per_token=0.00002,
            cost_per_image=0.001,
            cost_per_second_audio=0.0001,
            cost_per_second_video=0.0005,
        )
        assert cost.cost_per_token == 0.00002
        assert cost.cost_per_image == 0.001
        assert cost.cost_per_second_audio == 0.0001
        assert cost.cost_per_second_video == 0.0005


class TestProviderMetadata:
    """Tests for ProviderMetadata dataclass."""

    def test_create_valid_metadata(self) -> None:
        """Valid metadata can be created."""
        metadata = ProviderMetadata(
            provider_id="test-provider",
            model_id="test-model",
            supported_modalities=frozenset([ContentModality.TEXT]),
            dimensions=384,
        )
        assert metadata.provider_id == "test-provider"
        assert metadata.model_id == "test-model"
        assert metadata.dimensions == 384
        assert metadata.max_batch_size == 1
        assert metadata.cost_info is None

    def test_create_metadata_with_all_fields(self) -> None:
        """Metadata with all fields can be created."""
        cost = CostInfo(cost_per_token=0.00002)
        metadata = ProviderMetadata(
            provider_id="openai",
            model_id="text-embedding-3-small",
            supported_modalities=frozenset([ContentModality.TEXT]),
            dimensions=1536,
            max_batch_size=100,
            cost_info=cost,
            description="OpenAI text embedding provider",
        )
        assert metadata.max_batch_size == 100
        assert metadata.cost_info == cost
        assert metadata.description == "OpenAI text embedding provider"

    def test_empty_provider_id_raises(self) -> None:
        """Empty provider_id raises ValueError."""
        with pytest.raises(ValueError, match="provider_id cannot be empty"):
            ProviderMetadata(
                provider_id="",
                model_id="test-model",
                supported_modalities=frozenset([ContentModality.TEXT]),
                dimensions=384,
            )

    def test_empty_model_id_raises(self) -> None:
        """Empty model_id raises ValueError."""
        with pytest.raises(ValueError, match="model_id cannot be empty"):
            ProviderMetadata(
                provider_id="test-provider",
                model_id="",
                supported_modalities=frozenset([ContentModality.TEXT]),
                dimensions=384,
            )

    def test_empty_modalities_raises(self) -> None:
        """Empty supported_modalities raises ValueError."""
        with pytest.raises(ValueError, match="supported_modalities cannot be empty"):
            ProviderMetadata(
                provider_id="test-provider",
                model_id="test-model",
                supported_modalities=frozenset(),
                dimensions=384,
            )

    def test_zero_dimensions_raises(self) -> None:
        """Zero dimensions raises ValueError."""
        with pytest.raises(ValueError, match="dimensions must be positive"):
            ProviderMetadata(
                provider_id="test-provider",
                model_id="test-model",
                supported_modalities=frozenset([ContentModality.TEXT]),
                dimensions=0,
            )

    def test_zero_batch_size_raises(self) -> None:
        """Zero max_batch_size raises ValueError."""
        with pytest.raises(ValueError, match="max_batch_size must be positive"):
            ProviderMetadata(
                provider_id="test-provider",
                model_id="test-model",
                supported_modalities=frozenset([ContentModality.TEXT]),
                dimensions=384,
                max_batch_size=0,
            )

    def test_supports_modality(self) -> None:
        """supports() returns True for supported modalities."""
        metadata = ProviderMetadata(
            provider_id="test-provider",
            model_id="test-model",
            supported_modalities=frozenset([ContentModality.TEXT, ContentModality.IMAGE]),
            dimensions=384,
        )
        assert metadata.supports(ContentModality.TEXT) is True
        assert metadata.supports(ContentModality.IMAGE) is True
        assert metadata.supports(ContentModality.AUDIO) is False
        assert metadata.supports(ContentModality.VIDEO) is False


class TestContentModality:
    """Tests for ContentModality enum."""

    def test_all_modalities_exist(self) -> None:
        """All expected modalities are defined."""
        assert ContentModality.TEXT.value == "text"
        assert ContentModality.IMAGE.value == "image"
        assert ContentModality.AUDIO.value == "audio"
        assert ContentModality.VIDEO.value == "video"

    def test_modality_count(self) -> None:
        """Correct number of modalities are defined."""
        assert len(ContentModality) == 4


class MockTextProvider(EmbeddingProvider):
    """Mock provider for testing that only supports text."""

    @property
    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            provider_id="mock",
            model_id="mock-text-v1",
            supported_modalities=frozenset([ContentModality.TEXT]),
            dimensions=3,
            max_batch_size=10,
        )

    def embed_text(self, text: str) -> EmbeddingResult:
        return EmbeddingResult(
            vector=[0.1, 0.2, 0.3],
            dimensions=3,
            model_id="mock-text-v1",
        )

    def embed_image(self, image: Union[bytes, Path]) -> EmbeddingResult:
        raise NotImplementedError("MockTextProvider does not support image embeddings")

    def embed_audio(self, audio: Union[bytes, Path]) -> EmbeddingResult:
        raise NotImplementedError("MockTextProvider does not support audio embeddings")

    def embed_video(self, video: Union[bytes, Path]) -> EmbeddingResult:
        raise NotImplementedError("MockTextProvider does not support video embeddings")


class TestEmbeddingProvider:
    """Tests for EmbeddingProvider ABC."""

    def test_abstract_methods_defined(self) -> None:
        """EmbeddingProvider has expected abstract methods."""
        abstract_methods = EmbeddingProvider.__abstractmethods__
        assert "metadata" in abstract_methods
        assert "embed_text" in abstract_methods
        assert "embed_image" in abstract_methods
        assert "embed_audio" in abstract_methods
        assert "embed_video" in abstract_methods

    def test_concrete_implementation_works(self) -> None:
        """Concrete implementation can be instantiated and used."""
        provider = MockTextProvider()
        result = provider.embed_text("hello world")
        assert result.vector == [0.1, 0.2, 0.3]
        assert result.model_id == "mock-text-v1"

    def test_supports_modality(self) -> None:
        """supports_modality correctly checks provider capabilities."""
        provider = MockTextProvider()
        assert provider.supports_modality(ContentModality.TEXT) is True
        assert provider.supports_modality(ContentModality.IMAGE) is False

    def test_unsupported_modality_raises(self) -> None:
        """Unsupported modality raises NotImplementedError."""
        provider = MockTextProvider()
        with pytest.raises(NotImplementedError):
            provider.embed_image(b"fake-image-data")

    def test_embed_text_batch_default_implementation(self) -> None:
        """Default batch implementation calls embed_text for each item."""
        provider = MockTextProvider()
        results = provider.embed_text_batch(["text1", "text2", "text3"])
        assert len(results) == 3
        for result in results:
            assert result.vector == [0.1, 0.2, 0.3]

    def test_embed_text_batch_exceeds_max_raises(self) -> None:
        """Batch exceeding max_batch_size raises ValueError."""
        provider = MockTextProvider()
        # max_batch_size is 10, try with 11
        texts = [f"text{i}" for i in range(11)]
        with pytest.raises(ValueError, match="exceeds maximum"):
            provider.embed_text_batch(texts)

    def test_metadata_property(self) -> None:
        """metadata property returns correct ProviderMetadata."""
        provider = MockTextProvider()
        metadata = provider.metadata
        assert metadata.provider_id == "mock"
        assert metadata.model_id == "mock-text-v1"
        assert metadata.dimensions == 3
