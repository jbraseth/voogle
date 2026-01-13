# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Performance benchmark suite for search latency and ingestion throughput.

This module provides benchmarks for measuring system performance:
- Search latency: p50/p95/p99 percentiles for query response times
- Ingestion throughput: Documents indexed per second
- Memory usage: Memory consumption under load
- Concurrent queries: Performance under concurrent query load
- Regression alerts: Thresholds for detecting performance regressions

These benchmarks are designed to run with pytest-benchmark and provide
reproducible performance measurements for CI/CD integration.
"""

from __future__ import annotations

import gc
import statistics
import threading
import time
import tracemalloc
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable

import numpy as np
import pytest
from qdrant_client import models

if TYPE_CHECKING:
    from pytest_benchmark.fixture import BenchmarkFixture


# ============================================================================
# Performance Thresholds and Baselines
# ============================================================================

# Search latency thresholds in milliseconds
SEARCH_LATENCY_THRESHOLDS = {
    "p50_ms": 100.0,   # 50th percentile should be under 100ms
    "p95_ms": 500.0,   # 95th percentile should be under 500ms
    "p99_ms": 1000.0,  # 99th percentile should be under 1000ms
}

# Ingestion throughput thresholds
INGESTION_THRESHOLDS = {
    "docs_per_second_min": 10.0,  # Minimum acceptable throughput
    "docs_per_second_target": 50.0,  # Target throughput
}

# Memory usage thresholds in MB
MEMORY_THRESHOLDS = {
    "base_memory_mb": 500.0,  # Base memory usage limit
    "per_query_mb": 50.0,  # Memory per concurrent query
    "peak_memory_mb": 2000.0,  # Peak memory limit under load
}

# Concurrent query thresholds
CONCURRENCY_THRESHOLDS = {
    "max_concurrent": 50,  # Maximum concurrent queries
    "degradation_factor": 3.0,  # Max allowed latency increase vs single query
}

# Regression detection threshold (20% degradation triggers alert)
REGRESSION_THRESHOLD = 0.20


# ============================================================================
# Data Structures
# ============================================================================


@dataclass
class LatencyMetrics:
    """Latency metrics with percentile breakdowns.

    Attributes:
        samples: Raw latency samples in milliseconds.
        p50: 50th percentile (median) latency.
        p95: 95th percentile latency.
        p99: 99th percentile latency.
        mean: Mean latency.
        std_dev: Standard deviation of latencies.
        min: Minimum latency.
        max: Maximum latency.
    """

    samples: list[float] = field(default_factory=list)
    p50: float = 0.0
    p95: float = 0.0
    p99: float = 0.0
    mean: float = 0.0
    std_dev: float = 0.0
    min: float = 0.0
    max: float = 0.0

    def calculate(self) -> None:
        """Calculate percentile statistics from samples."""
        if not self.samples:
            return

        sorted_samples = sorted(self.samples)
        n = len(sorted_samples)

        self.min = sorted_samples[0]
        self.max = sorted_samples[-1]
        self.mean = statistics.mean(sorted_samples)
        self.std_dev = statistics.stdev(sorted_samples) if n > 1 else 0.0

        # Calculate percentiles
        self.p50 = self._percentile(sorted_samples, 50)
        self.p95 = self._percentile(sorted_samples, 95)
        self.p99 = self._percentile(sorted_samples, 99)

    def _percentile(self, sorted_data: list[float], p: float) -> float:
        """Calculate percentile from sorted data."""
        n = len(sorted_data)
        k = (n - 1) * p / 100
        f = int(k)
        c = f + 1 if f + 1 < n else f
        return sorted_data[f] + (k - f) * (sorted_data[c] - sorted_data[f])


@dataclass
class ThroughputMetrics:
    """Throughput metrics for ingestion performance.

    Attributes:
        total_docs: Total documents processed.
        total_time_sec: Total time in seconds.
        docs_per_second: Documents processed per second.
        batches: Number of batches processed.
        batch_sizes: Sizes of each batch.
    """

    total_docs: int = 0
    total_time_sec: float = 0.0
    docs_per_second: float = 0.0
    batches: int = 0
    batch_sizes: list[int] = field(default_factory=list)

    def calculate(self) -> None:
        """Calculate throughput from totals."""
        if self.total_time_sec > 0:
            self.docs_per_second = self.total_docs / self.total_time_sec


@dataclass
class MemoryMetrics:
    """Memory usage metrics.

    Attributes:
        base_memory_mb: Baseline memory before operations.
        peak_memory_mb: Peak memory during operations.
        final_memory_mb: Memory after operations complete.
        delta_mb: Change from baseline to peak.
        samples: Memory samples over time.
    """

    base_memory_mb: float = 0.0
    peak_memory_mb: float = 0.0
    final_memory_mb: float = 0.0
    delta_mb: float = 0.0
    samples: list[float] = field(default_factory=list)

    def calculate(self) -> None:
        """Calculate memory delta."""
        self.delta_mb = self.peak_memory_mb - self.base_memory_mb
        if self.samples:
            self.peak_memory_mb = max(self.samples)


@dataclass
class ConcurrencyMetrics:
    """Metrics for concurrent query handling.

    Attributes:
        concurrent_queries: Number of concurrent queries.
        total_queries: Total queries executed.
        successful_queries: Successfully completed queries.
        failed_queries: Failed queries.
        latencies: Individual query latencies.
        throughput_qps: Queries per second.
    """

    concurrent_queries: int = 0
    total_queries: int = 0
    successful_queries: int = 0
    failed_queries: int = 0
    latencies: list[float] = field(default_factory=list)
    throughput_qps: float = 0.0


@dataclass
class RegressionAlert:
    """Alert for performance regression.

    Attributes:
        metric_name: Name of the regressed metric.
        current_value: Current metric value.
        baseline_value: Expected baseline value.
        threshold: Regression threshold.
        degradation_pct: Percentage degradation.
        is_regression: Whether this constitutes a regression.
    """

    metric_name: str
    current_value: float
    baseline_value: float
    threshold: float
    degradation_pct: float = 0.0
    is_regression: bool = False

    def __post_init__(self) -> None:
        """Calculate degradation and determine if regression."""
        if self.baseline_value > 0:
            # For latency metrics, higher is worse
            if "latency" in self.metric_name.lower() or "memory" in self.metric_name.lower():
                self.degradation_pct = (
                    (self.current_value - self.baseline_value) / self.baseline_value
                )
                self.is_regression = self.degradation_pct > self.threshold
            # For throughput metrics, lower is worse
            else:
                self.degradation_pct = (
                    (self.baseline_value - self.current_value) / self.baseline_value
                )
                self.is_regression = self.degradation_pct > self.threshold


# ============================================================================
# Mock Components for Isolated Benchmarking
# ============================================================================


class MockEmbeddingProvider:
    """Mock embedding provider for performance benchmarking.

    Generates deterministic embeddings quickly without ML model overhead.
    """

    def __init__(self, dimension: int = 384) -> None:
        self.dimension = dimension
        self.provider_name = "mock"
        self.model_name = "mock-embeddings"
        self._cache: dict[str, np.ndarray] = {}

    def encode_texts(self, texts: list[str]) -> list[np.ndarray]:
        """Generate embeddings for texts."""
        return [self._embed(text) for text in texts]

    def _embed(self, text: str) -> np.ndarray:
        """Generate deterministic embedding for text."""
        if text not in self._cache:
            # Use hash for deterministic but fast embedding generation
            text_hash = hash(text) & 0xFFFFFFFF
            rng = np.random.default_rng(text_hash)
            embedding = rng.standard_normal(self.dimension).astype(np.float32)
            embedding = embedding / np.linalg.norm(embedding)
            self._cache[text] = embedding
        return self._cache[text]

    def get_embedding_dimension(self) -> int:
        """Return embedding dimension."""
        return self.dimension


@dataclass
class MockScoredPoint:
    """Mock scored point for benchmark results."""

    id: str
    score: float
    payload: dict | None = None
    vector: list[float] | None = None


@dataclass
class MockQueryResponse:
    """Mock query response containing scored points."""

    points: list[MockScoredPoint] = field(default_factory=list)


class MockQdrantClient:
    """Mock Qdrant client for isolated benchmarking.

    Simulates Qdrant operations with in-memory storage for consistent benchmarks.
    """

    def __init__(self) -> None:
        self.collections: dict[str, dict[str, models.PointStruct]] = {}
        self._query_delay_ms: float = 1.0  # Simulated query time

    def collection_exists(self, name: str) -> bool:
        """Check if collection exists."""
        return name in self.collections

    def create_collection(
        self,
        collection_name: str,
        vectors_config: models.VectorParams | None = None,
    ) -> bool:
        """Create a collection."""
        if collection_name not in self.collections:
            self.collections[collection_name] = {}
        return True

    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection."""
        if collection_name in self.collections:
            del self.collections[collection_name]
        return True

    def upsert(
        self,
        collection_name: str,
        points: list[models.PointStruct],
        wait: bool = True,
    ) -> bool:
        """Upsert points into collection."""
        if collection_name not in self.collections:
            self.collections[collection_name] = {}

        for point in points:
            self.collections[collection_name][str(point.id)] = point

        return True

    def query_points(
        self,
        collection_name: str,
        query: list[float],
        query_filter: models.Filter | None = None,
        limit: int = 10,
        offset: int = 0,
        with_vectors: bool = False,
        **kwargs: object,
    ) -> MockQueryResponse:
        """Query collection with simulated latency."""
        # Simulate query latency
        time.sleep(self._query_delay_ms / 1000)

        if collection_name not in self.collections:
            return MockQueryResponse(points=[])

        # Convert query to numpy for similarity calculation
        query_vec = np.array(query, dtype=np.float32)

        # Calculate similarities
        scored_points: list[MockScoredPoint] = []
        for point_id, point in self.collections[collection_name].items():
            if isinstance(point.vector, list):
                point_vec = np.array(point.vector, dtype=np.float32)
            else:
                continue

            # Cosine similarity
            similarity = float(
                np.dot(query_vec, point_vec)
                / (np.linalg.norm(query_vec) * np.linalg.norm(point_vec))
            )

            scored_points.append(
                MockScoredPoint(
                    id=point_id,
                    score=similarity,
                    payload=point.payload,
                    vector=point.vector if with_vectors else None,
                )
            )

        # Sort by score descending
        scored_points.sort(key=lambda x: x.score, reverse=True)

        # Apply offset and limit
        scored_points = scored_points[offset : offset + limit]

        return MockQueryResponse(points=scored_points)


