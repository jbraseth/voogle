# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Embedding stage for the ingestion pipeline.

This module provides the EmbeddingStage class that integrates embedding providers
into the pipeline architecture. It supports batch processing, provider routing
based on content type, content-hash caching, rate limiting, and cost tracking.

Usage:
    from voogle.pipeline.embedding import EmbeddingStage, EmbeddingStageConfig
    from voogle.embedding import SentenceTransformersProvider

    # Create with default provider
    stage = EmbeddingStage()

    # Create with custom configuration
    config = EmbeddingStageConfig(
        batch_size=64,
        rate_limit_per_second=100.0,
        enable_caching=True,
    )
    provider = SentenceTransformersProvider(model_id="BAAI/bge-small-en-v1.5")
    stage = EmbeddingStage(config=config, text_provider=provider)
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import time
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any

from voogle.embedding.provider import (
    ContentModality,
    EmbeddingProvider,
    EmbeddingResult,
)
from voogle.embedding.sentence_transformers import SentenceTransformersProvider
from voogle.pipeline.base import Stage, StageError

logger = logging.getLogger(__name__)


@dataclass
class CostMetrics:
    """Tracks cost metrics for embedding operations.

    Attributes:
        total_tokens: Total tokens processed.
        total_images: Total images processed.
        total_audio_seconds: Total audio seconds processed.
        total_video_seconds: Total video seconds processed.
        estimated_cost_usd: Estimated total cost in USD.
    """

    total_tokens: int = 0
    total_images: int = 0
    total_audio_seconds: float = 0.0
    total_video_seconds: float = 0.0
    estimated_cost_usd: float = 0.0


@dataclass
class EmbeddingStageConfig:
    """Configuration for the embedding stage.

    Attributes:
        batch_size: Maximum items to process in a single batch.
        rate_limit_per_second: Maximum embeddings per second (0 = unlimited).
        enable_caching: Whether to cache embeddings by content hash.
        cache_max_size: Maximum number of entries in the cache.
    """

    batch_size: int = 32
    rate_limit_per_second: float = 0.0
    enable_caching: bool = True
    cache_max_size: int = 10000

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.batch_size < 1:
            raise ValueError(f"batch_size must be >= 1, got {self.batch_size}")
        if self.rate_limit_per_second < 0:
            raise ValueError(
                f"rate_limit_per_second must be >= 0, got {self.rate_limit_per_second}"
            )
        if self.cache_max_size < 0:
            raise ValueError(f"cache_max_size must be >= 0, got {self.cache_max_size}")


@dataclass
class EmbeddingInput:
    """Input item for the embedding stage.

    Attributes:
        content: The content to embed (text, bytes, or path).
        modality: The content modality (text, image, audio, video).
        metadata: Optional metadata to pass through.
    """

    content: str | bytes
    modality: ContentModality = ContentModality.TEXT
    metadata: dict[str, Any] = field(default_factory=dict)

    def content_hash(self) -> str:
        """Generate a hash of the content for caching."""
        if isinstance(self.content, str):
            content_bytes = self.content.encode("utf-8")
        else:
            content_bytes = self.content
        return hashlib.sha256(content_bytes).hexdigest()


@dataclass
class EmbeddingOutput:
    """Output item from the embedding stage.

    Attributes:
        input: The original input item.
        result: The embedding result from the provider.
        cached: Whether this result was served from cache.
    """

    input: EmbeddingInput
    result: EmbeddingResult
    cached: bool = False


class RateLimiter:
    """Token bucket rate limiter for controlling embedding throughput."""

    def __init__(self, rate_per_second: float) -> None:
        """Initialize the rate limiter.

        Args:
            rate_per_second: Maximum operations per second. 0 means unlimited.
        """
        self._rate = rate_per_second
        self._tokens = rate_per_second
        self._last_update = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self, count: int = 1) -> None:
        """Acquire tokens, waiting if necessary.

        Args:
            count: Number of tokens to acquire.
        """
        if self._rate <= 0:
            return

        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_update
            self._tokens = min(self._rate, self._tokens + elapsed * self._rate)
            self._last_update = now

            while self._tokens < count:
                wait_time = (count - self._tokens) / self._rate
                await asyncio.sleep(wait_time)
                now = time.monotonic()
                elapsed = now - self._last_update
                self._tokens = min(self._rate, self._tokens + elapsed * self._rate)
                self._last_update = now

            self._tokens -= count


