# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for EmbeddingStage."""

from collections.abc import AsyncIterator
from pathlib import Path
from typing import Union

import pytest

from voogle.embedding.provider import (
    ContentModality,
    EmbeddingProvider,
    EmbeddingResult,
    ProviderMetadata,
)
from voogle.pipeline.embedding import (
    CostMetrics,
    EmbeddingCache,
    EmbeddingInput,
    EmbeddingOutput,
    EmbeddingStage,
    EmbeddingStageConfig,
    RateLimiter,
)


class MockEmbeddingProvider(EmbeddingProvider):
    """Mock embedding provider for testing."""

    def __init__(
        self,
        model_id: str = "mock-model",
        dimensions: int = 384,
        modalities: frozenset[ContentModality] | None = None,
    ) -> None:
        self._model_id = model_id
        self._dimensions = dimensions
        self._modalities = modalities or frozenset([ContentModality.TEXT])
        self.embed_calls: list[str] = []
        self.batch_calls: list[list[str]] = []

    @property
    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            provider_id="mock",
            model_id=self._model_id,
            supported_modalities=self._modalities,
            dimensions=self._dimensions,
            max_batch_size=100,
        )

    def embed_text(self, text: str) -> EmbeddingResult:
        self.embed_calls.append(text)
        return EmbeddingResult(
            vector=[0.1] * self._dimensions,
            dimensions=self._dimensions,
            model_id=self._model_id,
            tokens_used=len(text.split()),
        )

    def embed_text_batch(self, texts: list[str]) -> list[EmbeddingResult]:
        self.batch_calls.append(texts)
        return [self.embed_text(text) for text in texts]

    def embed_image(self, _image: Union[bytes, Path]) -> EmbeddingResult:
        return EmbeddingResult(
            vector=[0.2] * self._dimensions,
            dimensions=self._dimensions,
            model_id=self._model_id,
        )

    def embed_audio(self, _audio: Union[bytes, Path]) -> EmbeddingResult:
        return EmbeddingResult(
            vector=[0.3] * self._dimensions,
            dimensions=self._dimensions,
            model_id=self._model_id,
        )

    def embed_video(self, _video: Union[bytes, Path]) -> EmbeddingResult:
        return EmbeddingResult(
            vector=[0.4] * self._dimensions,
            dimensions=self._dimensions,
            model_id=self._model_id,
        )


class TestEmbeddingStageConfig:
    """Tests for EmbeddingStageConfig."""

    def test_default_config(self) -> None:
        """Default config has expected values."""
        config = EmbeddingStageConfig()
        assert config.batch_size == 32
        assert config.rate_limit_per_second == 0.0
        assert config.enable_caching is True
        assert config.cache_max_size == 10000

    def test_custom_config(self) -> None:
        """Custom config values are set correctly."""
        config = EmbeddingStageConfig(
            batch_size=64,
            rate_limit_per_second=100.0,
            enable_caching=False,
            cache_max_size=5000,
        )
        assert config.batch_size == 64
        assert config.rate_limit_per_second == 100.0
        assert config.enable_caching is False
        assert config.cache_max_size == 5000

    def test_invalid_batch_size_raises(self) -> None:
        """Invalid batch_size raises ValueError."""
        with pytest.raises(ValueError, match="batch_size must be >= 1"):
            EmbeddingStageConfig(batch_size=0)

    def test_negative_rate_limit_raises(self) -> None:
        """Negative rate_limit_per_second raises ValueError."""
        with pytest.raises(ValueError, match="rate_limit_per_second must be >= 0"):
            EmbeddingStageConfig(rate_limit_per_second=-1.0)

    def test_negative_cache_max_size_raises(self) -> None:
        """Negative cache_max_size raises ValueError."""
        with pytest.raises(ValueError, match="cache_max_size must be >= 0"):
            EmbeddingStageConfig(cache_max_size=-1)


class TestEmbeddingInput:
    """Tests for EmbeddingInput."""

    def test_create_text_input(self) -> None:
        """Text input can be created."""
        input_item = EmbeddingInput(content="hello world")
        assert input_item.content == "hello world"
        assert input_item.modality == ContentModality.TEXT
        assert input_item.metadata == {}

    def test_create_input_with_metadata(self) -> None:
        """Input with metadata can be created."""
        input_item = EmbeddingInput(
            content="hello",
            modality=ContentModality.TEXT,
            metadata={"id": 123},
        )
        assert input_item.metadata == {"id": 123}

    def test_content_hash_text(self) -> None:
        """Text content hash is consistent."""
        input1 = EmbeddingInput(content="hello world")
        input2 = EmbeddingInput(content="hello world")
        input3 = EmbeddingInput(content="different")

        assert input1.content_hash() == input2.content_hash()
        assert input1.content_hash() != input3.content_hash()

    def test_content_hash_bytes(self) -> None:
        """Bytes content hash is consistent."""
        input1 = EmbeddingInput(content=b"hello", modality=ContentModality.IMAGE)
        input2 = EmbeddingInput(content=b"hello", modality=ContentModality.IMAGE)

        assert input1.content_hash() == input2.content_hash()