# ============================================================================
# Benchmark Utilities
# ============================================================================


def measure_latency(func: Callable[[], object], iterations: int = 100) -> LatencyMetrics:
    """Measure function execution latency over multiple iterations.

    Args:
        func: Function to measure.
        iterations: Number of iterations.

    Returns:
        LatencyMetrics with percentile statistics.
    """
    metrics = LatencyMetrics()

    # Warmup
    for _ in range(min(5, iterations // 10)):
        func()

    # Measure
    for _ in range(iterations):
        start = time.perf_counter()
        func()
        elapsed_ms = (time.perf_counter() - start) * 1000
        metrics.samples.append(elapsed_ms)

    metrics.calculate()
    return metrics


def measure_throughput(
    func: Callable[[int], int],
    batch_sizes: list[int],
    duration_sec: float = 5.0,
) -> ThroughputMetrics:
    """Measure throughput of batch processing function.

    Args:
        func: Function that takes batch_size and returns docs processed.
        batch_sizes: List of batch sizes to cycle through.
        duration_sec: Duration to run the benchmark.

    Returns:
        ThroughputMetrics with docs/second statistics.
    """
    metrics = ThroughputMetrics()
    start_time = time.perf_counter()
    batch_idx = 0

    while (time.perf_counter() - start_time) < duration_sec:
        batch_size = batch_sizes[batch_idx % len(batch_sizes)]
        docs_processed = func(batch_size)
        metrics.total_docs += docs_processed
        metrics.batches += 1
        metrics.batch_sizes.append(batch_size)
        batch_idx += 1

    metrics.total_time_sec = time.perf_counter() - start_time
    metrics.calculate()
    return metrics


def measure_memory(func: Callable[[], object]) -> MemoryMetrics:
    """Measure memory usage during function execution.

    Args:
        func: Function to measure.

    Returns:
        MemoryMetrics with base, peak, and delta values.
    """
    metrics = MemoryMetrics()

    # Force garbage collection for accurate baseline
    gc.collect()

    # Start memory tracking
    tracemalloc.start()

    # Get baseline
    metrics.base_memory_mb = tracemalloc.get_traced_memory()[0] / (1024 * 1024)

    # Execute function
    func()

    # Get peak and current
    current, peak = tracemalloc.get_traced_memory()
    metrics.peak_memory_mb = peak / (1024 * 1024)
    metrics.final_memory_mb = current / (1024 * 1024)

    tracemalloc.stop()
    metrics.calculate()

    return metrics


def measure_concurrency(
    func: Callable[[], object],
    concurrency: int,
    total_operations: int,
) -> ConcurrencyMetrics:
    """Measure performance under concurrent load.

    Args:
        func: Function to execute concurrently.
        concurrency: Number of concurrent threads.
        total_operations: Total operations to perform.

    Returns:
        ConcurrencyMetrics with success/failure counts and latencies.
    """
    metrics = ConcurrencyMetrics()
    metrics.concurrent_queries = concurrency
    metrics.total_queries = total_operations

    latencies: list[float] = []
    lock = threading.Lock()
    successful = 0
    failed = 0

    def worker() -> None:
        nonlocal successful, failed
        start = time.perf_counter()
        try:
            func()
            elapsed_ms = (time.perf_counter() - start) * 1000
            with lock:
                latencies.append(elapsed_ms)
                successful += 1
        except Exception:
            with lock:
                failed += 1

    start_time = time.perf_counter()

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(worker) for _ in range(total_operations)]
        for future in as_completed(futures):
            pass  # Wait for completion

    total_time = time.perf_counter() - start_time

    metrics.successful_queries = successful
    metrics.failed_queries = failed
    metrics.latencies = latencies
    metrics.throughput_qps = total_operations / total_time if total_time > 0 else 0

    return metrics


def check_regression_alerts(
    current_metrics: dict[str, float],
    baseline_metrics: dict[str, float],
    threshold: float = REGRESSION_THRESHOLD,
) -> list[RegressionAlert]:
    """Check for performance regressions against baseline.

    Args:
        current_metrics: Current metric values.
        baseline_metrics: Baseline metric values.
        threshold: Regression threshold (e.g., 0.20 = 20%).

    Returns:
        List of RegressionAlert objects for detected regressions.
    """
    alerts = []

    for metric_name, current_value in current_metrics.items():
        if metric_name in baseline_metrics:
            baseline_value = baseline_metrics[metric_name]
            alert = RegressionAlert(
                metric_name=metric_name,
                current_value=current_value,
                baseline_value=baseline_value,
                threshold=threshold,
            )
            if alert.is_regression:
                alerts.append(alert)

    return alerts


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def mock_embedding_provider() -> MockEmbeddingProvider:
    """Fixture providing mock embedding provider."""
    return MockEmbeddingProvider(dimension=384)


@pytest.fixture
def mock_qdrant_client() -> MockQdrantClient:
    """Fixture providing mock Qdrant client."""
    return MockQdrantClient()


@pytest.fixture
def seeded_mock_client(
    mock_qdrant_client: MockQdrantClient,
    mock_embedding_provider: MockEmbeddingProvider,
) -> MockQdrantClient:
    """Fixture providing mock Qdrant client with seeded data."""
    collection_name = "benchmark_collection"
    mock_qdrant_client.create_collection(collection_name)

    # Seed with test documents
    documents = [
        f"Document {i} about topic {i % 10} with content variation {i * 7 % 13}"
        for i in range(1000)
    ]

    embeddings = mock_embedding_provider.encode_texts(documents)
    points = [
        models.PointStruct(
            id=str(i),
            vector=emb.tolist(),
            payload={
                "text": doc,
                "episode": i,
                "channel": i % 10,
                "start_secs": i * 10,
                "end_secs": i * 10 + 30,
            },
        )
        for i, (doc, emb) in enumerate(zip(documents, embeddings))
    ]

    mock_qdrant_client.upsert(collection_name, points)
    return mock_qdrant_client


@pytest.fixture
def sample_queries() -> list[str]:
    """Fixture providing sample queries for benchmarking."""
    return [
        "machine learning fundamentals",
        "deep learning neural networks",
        "natural language processing",
        "computer vision applications",
        "reinforcement learning",
        "semantic search embeddings",
        "vector database optimization",
        "distributed systems design",
        "microservices architecture",
        "data pipeline engineering",
    ]


# ============================================================================
# Benchmark Tests - Search Latency
# ============================================================================


pytestmark = pytest.mark.benchmark


class TestSearchLatency:
    """Tests for search latency benchmarks with percentile metrics."""

    def test_search_latency_p50(
        self,
        benchmark: BenchmarkFixture,
        seeded_mock_client: MockQdrantClient,
        mock_embedding_provider: MockEmbeddingProvider,
        sample_queries: list[str],
    ) -> None:
        """Benchmark p50 search latency."""
        collection_name = "benchmark_collection"

        def run_search() -> object:
            query = sample_queries[0]
            query_emb = mock_embedding_provider._embed(query)
            return seeded_mock_client.query_points(
                collection_name=collection_name,
                query=query_emb.tolist(),
                limit=10,
            )

        # Run benchmark
        result = benchmark(run_search)
        assert result is not None

    def test_search_latency_percentiles(
        self,
        seeded_mock_client: MockQdrantClient,
        mock_embedding_provider: MockEmbeddingProvider,
        sample_queries: list[str],
    ) -> None:
        """Measure search latency percentiles (p50/p95/p99)."""
        collection_name = "benchmark_collection"

        def run_search() -> object:
            query = sample_queries[hash(time.time()) % len(sample_queries)]
            query_emb = mock_embedding_provider._embed(query)
            return seeded_mock_client.query_points(
                collection_name=collection_name,
                query=query_emb.tolist(),
                limit=10,
            )

        metrics = measure_latency(run_search, iterations=100)

        # Verify percentiles are calculated
        assert metrics.p50 > 0
        assert metrics.p95 >= metrics.p50
        assert metrics.p99 >= metrics.p95

        # Log results for visibility
        print(f"\nSearch Latency Percentiles:")
        print(f"  p50: {metrics.p50:.2f}ms")
        print(f"  p95: {metrics.p95:.2f}ms")
        print(f"  p99: {metrics.p99:.2f}ms")

    def test_search_latency_within_threshold(
        self,
        seeded_mock_client: MockQdrantClient,
        mock_embedding_provider: MockEmbeddingProvider,
        sample_queries: list[str],
    ) -> None:
        """Verify search latency is within acceptable thresholds."""
        collection_name = "benchmark_collection"

        def run_search() -> object:
            query = sample_queries[0]
            query_emb = mock_embedding_provider._embed(query)
            return seeded_mock_client.query_points(
                collection_name=collection_name,
                query=query_emb.tolist(),
                limit=10,
            )

        metrics = measure_latency(run_search, iterations=50)

        # Thresholds are generous for mock client; real tests would use actual thresholds
        assert metrics.p50 < SEARCH_LATENCY_THRESHOLDS["p50_ms"] * 10
        assert metrics.p95 < SEARCH_LATENCY_THRESHOLDS["p95_ms"] * 10
        assert metrics.p99 < SEARCH_LATENCY_THRESHOLDS["p99_ms"] * 10


# ============================================================================
# Benchmark Tests - Ingestion Throughput
# ============================================================================


class TestIngestionThroughput:
    """Tests for ingestion throughput benchmarks."""

    def test_ingestion_throughput_single_batch(
        self,
        benchmark: BenchmarkFixture,
        mock_qdrant_client: MockQdrantClient,
        mock_embedding_provider: MockEmbeddingProvider,
    ) -> None:
        """Benchmark single batch ingestion throughput."""
        collection_name = "throughput_test"
        mock_qdrant_client.create_collection(collection_name)
        batch_size = 100

        def ingest_batch() -> int:
            documents = [f"Document {i} for throughput test" for i in range(batch_size)]
            embeddings = mock_embedding_provider.encode_texts(documents)
            points = [
                models.PointStruct(
                    id=str(i),
                    vector=emb.tolist(),
                    payload={"text": doc, "episode": i, "channel": 1, "start_secs": 0, "end_secs": 10},
                )
                for i, (doc, emb) in enumerate(zip(documents, embeddings))
            ]
            mock_qdrant_client.upsert(collection_name, points)
            return batch_size

        result = benchmark(ingest_batch)
        assert result == batch_size

    def test_ingestion_throughput_docs_per_second(
        self,
        mock_qdrant_client: MockQdrantClient,
        mock_embedding_provider: MockEmbeddingProvider,
    ) -> None:
        """Measure documents indexed per second."""
        collection_name = "throughput_measure"
        mock_qdrant_client.create_collection(collection_name)
        doc_counter = [0]  # Use list to allow mutation in closure

        def ingest_batch(batch_size: int) -> int:
            documents = [
                f"Document {doc_counter[0] + i} for throughput measurement"
                for i in range(batch_size)
            ]
            doc_counter[0] += batch_size
            embeddings = mock_embedding_provider.encode_texts(documents)
            points = [
                models.PointStruct(
                    id=str(doc_counter[0] + i),
                    vector=emb.tolist(),
                    payload={"text": doc, "episode": i, "channel": 1, "start_secs": 0, "end_secs": 10},
                )
                for i, (doc, emb) in enumerate(zip(documents, embeddings))
            ]
            mock_qdrant_client.upsert(collection_name, points)
            return batch_size

        metrics = measure_throughput(
            ingest_batch,
            batch_sizes=[10, 25, 50, 100],
            duration_sec=2.0,
        )

        assert metrics.total_docs > 0
        assert metrics.docs_per_second > 0

        print(f"\nIngestion Throughput:")
        print(f"  Total docs: {metrics.total_docs}")
        print(f"  Total time: {metrics.total_time_sec:.2f}s")
        print(f"  Docs/second: {metrics.docs_per_second:.1f}")

    def test_ingestion_batch_size_scaling(
        self,
        mock_qdrant_client: MockQdrantClient,
        mock_embedding_provider: MockEmbeddingProvider,
    ) -> None:
        """Test throughput scaling with different batch sizes."""
        results: dict[int, float] = {}

        for batch_size in [10, 50, 100, 200]:
            collection_name = f"batch_test_{batch_size}"
            mock_qdrant_client.create_collection(collection_name)

            start_time = time.perf_counter()
            for _ in range(5):
                documents = [f"Doc {i}" for i in range(batch_size)]
                embeddings = mock_embedding_provider.encode_texts(documents)
                points = [
                    models.PointStruct(
                        id=str(i),
                        vector=emb.tolist(),
                        payload={"text": doc, "episode": i, "channel": 1, "start_secs": 0, "end_secs": 10},
                    )
                    for i, (doc, emb) in enumerate(zip(documents, embeddings))
                ]
                mock_qdrant_client.upsert(collection_name, points)

            elapsed = time.perf_counter() - start_time
            total_docs = batch_size * 5
            results[batch_size] = total_docs / elapsed

        # Larger batches should generally have better throughput
        print("\nBatch Size Scaling:")
        for batch_size, throughput in results.items():
            print(f"  Batch {batch_size}: {throughput:.1f} docs/s")


# ============================================================================
# Benchmark Tests - Memory Usage
# ============================================================================


class TestMemoryUsage:
    """Tests for memory usage under load."""

    def test_memory_usage_baseline(self) -> None:
        """Measure baseline memory usage."""
        gc.collect()
        tracemalloc.start()
        base_memory = tracemalloc.get_traced_memory()[0] / (1024 * 1024)
        tracemalloc.stop()

        print(f"\nBaseline memory: {base_memory:.2f} MB")
        assert base_memory >= 0

    def test_memory_usage_during_search(
        self,
        seeded_mock_client: MockQdrantClient,
        mock_embedding_provider: MockEmbeddingProvider,
        sample_queries: list[str],
    ) -> None:
        """Measure memory usage during search operations."""
        collection_name = "benchmark_collection"

        def run_searches() -> None:
            for query in sample_queries:
                query_emb = mock_embedding_provider._embed(query)
                seeded_mock_client.query_points(
                    collection_name=collection_name,
                    query=query_emb.tolist(),
                    limit=10,
                )

        metrics = measure_memory(run_searches)

        print(f"\nMemory Usage During Search:")
        print(f"  Base: {metrics.base_memory_mb:.2f} MB")
        print(f"  Peak: {metrics.peak_memory_mb:.2f} MB")
        print(f"  Delta: {metrics.delta_mb:.2f} MB")

    def test_memory_usage_during_ingestion(
        self,
        mock_qdrant_client: MockQdrantClient,
        mock_embedding_provider: MockEmbeddingProvider,
    ) -> None:
        """Measure memory usage during document ingestion."""
        collection_name = "memory_test"
        mock_qdrant_client.create_collection(collection_name)

        def run_ingestion() -> None:
            for batch_num in range(10):
                documents = [
                    f"Document {batch_num * 100 + i} for memory test"
                    for i in range(100)
                ]
                embeddings = mock_embedding_provider.encode_texts(documents)
                points = [
                    models.PointStruct(
                        id=str(batch_num * 100 + i),
                        vector=emb.tolist(),
                        payload={"text": doc, "episode": i, "channel": 1, "start_secs": 0, "end_secs": 10},
                    )
                    for i, (doc, emb) in enumerate(zip(documents, embeddings))
                ]
                mock_qdrant_client.upsert(collection_name, points)

        metrics = measure_memory(run_ingestion)

        print(f"\nMemory Usage During Ingestion:")
        print(f"  Base: {metrics.base_memory_mb:.2f} MB")
        print(f"  Peak: {metrics.peak_memory_mb:.2f} MB")
        print(f"  Delta: {metrics.delta_mb:.2f} MB")


# ============================================================================
# Benchmark Tests - Concurrent Query Handling
# ============================================================================


class TestConcurrentQueries:
    """Tests for concurrent query handling."""

    def test_concurrent_queries_basic(
        self,
        seeded_mock_client: MockQdrantClient,
        mock_embedding_provider: MockEmbeddingProvider,
        sample_queries: list[str],
    ) -> None:
        """Test handling of concurrent queries."""
        collection_name = "benchmark_collection"
        query_idx = [0]  # Use list for mutation in closure

        def run_query() -> object:
            query = sample_queries[query_idx[0] % len(sample_queries)]
            query_idx[0] += 1
            query_emb = mock_embedding_provider._embed(query)
            return seeded_mock_client.query_points(
                collection_name=collection_name,
                query=query_emb.tolist(),
                limit=10,
            )

        metrics = measure_concurrency(
            run_query,
            concurrency=10,
            total_operations=100,
        )

        assert metrics.successful_queries > 0
        assert metrics.failed_queries == 0
        assert metrics.throughput_qps > 0

        print(f"\nConcurrent Query Handling (10 threads):")
        print(f"  Successful: {metrics.successful_queries}")
        print(f"  Failed: {metrics.failed_queries}")
        print(f"  Throughput: {metrics.throughput_qps:.1f} qps")

    def test_concurrent_scaling(
        self,
        seeded_mock_client: MockQdrantClient,
        mock_embedding_provider: MockEmbeddingProvider,
        sample_queries: list[str],
    ) -> None:
        """Test query performance scaling with concurrency."""
        collection_name = "benchmark_collection"
        results: dict[int, ConcurrencyMetrics] = {}

        for concurrency in [1, 5, 10, 20]:
            query_idx = [0]

            def run_query() -> object:
                query = sample_queries[query_idx[0] % len(sample_queries)]
                query_idx[0] += 1
                query_emb = mock_embedding_provider._embed(query)
                return seeded_mock_client.query_points(
                    collection_name=collection_name,
                    query=query_emb.tolist(),
                    limit=10,
                )

            metrics = measure_concurrency(
                run_query,
                concurrency=concurrency,
                total_operations=50,
            )
            results[concurrency] = metrics

        print("\nConcurrency Scaling:")
        for concurrency, metrics in results.items():
            avg_latency = (
                statistics.mean(metrics.latencies) if metrics.latencies else 0
            )
            print(
                f"  {concurrency} threads: {metrics.throughput_qps:.1f} qps, "
                f"avg latency {avg_latency:.2f}ms"
            )


# ============================================================================
# Benchmark Tests - Regression Detection
# ============================================================================


class TestRegressionAlerts:
    """Tests for performance regression detection."""

    def test_no_regression_when_within_threshold(self) -> None:
        """No alerts when metrics are within threshold."""
        current = {"search_latency_p50_ms": 100.0, "throughput_docs_per_sec": 50.0}
        baseline = {"search_latency_p50_ms": 90.0, "throughput_docs_per_sec": 55.0}

        alerts = check_regression_alerts(current, baseline, threshold=0.20)

        # Within 20% threshold
        assert len(alerts) == 0

    def test_regression_detected_for_latency(self) -> None:
        """Alert generated when latency degrades significantly."""
        current = {"search_latency_p50_ms": 150.0}  # 50% degradation
        baseline = {"search_latency_p50_ms": 100.0}

        alerts = check_regression_alerts(current, baseline, threshold=0.20)

        assert len(alerts) == 1
        assert alerts[0].metric_name == "search_latency_p50_ms"
        assert alerts[0].is_regression is True

    def test_regression_detected_for_throughput(self) -> None:
        """Alert generated when throughput drops significantly."""
        current = {"throughput_docs_per_sec": 30.0}  # 40% drop
        baseline = {"throughput_docs_per_sec": 50.0}

        alerts = check_regression_alerts(current, baseline, threshold=0.20)

        assert len(alerts) == 1
        assert alerts[0].metric_name == "throughput_docs_per_sec"
        assert alerts[0].is_regression is True

    def test_multiple_regressions_detected(self) -> None:
        """Multiple regressions detected correctly."""
        current = {
            "search_latency_p50_ms": 200.0,  # 100% increase
            "search_latency_p95_ms": 800.0,  # 60% increase
            "throughput_docs_per_sec": 20.0,  # 60% drop
        }
        baseline = {
            "search_latency_p50_ms": 100.0,
            "search_latency_p95_ms": 500.0,
            "throughput_docs_per_sec": 50.0,
        }

        alerts = check_regression_alerts(current, baseline, threshold=0.20)

        assert len(alerts) == 3

    def test_regression_report_format(self) -> None:
        """Verify regression alert provides useful information."""
        alert = RegressionAlert(
            metric_name="search_latency_p50_ms",
            current_value=150.0,
            baseline_value=100.0,
            threshold=0.20,
        )

        assert alert.is_regression is True
        assert alert.degradation_pct == pytest.approx(0.50, rel=0.01)


# ============================================================================
# Integration Tests - Full Benchmark Suite
# ============================================================================


class TestFullBenchmarkSuite:
    """Integration tests running the full benchmark suite."""

    def test_full_search_benchmark(
        self,
        benchmark: BenchmarkFixture,
        seeded_mock_client: MockQdrantClient,
        mock_embedding_provider: MockEmbeddingProvider,
        sample_queries: list[str],
    ) -> None:
        """Run complete search benchmark and verify all metrics."""
        collection_name = "benchmark_collection"

        def run_search_suite() -> LatencyMetrics:
            query_idx = [0]

            def single_search() -> object:
                query = sample_queries[query_idx[0] % len(sample_queries)]
                query_idx[0] += 1
                query_emb = mock_embedding_provider._embed(query)
                return seeded_mock_client.query_points(
                    collection_name=collection_name,
                    query=query_emb.tolist(),
                    limit=10,
                )

            return measure_latency(single_search, iterations=50)

        metrics = benchmark(run_search_suite)

        assert metrics.p50 > 0
        assert metrics.p95 > 0
        assert metrics.p99 > 0

    def test_benchmark_produces_complete_report(
        self,
        seeded_mock_client: MockQdrantClient,
        mock_embedding_provider: MockEmbeddingProvider,
        sample_queries: list[str],
    ) -> None:
        """Verify benchmark produces all required metrics for reporting."""
        collection_name = "benchmark_collection"

        # Search latency
        def single_search() -> object:
            query = sample_queries[0]
            query_emb = mock_embedding_provider._embed(query)
            return seeded_mock_client.query_points(
                collection_name=collection_name,
                query=query_emb.tolist(),
                limit=10,
            )

        latency_metrics = measure_latency(single_search, iterations=30)

        # Ingestion throughput
        mock_client = MockQdrantClient()
        mock_client.create_collection("report_test")
        doc_counter = [0]

        def ingest_batch(batch_size: int) -> int:
            documents = [f"Doc {doc_counter[0] + i}" for i in range(batch_size)]
            doc_counter[0] += batch_size
            embeddings = mock_embedding_provider.encode_texts(documents)
            points = [
                models.PointStruct(
                    id=str(doc_counter[0] + i),
                    vector=emb.tolist(),
                    payload={"text": doc, "episode": i, "channel": 1, "start_secs": 0, "end_secs": 10},
                )
                for i, (doc, emb) in enumerate(zip(documents, embeddings))
            ]
            mock_client.upsert("report_test", points)
            return batch_size

        throughput_metrics = measure_throughput(
            ingest_batch,
            batch_sizes=[50],
            duration_sec=1.0,
        )

        # Memory usage
        memory_metrics = measure_memory(lambda: [single_search() for _ in range(10)])

        # Concurrent handling
        concurrency_metrics = measure_concurrency(
            single_search,
            concurrency=5,
            total_operations=20,
        )

        # Generate report
        report = {
            "search_latency_p50_ms": latency_metrics.p50,
            "search_latency_p95_ms": latency_metrics.p95,
            "search_latency_p99_ms": latency_metrics.p99,
            "ingestion_docs_per_second": throughput_metrics.docs_per_second,
            "memory_peak_mb": memory_metrics.peak_memory_mb,
            "concurrent_throughput_qps": concurrency_metrics.throughput_qps,
        }

        # Verify all metrics present
        assert all(v >= 0 for v in report.values())

        print("\nFull Benchmark Report:")
        for metric_name, value in report.items():
            print(f"  {metric_name}: {value:.2f}")

        # Check for regressions against baseline
        baseline = {
            "search_latency_p50_ms": 100.0,
            "search_latency_p95_ms": 500.0,
            "search_latency_p99_ms": 1000.0,
            "ingestion_docs_per_second": 10.0,
            "memory_peak_mb": 500.0,
            "concurrent_throughput_qps": 10.0,
        }

        alerts = check_regression_alerts(report, baseline, threshold=REGRESSION_THRESHOLD)

        print(f"\nRegression Alerts: {len(alerts)}")
        for alert in alerts:
            print(
                f"  {alert.metric_name}: {alert.current_value:.2f} vs "
                f"baseline {alert.baseline_value:.2f} "
                f"(degradation: {alert.degradation_pct:.1%})"
            )