class EmbeddingCache:
    """LRU cache for embedding results keyed by content hash."""

    def __init__(self, max_size: int) -> None:
        """Initialize the cache.

        Args:
            max_size: Maximum number of entries. 0 disables caching.
        """
        self._max_size = max_size
        self._cache: dict[str, EmbeddingResult] = {}
        self._access_order: list[str] = []
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> EmbeddingResult | None:
        """Get an item from the cache.

        Args:
            key: The cache key (content hash).

        Returns:
            The cached EmbeddingResult or None if not found.
        """
        if self._max_size <= 0 or key not in self._cache:
            self._misses += 1
            return None

        # Move to end for LRU
        self._access_order.remove(key)
        self._access_order.append(key)
        self._hits += 1
        return self._cache[key]

    def put(self, key: str, value: EmbeddingResult) -> None:
        """Store an item in the cache.

        Args:
            key: The cache key (content hash).
            value: The EmbeddingResult to cache.
        """
        if self._max_size <= 0:
            return

        if key in self._cache:
            self._access_order.remove(key)
        elif len(self._cache) >= self._max_size:
            # Evict oldest
            oldest = self._access_order.pop(0)
            del self._cache[oldest]

        self._cache[key] = value
        self._access_order.append(key)

    @property
    def hit_rate(self) -> float:
        """Calculate the cache hit rate."""
        total = self._hits + self._misses
        if total == 0:
            return 0.0
        return self._hits / total

    @property
    def size(self) -> int:
        """Return the current cache size."""
        return len(self._cache)