class TestEmbeddingOutput:
    """Tests for EmbeddingOutput."""

    def test_create_output(self) -> None:
        """Output can be created."""
        input_item = EmbeddingInput(content="hello")
        result = EmbeddingResult(
            vector=[0.1, 0.2, 0.3],
            dimensions=3,
            model_id="test",
        )
        output = EmbeddingOutput(input=input_item, result=result, cached=False)

        assert output.input == input_item
        assert output.result == result
        assert output.cached is False


class TestCostMetrics:
    """Tests for CostMetrics."""

    def test_default_metrics(self) -> None:
        """Default metrics are zero."""
        metrics = CostMetrics()
        assert metrics.total_tokens == 0
        assert metrics.total_images == 0
        assert metrics.total_audio_seconds == 0.0
        assert metrics.total_video_seconds == 0.0
        assert metrics.estimated_cost_usd == 0.0


class TestRateLimiter:
    """Tests for RateLimiter."""

    @pytest.mark.asyncio
    async def test_unlimited_rate(self) -> None:
        """Unlimited rate (0) allows immediate acquisition."""
        limiter = RateLimiter(0.0)
        # Should complete immediately
        await limiter.acquire(100)

    @pytest.mark.asyncio
    async def test_rate_limiting(self) -> None:
        """Rate limiting delays acquisition."""
        import time

        limiter = RateLimiter(10.0)  # 10 per second

        start = time.monotonic()
        await limiter.acquire(10)  # Should be immediate
        elapsed = time.monotonic() - start

        # Should be nearly instant for first burst
        assert elapsed < 0.1


class TestEmbeddingCache:
    """Tests for EmbeddingCache."""

    def test_cache_put_and_get(self) -> None:
        """Cache stores and retrieves values."""
        cache = EmbeddingCache(max_size=10)
        result = EmbeddingResult(
            vector=[0.1, 0.2],
            dimensions=2,
            model_id="test",
        )

        cache.put("key1", result)
        retrieved = cache.get("key1")

        assert retrieved == result

    def test_cache_miss(self) -> None:
        """Cache returns None for missing keys."""
        cache = EmbeddingCache(max_size=10)
        assert cache.get("nonexistent") is None

    def test_cache_eviction(self) -> None:
        """Cache evicts oldest entries when full."""
        cache = EmbeddingCache(max_size=2)
        result = EmbeddingResult(
            vector=[0.1],
            dimensions=1,
            model_id="test",
        )

        cache.put("key1", result)
        cache.put("key2", result)
        cache.put("key3", result)  # Should evict key1

        assert cache.get("key1") is None
        assert cache.get("key2") is not None
        assert cache.get("key3") is not None

    def test_cache_disabled(self) -> None:
        """Cache with max_size=0 doesn't store values."""
        cache = EmbeddingCache(max_size=0)
        result = EmbeddingResult(
            vector=[0.1],
            dimensions=1,
            model_id="test",
        )

        cache.put("key1", result)
        assert cache.get("key1") is None
        assert cache.size == 0

    def test_cache_hit_rate(self) -> None:
        """Cache tracks hit rate correctly."""
        cache = EmbeddingCache(max_size=10)
        result = EmbeddingResult(
            vector=[0.1],
            dimensions=1,
            model_id="test",
        )

        cache.put("key1", result)
        cache.get("key1")  # hit
        cache.get("key1")  # hit
        cache.get("key2")  # miss

        assert cache.hit_rate == 2.0 / 3.0