class EmbeddingStage(Stage[EmbeddingInput, EmbeddingOutput]):
    """Pipeline stage for generating embeddings from content.

    This stage takes EmbeddingInput items, routes them to the appropriate
    embedding provider based on content modality, and produces EmbeddingOutput
    items with the embedding vectors.

    Features:
    - Batch processing for efficiency
    - Provider routing based on content type
    - Content-hash caching to avoid recomputing embeddings
    - Rate limiting to control API usage
    - Cost tracking for budgeting

    Example:
        from voogle.pipeline import Pipeline
        from voogle.pipeline.embedding import EmbeddingStage, EmbeddingInput

        stage = EmbeddingStage()
        pipeline = Pipeline([stage])

        async def inputs():
            yield EmbeddingInput(content="Hello world")
            yield EmbeddingInput(content="Goodbye world")

        async for output in pipeline.execute(inputs()):
            print(f"Vector dimensions: {output.result.dimensions}")
    """

    def __init__(
        self,
        config: EmbeddingStageConfig | None = None,
        text_provider: EmbeddingProvider | None = None,
        image_provider: EmbeddingProvider | None = None,
        audio_provider: EmbeddingProvider | None = None,
        video_provider: EmbeddingProvider | None = None,
    ) -> None:
        """Initialize the embedding stage.

        Args:
            config: Stage configuration. Uses defaults if not provided.
            text_provider: Provider for text embeddings. Uses SentenceTransformers
                          if not provided.
            image_provider: Provider for image embeddings. Optional.
            audio_provider: Provider for audio embeddings. Optional.
            video_provider: Provider for video embeddings. Optional.
        """
        self._config = config or EmbeddingStageConfig()
        self._text_provider = text_provider
        self._image_provider = image_provider
        self._audio_provider = audio_provider
        self._video_provider = video_provider

        self._rate_limiter = RateLimiter(self._config.rate_limit_per_second)
        self._cache = EmbeddingCache(
            self._config.cache_max_size if self._config.enable_caching else 0
        )
        self._cost_metrics = CostMetrics()
        self._items_processed = 0

    @property
    def name(self) -> str:
        """Return the name of this stage."""
        return "embedding"

    @property
    def config(self) -> EmbeddingStageConfig:
        """Return the stage configuration."""
        return self._config

    @property
    def cost_metrics(self) -> CostMetrics:
        """Return the current cost metrics."""
        return self._cost_metrics

    @property
    def cache_stats(self) -> dict[str, Any]:
        """Return cache statistics."""
        return {
            "size": self._cache.size,
            "hit_rate": self._cache.hit_rate,
            "enabled": self._config.enable_caching,
        }

    def get_provider(self, modality: ContentModality) -> EmbeddingProvider:
        """Get the provider for a given modality.

        Args:
            modality: The content modality.

        Returns:
            The appropriate embedding provider.

        Raises:
            StageError: If no provider is configured for the modality.
        """
        provider_map = {
            ContentModality.TEXT: self._text_provider,
            ContentModality.IMAGE: self._image_provider,
            ContentModality.AUDIO: self._audio_provider,
            ContentModality.VIDEO: self._video_provider,
        }

        provider = provider_map.get(modality)
        if provider is None:
            if modality == ContentModality.TEXT:
                # Lazy-initialize default text provider
                self._text_provider = SentenceTransformersProvider()
                return self._text_provider
            raise StageError(
                self.name,
                f"No provider configured for modality: {modality.value}",
            )

        return provider

    async def setup(self) -> None:
        """Initialize resources before processing."""
        logger.info(
            f"EmbeddingStage setup: batch_size={self._config.batch_size}, "
            f"rate_limit={self._config.rate_limit_per_second}/s, "
            f"caching={'enabled' if self._config.enable_caching else 'disabled'}"
        )

    async def teardown(self) -> None:
        """Clean up resources after processing."""
        logger.info(
            f"EmbeddingStage teardown: processed={self._items_processed}, "
            f"cost=${self._cost_metrics.estimated_cost_usd:.4f}, "
            f"cache_hit_rate={self._cache.hit_rate:.2%}"
        )

    async def process(
        self, items: AsyncIterator[EmbeddingInput]
    ) -> AsyncIterator[EmbeddingOutput]:
        """Process input items and generate embeddings.

        Args:
            items: Async iterator of EmbeddingInput items.

        Yields:
            EmbeddingOutput items with embedding vectors.
        """
        batch: list[EmbeddingInput] = []

        async for item in items:
            batch.append(item)

            if len(batch) >= self._config.batch_size:
                async for output in self._process_batch(batch):
                    yield output
                batch = []

        # Process remaining items
        if batch:
            async for output in self._process_batch(batch):
                yield output

    async def _process_batch(
        self, batch: list[EmbeddingInput]
    ) -> AsyncIterator[EmbeddingOutput]:
        """Process a batch of items.

        Args:
            batch: List of items to process.

        Yields:
            EmbeddingOutput for each item.
        """
        # Check cache first and deduplicate within batch
        cached_results: dict[str, EmbeddingResult] = {}
        uncached_items: list[tuple[int, EmbeddingInput]] = []
        seen_hashes: set[str] = set()  # Track hashes we'll process in this batch

        for idx, item in enumerate(batch):
            content_hash = item.content_hash()
            cached = self._cache.get(content_hash)
            if cached is not None:
                cached_results[content_hash] = cached
            elif content_hash in seen_hashes:
                # Duplicate within same batch - will be served from batch results
                pass
            else:
                uncached_items.append((idx, item))
                seen_hashes.add(content_hash)

        # Group uncached items by modality for efficient batching
        items_by_modality: dict[ContentModality, list[tuple[int, EmbeddingInput]]] = {}
        for idx, item in uncached_items:
            if item.modality not in items_by_modality:
                items_by_modality[item.modality] = []
            items_by_modality[item.modality].append((idx, item))

        # Process each modality batch
        new_results: dict[str, EmbeddingResult] = {}
        for modality, modality_items in items_by_modality.items():
            try:
                provider = self.get_provider(modality)
                results = await self._embed_batch(provider, modality, modality_items)
                for (idx, item), result in zip(modality_items, results):
                    content_hash = item.content_hash()
                    new_results[content_hash] = result
                    # Cache the result
                    self._cache.put(content_hash, result)
                    # Track costs
                    self._track_cost(modality, result)
            except Exception as e:
                logger.error(f"Error processing {modality.value} batch: {e}")
                raise StageError(self.name, str(e), cause=e)

        # Yield results in original order
        for idx, item in enumerate(batch):
            content_hash = item.content_hash()
            if content_hash in cached_results:
                yield EmbeddingOutput(
                    input=item,
                    result=cached_results[content_hash],
                    cached=True,
                )
            elif content_hash in new_results:
                # Check if this was the first occurrence (we processed it)
                # or a duplicate within the batch
                is_first_occurrence = any(
                    i == idx for i, itm in uncached_items if itm.content_hash() == content_hash
                )
                if is_first_occurrence:
                    self._items_processed += 1
                yield EmbeddingOutput(
                    input=item,
                    result=new_results[content_hash],
                    cached=not is_first_occurrence,
                )

    async def _embed_batch(
        self,
        provider: EmbeddingProvider,
        modality: ContentModality,
        items: list[tuple[int, EmbeddingInput]],
    ) -> list[EmbeddingResult]:
        """Generate embeddings for a batch of items.

        Args:
            provider: The embedding provider to use.
            modality: The content modality.
            items: List of (index, item) tuples.

        Returns:
            List of EmbeddingResult objects.
        """
        # Apply rate limiting
        await self._rate_limiter.acquire(len(items))

        # Process based on modality
        if modality == ContentModality.TEXT:
            texts = [str(item.content) for _, item in items]
            return provider.embed_text_batch(texts)
        if modality == ContentModality.IMAGE:
            return [provider.embed_image(item.content) for _, item in items]  # type: ignore
        if modality == ContentModality.AUDIO:
            return [provider.embed_audio(item.content) for _, item in items]  # type: ignore
        if modality == ContentModality.VIDEO:
            return [provider.embed_video(item.content) for _, item in items]  # type: ignore

        # This should never happen, but satisfies exhaustiveness checking
        raise StageError(self.name, f"Unknown modality: {modality}")  # type: ignore[unreachable]

    def _track_cost(self, modality: ContentModality, result: EmbeddingResult) -> None:
        """Track cost metrics for an embedding result.

        Args:
            modality: The content modality.
            result: The embedding result.
        """
        if modality == ContentModality.TEXT and result.tokens_used:
            self._cost_metrics.total_tokens += result.tokens_used
        elif modality == ContentModality.IMAGE:
            self._cost_metrics.total_images += 1

        # Estimate cost based on provider cost info (if available)
        # This is simplified - real implementation would query provider metadata
        # For now, we track counts and leave cost estimation to the user

    def __str__(self) -> str:
        """Return string representation of the stage."""
        return (
            f"EmbeddingStage("
            f"batch_size={self._config.batch_size}, "
            f"rate_limit={self._config.rate_limit_per_second}/s, "
            f"caching={self._config.enable_caching})"
        )

    def __repr__(self) -> str:
        """Return detailed string representation."""
        return str(self)