class TestEmbeddingStage:
    """Tests for EmbeddingStage."""

    def test_create_default_stage(self) -> None:
        """Default stage can be created."""
        stage = EmbeddingStage()
        assert stage.name == "embedding"
        assert stage.config.batch_size == 32

    def test_create_with_custom_config(self) -> None:
        """Stage with custom config can be created."""
        config = EmbeddingStageConfig(batch_size=64)
        stage = EmbeddingStage(config=config)
        assert stage.config.batch_size == 64

    def test_create_with_custom_provider(self) -> None:
        """Stage with custom provider can be created."""
        provider = MockEmbeddingProvider()
        stage = EmbeddingStage(text_provider=provider)
        assert stage.get_provider(ContentModality.TEXT) == provider

    def test_get_provider_text_default(self) -> None:
        """Default text provider is SentenceTransformers."""
        stage = EmbeddingStage()
        provider = stage.get_provider(ContentModality.TEXT)
        assert provider is not None

    def test_get_provider_missing_raises(self) -> None:
        """Missing provider raises StageError."""
        from voogle.pipeline.base import StageError

        stage = EmbeddingStage()
        with pytest.raises(StageError, match="No provider configured"):
            stage.get_provider(ContentModality.IMAGE)

    @pytest.mark.asyncio
    async def test_process_single_item(self) -> None:
        """Stage processes a single item."""
        provider = MockEmbeddingProvider()
        stage = EmbeddingStage(text_provider=provider)

        async def items() -> AsyncIterator[EmbeddingInput]:
            yield EmbeddingInput(content="hello world")

        results = []
        async for output in stage.process(items()):
            results.append(output)

        assert len(results) == 1
        assert results[0].result.dimensions == 384
        assert results[0].cached is False

    @pytest.mark.asyncio
    async def test_process_batch(self) -> None:
        """Stage batches items correctly."""
        provider = MockEmbeddingProvider()
        config = EmbeddingStageConfig(batch_size=2)
        stage = EmbeddingStage(config=config, text_provider=provider)

        async def items() -> AsyncIterator[EmbeddingInput]:
            yield EmbeddingInput(content="first")
            yield EmbeddingInput(content="second")
            yield EmbeddingInput(content="third")

        results = []
        async for output in stage.process(items()):
            results.append(output)

        assert len(results) == 3
        # Should have made 2 batch calls (2 items + 1 item)
        assert len(provider.batch_calls) == 2

    @pytest.mark.asyncio
    async def test_process_with_caching(self) -> None:
        """Stage caches and reuses embeddings."""
        provider = MockEmbeddingProvider()
        config = EmbeddingStageConfig(enable_caching=True)
        stage = EmbeddingStage(config=config, text_provider=provider)

        async def items() -> AsyncIterator[EmbeddingInput]:
            yield EmbeddingInput(content="duplicate")
            yield EmbeddingInput(content="unique")
            yield EmbeddingInput(content="duplicate")  # Should be cached

        results = []
        async for output in stage.process(items()):
            results.append(output)

        assert len(results) == 3
        assert results[0].cached is False
        assert results[1].cached is False
        assert results[2].cached is True  # Retrieved from cache

    @pytest.mark.asyncio
    async def test_process_without_caching(self) -> None:
        """Stage without caching recomputes embeddings across batches."""
        provider = MockEmbeddingProvider()
        # Set batch_size=1 to force separate batches
        config = EmbeddingStageConfig(enable_caching=False, batch_size=1)
        stage = EmbeddingStage(config=config, text_provider=provider)

        async def items() -> AsyncIterator[EmbeddingInput]:
            yield EmbeddingInput(content="duplicate")
            yield EmbeddingInput(content="duplicate")

        results = []
        async for output in stage.process(items()):
            results.append(output)

        assert len(results) == 2
        # Both should be computed (not cached) since caching is disabled
        assert results[0].cached is False
        assert results[1].cached is False
        # Provider should have been called twice
        assert len(provider.batch_calls) == 2

    @pytest.mark.asyncio
    async def test_setup_and_teardown(self) -> None:
        """Setup and teardown complete without error."""
        stage = EmbeddingStage()
        await stage.setup()
        await stage.teardown()

    def test_cache_stats(self) -> None:
        """Cache stats are accessible."""
        stage = EmbeddingStage()
        stats = stage.cache_stats
        assert "size" in stats
        assert "hit_rate" in stats
        assert "enabled" in stats

    def test_cost_metrics(self) -> None:
        """Cost metrics are accessible."""
        stage = EmbeddingStage()
        metrics = stage.cost_metrics
        assert isinstance(metrics, CostMetrics)

    def test_str_representation(self) -> None:
        """Stage has informative string representation."""
        stage = EmbeddingStage()
        stage_str = str(stage)
        assert "EmbeddingStage" in stage_str
        assert "batch_size" in stage_str


class TestProviderRouting:
    """Tests for provider routing based on content type."""

    @pytest.mark.asyncio
    async def test_route_to_correct_provider(self) -> None:
        """Items are routed to correct provider based on modality."""
        text_provider = MockEmbeddingProvider(model_id="text-model")
        image_provider = MockEmbeddingProvider(
            model_id="image-model",
            modalities=frozenset([ContentModality.IMAGE]),
        )

        stage = EmbeddingStage(
            text_provider=text_provider,
            image_provider=image_provider,
        )

        async def items() -> AsyncIterator[EmbeddingInput]:
            yield EmbeddingInput(content="text content", modality=ContentModality.TEXT)
            yield EmbeddingInput(content=b"image data", modality=ContentModality.IMAGE)

        results = []
        async for output in stage.process(items()):
            results.append(output)

        assert len(results) == 2
        assert results[0].result.model_id == "text-model"
        assert results[1].result.model_id == "image-model"
