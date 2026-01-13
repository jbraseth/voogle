# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Embedding quality benchmark suite for retrieval evaluation.

This module provides benchmarks for evaluating embedding quality using standard
information retrieval metrics:
- MRR (Mean Reciprocal Rank): Average reciprocal rank of first relevant result
- NDCG@k (Normalized Discounted Cumulative Gain): Ranking quality at k
- Recall@k: Fraction of relevant documents retrieved at k

Benchmarks include:
- Labeled benchmark dataset with known relevance judgments
- Provider comparison between local and OpenAI embeddings
- Per-content-type breakdown (audio, text, web, etc.)
- Regression detection with baseline comparisons
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

import numpy as np
import pytest

if TYPE_CHECKING:
    from pytest_benchmark.fixture import BenchmarkFixture


class ContentType(str, Enum):
    """Content types for benchmark dataset."""

    AUDIO = "audio"
    TEXT = "text"
    WEB = "web"
    CODE = "code"
    PDF = "pdf"


@dataclass
class BenchmarkQuery:
    """A query with labeled relevance judgments for benchmarking.

    Attributes:
        query_id: Unique identifier for this query.
        query_text: The search query text.
        content_type: Content type this query targets.
        relevant_doc_ids: Set of document IDs that are relevant to this query.
        highly_relevant_doc_ids: Subset of docs that are highly relevant (grade 2).
    """

    query_id: str
    query_text: str
    content_type: ContentType
    relevant_doc_ids: set[str] = field(default_factory=set)
    highly_relevant_doc_ids: set[str] = field(default_factory=set)


@dataclass
class BenchmarkDocument:
    """A document in the benchmark dataset.

    Attributes:
        doc_id: Unique identifier for this document.
        text: The document text content.
        content_type: Type of content this document represents.
        embedding: Pre-computed embedding vector (optional).
    """

    doc_id: str
    text: str
    content_type: ContentType
    embedding: list[float] | None = None


@dataclass
class RetrievalResult:
    """A single retrieval result from the search system.

    Attributes:
        doc_id: Document identifier.
        score: Relevance score from the search system.
        rank: Position in the result list (1-indexed).
    """

    doc_id: str
    score: float
    rank: int


@dataclass
class BenchmarkDataset:
    """A complete benchmark dataset with queries and documents.

    Attributes:
        name: Dataset name/identifier.
        documents: List of benchmark documents.
        queries: List of benchmark queries with relevance judgments.
    """

    name: str
    documents: list[BenchmarkDocument]
    queries: list[BenchmarkQuery]

    def get_documents_by_type(self, content_type: ContentType) -> list[BenchmarkDocument]:
        """Get documents filtered by content type."""
        return [d for d in self.documents if d.content_type == content_type]

    def get_queries_by_type(self, content_type: ContentType) -> list[BenchmarkQuery]:
        """Get queries filtered by content type."""
        return [q for q in self.queries if q.content_type == content_type]


class RetrievalMetrics:
    """Calculator for information retrieval quality metrics."""

    @staticmethod
    def mrr(results_per_query: list[tuple[list[RetrievalResult], set[str]]]) -> float:
        """Calculate Mean Reciprocal Rank (MRR).

        MRR is the average of the reciprocal ranks of the first relevant
        document across all queries.

        Args:
            results_per_query: List of (results, relevant_doc_ids) tuples.

        Returns:
            MRR score between 0.0 and 1.0.
        """
        if not results_per_query:
            return 0.0

        reciprocal_ranks = []
        for results, relevant_ids in results_per_query:
            rr = 0.0
            for result in results:
                if result.doc_id in relevant_ids:
                    rr = 1.0 / result.rank
                    break
            reciprocal_ranks.append(rr)

        return sum(reciprocal_ranks) / len(reciprocal_ranks)

    @staticmethod
    def dcg_at_k(
        results: list[RetrievalResult],
        relevant_ids: set[str],
        highly_relevant_ids: set[str],
        k: int,
    ) -> float:
        """Calculate Discounted Cumulative Gain at k.

        Uses graded relevance: highly_relevant=2, relevant=1, non-relevant=0.

        Args:
            results: Ranked list of retrieval results.
            relevant_ids: Set of relevant document IDs.
            highly_relevant_ids: Set of highly relevant document IDs.
            k: Cutoff position.

        Returns:
            DCG@k score.
        """
        dcg = 0.0
        for i, result in enumerate(results[:k]):
            if result.doc_id in highly_relevant_ids:
                rel = 2
            elif result.doc_id in relevant_ids:
                rel = 1
            else:
                rel = 0
            # DCG formula: rel / log2(rank + 1)
            dcg += rel / math.log2(i + 2)  # i+2 because i is 0-indexed and log2(1)=0
        return dcg

    @staticmethod
    def ideal_dcg_at_k(
        relevant_ids: set[str],
        highly_relevant_ids: set[str],
        k: int,
    ) -> float:
        """Calculate ideal DCG at k (all relevant docs ranked at top).

        Args:
            relevant_ids: Set of relevant document IDs.
            highly_relevant_ids: Set of highly relevant document IDs.
            k: Cutoff position.

        Returns:
            IDCG@k score.
        """
        # Create ideal ranking: highly relevant first, then relevant
        ideal_rels = [2] * len(highly_relevant_ids) + [1] * (
            len(relevant_ids) - len(highly_relevant_ids)
        )
        ideal_rels = ideal_rels[:k]

        idcg = 0.0
        for i, rel in enumerate(ideal_rels):
            idcg += rel / math.log2(i + 2)
        return idcg

    @staticmethod
    def ndcg_at_k(
        results: list[RetrievalResult],
        relevant_ids: set[str],
        highly_relevant_ids: set[str],
        k: int,
    ) -> float:
        """Calculate Normalized Discounted Cumulative Gain at k.

        NDCG normalizes DCG by the ideal DCG, giving a score between 0 and 1.

        Args:
            results: Ranked list of retrieval results.
            relevant_ids: Set of relevant document IDs.
            highly_relevant_ids: Set of highly relevant document IDs.
            k: Cutoff position.

        Returns:
            NDCG@k score between 0.0 and 1.0.
        """
        dcg = RetrievalMetrics.dcg_at_k(results, relevant_ids, highly_relevant_ids, k)
        idcg = RetrievalMetrics.ideal_dcg_at_k(relevant_ids, highly_relevant_ids, k)

        if idcg == 0:
            return 0.0
        return dcg / idcg

    @staticmethod
    def recall_at_k(
        results: list[RetrievalResult],
        relevant_ids: set[str],
        k: int,
    ) -> float:
        """Calculate Recall at k.

        Recall@k is the fraction of relevant documents retrieved in top k results.

        Args:
            results: Ranked list of retrieval results.
            relevant_ids: Set of relevant document IDs.
            k: Cutoff position.

        Returns:
            Recall@k score between 0.0 and 1.0.
        """
        if not relevant_ids:
            return 0.0

        retrieved_relevant = sum(
            1 for r in results[:k] if r.doc_id in relevant_ids
        )
        return retrieved_relevant / len(relevant_ids)

    @staticmethod
    def mean_ndcg_at_k(
        results_per_query: list[
            tuple[list[RetrievalResult], set[str], set[str]]
        ],
        k: int,
    ) -> float:
        """Calculate mean NDCG@k across all queries.

        Args:
            results_per_query: List of (results, relevant_ids, highly_relevant_ids).
            k: Cutoff position.

        Returns:
            Mean NDCG@k score.
        """
        if not results_per_query:
            return 0.0

        ndcg_scores = [
            RetrievalMetrics.ndcg_at_k(results, rel_ids, high_rel_ids, k)
            for results, rel_ids, high_rel_ids in results_per_query
        ]
        return sum(ndcg_scores) / len(ndcg_scores)

    @staticmethod
    def mean_recall_at_k(
        results_per_query: list[tuple[list[RetrievalResult], set[str]]],
        k: int,
    ) -> float:
        """Calculate mean Recall@k across all queries.

        Args:
            results_per_query: List of (results, relevant_ids) tuples.
            k: Cutoff position.

        Returns:
            Mean Recall@k score.
        """
        if not results_per_query:
            return 0.0

        recall_scores = [
            RetrievalMetrics.recall_at_k(results, rel_ids, k)
            for results, rel_ids in results_per_query
        ]
        return sum(recall_scores) / len(recall_scores)


def create_labeled_benchmark_dataset() -> BenchmarkDataset:
    """Create a labeled benchmark dataset for testing.

    This creates a synthetic dataset with known relevance judgments
    for testing embedding quality metrics.

    Returns:
        BenchmarkDataset with documents and queries with relevance labels.
    """
    documents = [
        # Audio content
        BenchmarkDocument(
            doc_id="audio_001",
            text="The podcast discusses machine learning fundamentals and neural networks.",
            content_type=ContentType.AUDIO,
        ),
        BenchmarkDocument(
            doc_id="audio_002",
            text="Interview about deep learning applications in computer vision.",
            content_type=ContentType.AUDIO,
        ),
        BenchmarkDocument(
            doc_id="audio_003",
            text="Discussion on natural language processing and transformers.",
            content_type=ContentType.AUDIO,
        ),
        BenchmarkDocument(
            doc_id="audio_004",
            text="Episode about cooking traditional Italian pasta dishes.",
            content_type=ContentType.AUDIO,
        ),
        BenchmarkDocument(
            doc_id="audio_005",
            text="Talk about reinforcement learning and game playing AI.",
            content_type=ContentType.AUDIO,
        ),
        # Text content
        BenchmarkDocument(
            doc_id="text_001",
            text="Introduction to vector embeddings and similarity search.",
            content_type=ContentType.TEXT,
        ),
        BenchmarkDocument(
            doc_id="text_002",
            text="Guide to semantic search using sentence transformers.",
            content_type=ContentType.TEXT,
        ),
        BenchmarkDocument(
            doc_id="text_003",
            text="Tutorial on building a recipe search application.",
            content_type=ContentType.TEXT,
        ),
        BenchmarkDocument(
            doc_id="text_004",
            text="Article about retrieval augmented generation systems.",
            content_type=ContentType.TEXT,
        ),
        BenchmarkDocument(
            doc_id="text_005",
            text="Documentation for Qdrant vector database.",
            content_type=ContentType.TEXT,
        ),
        # Web content
        BenchmarkDocument(
            doc_id="web_001",
            text="Blog post about fine-tuning language models for search.",
            content_type=ContentType.WEB,
        ),
        BenchmarkDocument(
            doc_id="web_002",
            text="News article on advances in AI and machine learning.",
            content_type=ContentType.WEB,
        ),
        BenchmarkDocument(
            doc_id="web_003",
            text="Product page for cloud computing services.",
            content_type=ContentType.WEB,
        ),
        # Code content
        BenchmarkDocument(
            doc_id="code_001",
            text="Python function for calculating cosine similarity between vectors.",
            content_type=ContentType.CODE,
        ),
        BenchmarkDocument(
            doc_id="code_002",
            text="JavaScript module for handling API requests and responses.",
            content_type=ContentType.CODE,
        ),
        # PDF content
        BenchmarkDocument(
            doc_id="pdf_001",
            text="Research paper on attention mechanisms in neural networks.",
            content_type=ContentType.PDF,
        ),
        BenchmarkDocument(
            doc_id="pdf_002",
            text="Whitepaper about distributed vector search systems.",
            content_type=ContentType.PDF,
        ),
    ]

    queries = [
        # ML/AI queries
        BenchmarkQuery(
            query_id="q001",
            query_text="machine learning neural networks",
            content_type=ContentType.AUDIO,
            relevant_doc_ids={"audio_001", "audio_002", "audio_003", "audio_005"},
            highly_relevant_doc_ids={"audio_001", "audio_002"},
        ),
        BenchmarkQuery(
            query_id="q002",
            query_text="deep learning computer vision",
            content_type=ContentType.AUDIO,
            relevant_doc_ids={"audio_002", "audio_001"},
            highly_relevant_doc_ids={"audio_002"},
        ),
        BenchmarkQuery(
            query_id="q003",
            query_text="vector embeddings semantic search",
            content_type=ContentType.TEXT,
            relevant_doc_ids={"text_001", "text_002", "text_004", "text_005"},
            highly_relevant_doc_ids={"text_001", "text_002"},
        ),
        BenchmarkQuery(
            query_id="q004",
            query_text="language model fine-tuning",
            content_type=ContentType.WEB,
            relevant_doc_ids={"web_001", "web_002"},
            highly_relevant_doc_ids={"web_001"},
        ),
        BenchmarkQuery(
            query_id="q005",
            query_text="cosine similarity python",
            content_type=ContentType.CODE,
            relevant_doc_ids={"code_001"},
            highly_relevant_doc_ids={"code_001"},
        ),
        BenchmarkQuery(
            query_id="q006",
            query_text="attention mechanism transformer",
            content_type=ContentType.PDF,
            relevant_doc_ids={"pdf_001", "audio_003"},
            highly_relevant_doc_ids={"pdf_001"},
        ),
        BenchmarkQuery(
            query_id="q007",
            query_text="reinforcement learning games",
            content_type=ContentType.AUDIO,
            relevant_doc_ids={"audio_005"},
            highly_relevant_doc_ids={"audio_005"},
        ),
        BenchmarkQuery(
            query_id="q008",
            query_text="vector database distributed search",
            content_type=ContentType.PDF,
            relevant_doc_ids={"pdf_002", "text_005"},
            highly_relevant_doc_ids={"pdf_002"},
        ),
    ]

    return BenchmarkDataset(
        name="voogle-embedding-benchmark-v1",
        documents=documents,
        queries=queries,
    )


class MockEmbeddingProvider:
    """Mock embedding provider for benchmarking.

    Generates deterministic embeddings based on text content for testing.
    """

    def __init__(self, provider_name: str = "mock", dimension: int = 384) -> None:
        self.provider_name = provider_name
        self.dimension = dimension
        self._seed = 42

    def embed(self, text: str) -> np.ndarray:
        """Generate a deterministic embedding for text.

        Uses a hash-based approach to generate consistent embeddings.
        """
        # Use hash of text as seed for reproducibility
        text_hash = hash(text) & 0xFFFFFFFF
        rng = np.random.default_rng(text_hash)
        embedding = rng.standard_normal(self.dimension).astype(np.float32)
        # Normalize to unit length
        embedding = embedding / np.linalg.norm(embedding)
        return embedding

    def embed_batch(self, texts: list[str]) -> list[np.ndarray]:
        """Generate embeddings for a batch of texts."""
        return [self.embed(text) for text in texts]


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors."""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


class MockRetriever:
    """Mock retriever for benchmarking that uses cosine similarity."""

    def __init__(
        self,
        documents: list[BenchmarkDocument],
        provider: MockEmbeddingProvider,
    ) -> None:
        self.documents = documents
        self.provider = provider
        # Pre-compute document embeddings
        self.doc_embeddings = {
            doc.doc_id: provider.embed(doc.text) for doc in documents
        }

    def search(self, query: str, k: int = 10) -> list[RetrievalResult]:
        """Search for documents similar to query.

        Args:
            query: Query text.
            k: Number of results to return.

        Returns:
            List of RetrievalResult objects ranked by similarity.
        """
        query_embedding = self.provider.embed(query)

        # Calculate similarities
        similarities = [
            (doc_id, cosine_similarity(query_embedding, doc_emb))
            for doc_id, doc_emb in self.doc_embeddings.items()
        ]

        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Return top k results
        return [
            RetrievalResult(doc_id=doc_id, score=score, rank=i + 1)
            for i, (doc_id, score) in enumerate(similarities[:k])
        ]


# Baseline metrics for regression detection
BASELINE_METRICS = {
    "local": {
        "mrr": 0.5,
        "ndcg@10": 0.4,
        "recall@5": 0.3,
        "recall@10": 0.5,
    },
    "openai": {
        "mrr": 0.6,
        "ndcg@10": 0.5,
        "recall@5": 0.4,
        "recall@10": 0.6,
    },
}

# Regression threshold (allow 10% degradation before flagging)
REGRESSION_THRESHOLD = 0.10


@dataclass
class BenchmarkResult:
    """Results from a benchmark run.

    Attributes:
        provider_name: Name of the embedding provider.
        mrr: Mean Reciprocal Rank score.
        ndcg_at_10: NDCG@10 score.
        recall_at_5: Recall@5 score.
        recall_at_10: Recall@10 score.
        per_content_type: Metrics broken down by content type.
    """

    provider_name: str
    mrr: float
    ndcg_at_10: float
    recall_at_5: float
    recall_at_10: float
    per_content_type: dict[ContentType, dict[str, float]] = field(default_factory=dict)


def run_benchmark(
    dataset: BenchmarkDataset,
    provider: MockEmbeddingProvider,
    k_values: list[int] | None = None,
) -> BenchmarkResult:
    """Run benchmark evaluation on a dataset with given provider.

    Args:
        dataset: Benchmark dataset with queries and relevance judgments.
        provider: Embedding provider to evaluate.
        k_values: List of k values for recall@k metrics.

    Returns:
        BenchmarkResult with all computed metrics.
    """
    if k_values is None:
        k_values = [5, 10]
    retriever = MockRetriever(dataset.documents, provider)

    # Collect results for all queries
    mrr_data: list[tuple[list[RetrievalResult], set[str]]] = []
    ndcg_data: list[tuple[list[RetrievalResult], set[str], set[str]]] = []

    # Per content-type tracking
    type_mrr_data: dict[ContentType, list[tuple[list[RetrievalResult], set[str]]]] = {
        ct: [] for ct in ContentType
    }
    type_ndcg_data: dict[
        ContentType, list[tuple[list[RetrievalResult], set[str], set[str]]]
    ] = {ct: [] for ct in ContentType}

    for query in dataset.queries:
        results = retriever.search(query.query_text, k=max(k_values))

        mrr_data.append((results, query.relevant_doc_ids))
        ndcg_data.append(
            (results, query.relevant_doc_ids, query.highly_relevant_doc_ids)
        )

        type_mrr_data[query.content_type].append((results, query.relevant_doc_ids))
        type_ndcg_data[query.content_type].append(
            (results, query.relevant_doc_ids, query.highly_relevant_doc_ids)
        )

    # Calculate overall metrics
    mrr = RetrievalMetrics.mrr(mrr_data)
    ndcg_at_10 = RetrievalMetrics.mean_ndcg_at_k(ndcg_data, 10)
    recall_at_5 = RetrievalMetrics.mean_recall_at_k(mrr_data, 5)
    recall_at_10 = RetrievalMetrics.mean_recall_at_k(mrr_data, 10)

    # Calculate per content-type metrics
    per_content_type = {}
    for content_type in ContentType:
        if type_mrr_data[content_type]:
            per_content_type[content_type] = {
                "mrr": RetrievalMetrics.mrr(type_mrr_data[content_type]),
                "ndcg@10": RetrievalMetrics.mean_ndcg_at_k(
                    type_ndcg_data[content_type], 10
                ),
                "recall@5": RetrievalMetrics.mean_recall_at_k(
                    type_mrr_data[content_type], 5
                ),
                "recall@10": RetrievalMetrics.mean_recall_at_k(
                    type_mrr_data[content_type], 10
                ),
            }

    return BenchmarkResult(
        provider_name=provider.provider_name,
        mrr=mrr,
        ndcg_at_10=ndcg_at_10,
        recall_at_5=recall_at_5,
        recall_at_10=recall_at_10,
        per_content_type=per_content_type,
    )


def check_regression(
    current: BenchmarkResult,
    baseline: dict[str, float],
    threshold: float = REGRESSION_THRESHOLD,
) -> list[str]:
    """Check for metric regressions against baseline.

    Args:
        current: Current benchmark results.
        baseline: Baseline metrics to compare against.
        threshold: Allowed relative degradation (e.g., 0.10 = 10%).

    Returns:
        List of regression warnings (empty if no regressions).
    """
    warnings = []

    metrics = [
        ("mrr", current.mrr),
        ("ndcg@10", current.ndcg_at_10),
        ("recall@5", current.recall_at_5),
        ("recall@10", current.recall_at_10),
    ]

    for metric_name, current_value in metrics:
        if metric_name in baseline:
            baseline_value = baseline[metric_name]
            if baseline_value > 0:
                degradation = (baseline_value - current_value) / baseline_value
                if degradation > threshold:
                    warnings.append(
                        f"{metric_name} regressed: {current_value:.3f} vs baseline {baseline_value:.3f} "
                        f"(degradation: {degradation:.1%}, threshold: {threshold:.1%})"
                    )

    return warnings


# ============================================================================
# Pytest Benchmark Tests
# ============================================================================


pytestmark = pytest.mark.benchmark


@pytest.fixture
def benchmark_dataset() -> BenchmarkDataset:
    """Fixture providing the labeled benchmark dataset."""
    return create_labeled_benchmark_dataset()


@pytest.fixture
def local_provider() -> MockEmbeddingProvider:
    """Fixture providing a mock local embedding provider."""
    return MockEmbeddingProvider(provider_name="local", dimension=384)


@pytest.fixture
def openai_provider() -> MockEmbeddingProvider:
    """Fixture providing a mock OpenAI-like embedding provider."""
    return MockEmbeddingProvider(provider_name="openai", dimension=1536)


class TestRetrievalMetrics:
    """Tests for retrieval metric calculations."""

    def test_mrr_perfect_ranking(self) -> None:
        """MRR is 1.0 when first result is always relevant."""
        results = [
            RetrievalResult(doc_id="a", score=0.9, rank=1),
            RetrievalResult(doc_id="b", score=0.8, rank=2),
        ]
        relevant = {"a"}

        mrr = RetrievalMetrics.mrr([(results, relevant)])
        assert mrr == 1.0

    def test_mrr_second_position(self) -> None:
        """MRR is 0.5 when first relevant is at position 2."""
        results = [
            RetrievalResult(doc_id="a", score=0.9, rank=1),
            RetrievalResult(doc_id="b", score=0.8, rank=2),
        ]
        relevant = {"b"}

        mrr = RetrievalMetrics.mrr([(results, relevant)])
        assert mrr == 0.5

    def test_mrr_no_relevant(self) -> None:
        """MRR is 0.0 when no relevant documents retrieved."""
        results = [
            RetrievalResult(doc_id="a", score=0.9, rank=1),
        ]
        relevant = {"x"}

        mrr = RetrievalMetrics.mrr([(results, relevant)])
        assert mrr == 0.0

    def test_ndcg_perfect_ranking(self) -> None:
        """NDCG@k is 1.0 when ranking is optimal."""
        results = [
            RetrievalResult(doc_id="a", score=0.9, rank=1),
            RetrievalResult(doc_id="b", score=0.8, rank=2),
        ]
        relevant = {"a", "b"}
        highly_relevant = {"a"}

        ndcg = RetrievalMetrics.ndcg_at_k(results, relevant, highly_relevant, k=2)
        assert ndcg == pytest.approx(1.0, rel=0.01)

    def test_ndcg_reverse_ranking(self) -> None:
        """NDCG@k is less than 1.0 when ranking is suboptimal."""
        results = [
            RetrievalResult(doc_id="b", score=0.9, rank=1),  # relevant, not highly
            RetrievalResult(doc_id="a", score=0.8, rank=2),  # highly relevant
        ]
        relevant = {"a", "b"}
        highly_relevant = {"a"}

        ndcg = RetrievalMetrics.ndcg_at_k(results, relevant, highly_relevant, k=2)
        assert 0.0 < ndcg < 1.0

    def test_recall_at_k(self) -> None:
        """Recall@k correctly counts retrieved relevant docs."""
        results = [
            RetrievalResult(doc_id="a", score=0.9, rank=1),
            RetrievalResult(doc_id="b", score=0.8, rank=2),
            RetrievalResult(doc_id="c", score=0.7, rank=3),
        ]
        relevant = {"a", "c", "d"}  # 2 of 3 in results

        recall = RetrievalMetrics.recall_at_k(results, relevant, k=3)
        assert recall == pytest.approx(2 / 3, rel=0.01)


class TestBenchmarkDataset:
    """Tests for benchmark dataset creation and validation."""

    def test_dataset_has_documents(self, benchmark_dataset: BenchmarkDataset) -> None:
        """Dataset contains expected documents."""
        assert len(benchmark_dataset.documents) > 0

    def test_dataset_has_queries(self, benchmark_dataset: BenchmarkDataset) -> None:
        """Dataset contains expected queries."""
        assert len(benchmark_dataset.queries) > 0

    def test_all_content_types_covered(
        self, benchmark_dataset: BenchmarkDataset
    ) -> None:
        """Dataset covers all content types."""
        doc_types = {d.content_type for d in benchmark_dataset.documents}
        query_types = {q.content_type for q in benchmark_dataset.queries}

        for content_type in ContentType:
            assert content_type in doc_types
            assert content_type in query_types

    def test_relevant_docs_exist(self, benchmark_dataset: BenchmarkDataset) -> None:
        """All referenced relevant doc IDs exist in dataset."""
        doc_ids = {d.doc_id for d in benchmark_dataset.documents}

        for query in benchmark_dataset.queries:
            for doc_id in query.relevant_doc_ids:
                assert doc_id in doc_ids, f"Missing doc {doc_id} for query {query.query_id}"


class TestMockProvider:
    """Tests for mock embedding provider."""

    def test_embedding_dimension(self, local_provider: MockEmbeddingProvider) -> None:
        """Provider generates embeddings with correct dimension."""
        embedding = local_provider.embed("test text")
        assert embedding.shape == (local_provider.dimension,)

    def test_embedding_normalized(self, local_provider: MockEmbeddingProvider) -> None:
        """Provider generates unit-normalized embeddings."""
        embedding = local_provider.embed("test text")
        norm = np.linalg.norm(embedding)
        assert norm == pytest.approx(1.0, rel=0.01)

    def test_embedding_deterministic(
        self, local_provider: MockEmbeddingProvider
    ) -> None:
        """Same text produces same embedding."""
        emb1 = local_provider.embed("test text")
        emb2 = local_provider.embed("test text")
        np.testing.assert_array_equal(emb1, emb2)

    def test_different_texts_different_embeddings(
        self, local_provider: MockEmbeddingProvider
    ) -> None:
        """Different texts produce different embeddings."""
        emb1 = local_provider.embed("text one")
        emb2 = local_provider.embed("text two")
        assert not np.array_equal(emb1, emb2)


class TestBenchmarkRun:
    """Tests for running the full benchmark."""

    def test_benchmark_produces_metrics(
        self,
        benchmark_dataset: BenchmarkDataset,
        local_provider: MockEmbeddingProvider,
    ) -> None:
        """Benchmark run produces all expected metrics."""
        result = run_benchmark(benchmark_dataset, local_provider)

        assert 0.0 <= result.mrr <= 1.0
        assert 0.0 <= result.ndcg_at_10 <= 1.0
        assert 0.0 <= result.recall_at_5 <= 1.0
        assert 0.0 <= result.recall_at_10 <= 1.0

    def test_benchmark_has_content_type_breakdown(
        self,
        benchmark_dataset: BenchmarkDataset,
        local_provider: MockEmbeddingProvider,
    ) -> None:
        """Benchmark produces per-content-type metrics."""
        result = run_benchmark(benchmark_dataset, local_provider)

        # Check that we have metrics for content types with queries
        assert ContentType.AUDIO in result.per_content_type
        assert ContentType.TEXT in result.per_content_type

        # Check content type metrics structure
        for ct_metrics in result.per_content_type.values():
            assert "mrr" in ct_metrics
            assert "ndcg@10" in ct_metrics
            assert "recall@5" in ct_metrics
            assert "recall@10" in ct_metrics


class TestProviderComparison:
    """Tests for comparing different embedding providers."""

    def test_compare_providers(
        self,
        benchmark_dataset: BenchmarkDataset,
        local_provider: MockEmbeddingProvider,
        openai_provider: MockEmbeddingProvider,
    ) -> None:
        """Compare metrics between local and OpenAI providers."""
        local_result = run_benchmark(benchmark_dataset, local_provider)
        openai_result = run_benchmark(benchmark_dataset, openai_provider)

        # Both should produce valid metrics
        assert local_result.provider_name == "local"
        assert openai_result.provider_name == "openai"

        # Metrics should be in valid range
        for result in [local_result, openai_result]:
            assert 0.0 <= result.mrr <= 1.0
            assert 0.0 <= result.ndcg_at_10 <= 1.0


class TestRegressionDetection:
    """Tests for regression detection logic."""

    def test_no_regression_when_above_baseline(self) -> None:
        """No warnings when all metrics are above baseline."""
        result = BenchmarkResult(
            provider_name="local",
            mrr=0.6,
            ndcg_at_10=0.5,
            recall_at_5=0.4,
            recall_at_10=0.6,
        )
        baseline = {"mrr": 0.5, "ndcg@10": 0.4, "recall@5": 0.3, "recall@10": 0.5}

        warnings = check_regression(result, baseline)
        assert len(warnings) == 0

    def test_regression_detected_when_below_threshold(self) -> None:
        """Warning generated when metric drops below threshold."""
        result = BenchmarkResult(
            provider_name="local",
            mrr=0.4,  # 20% below baseline of 0.5
            ndcg_at_10=0.5,
            recall_at_5=0.4,
            recall_at_10=0.6,
        )
        baseline = {"mrr": 0.5, "ndcg@10": 0.4, "recall@5": 0.3, "recall@10": 0.5}

        warnings = check_regression(result, baseline, threshold=0.10)
        assert len(warnings) == 1
        assert "mrr" in warnings[0]

    def test_small_regression_allowed(self) -> None:
        """Small regressions within threshold don't trigger warning."""
        result = BenchmarkResult(
            provider_name="local",
            mrr=0.47,  # 6% below baseline of 0.5
            ndcg_at_10=0.5,
            recall_at_5=0.4,
            recall_at_10=0.6,
        )
        baseline = {"mrr": 0.5, "ndcg@10": 0.4, "recall@5": 0.3, "recall@10": 0.5}

        warnings = check_regression(result, baseline, threshold=0.10)
        assert len(warnings) == 0


# ============================================================================
# Pytest-Benchmark Integration Tests
# ============================================================================


class TestBenchmarkPerformance:
    """Performance benchmarks using pytest-benchmark."""

    def test_mrr_calculation_performance(
        self,
        benchmark: BenchmarkFixture,
        benchmark_dataset: BenchmarkDataset,  # noqa: ARG002
    ) -> None:
        """Benchmark MRR calculation performance."""
        # Note: benchmark_dataset fixture validates dataset is loadable
        # Prepare synthetic test data for isolated metric performance
        results = [
            RetrievalResult(doc_id=f"doc_{i}", score=0.9 - i * 0.01, rank=i + 1)
            for i in range(100)
        ]
        relevant = {f"doc_{i}" for i in range(0, 100, 10)}

        data = [(results, relevant) for _ in range(100)]

        def run() -> float:
            return RetrievalMetrics.mrr(data)

        result = benchmark(run)
        assert 0.0 <= result <= 1.0

    def test_ndcg_calculation_performance(
        self, benchmark: BenchmarkFixture
    ) -> None:
        """Benchmark NDCG@k calculation performance."""
        results = [
            RetrievalResult(doc_id=f"doc_{i}", score=0.9 - i * 0.01, rank=i + 1)
            for i in range(100)
        ]
        relevant = {f"doc_{i}" for i in range(0, 100, 5)}
        highly_relevant = {f"doc_{i}" for i in range(0, 100, 10)}

        def run() -> float:
            return RetrievalMetrics.ndcg_at_k(results, relevant, highly_relevant, k=10)

        result = benchmark(run)
        assert 0.0 <= result <= 1.0

    def test_embedding_generation_performance(
        self, benchmark: BenchmarkFixture, local_provider: MockEmbeddingProvider
    ) -> None:
        """Benchmark embedding generation performance."""
        texts = [f"Sample text number {i} for embedding generation" for i in range(100)]

        def run() -> list[np.ndarray]:
            return local_provider.embed_batch(texts)

        embeddings = benchmark(run)
        assert len(embeddings) == 100

    def test_full_benchmark_run_performance(
        self,
        benchmark: BenchmarkFixture,
        benchmark_dataset: BenchmarkDataset,
        local_provider: MockEmbeddingProvider,
    ) -> None:
        """Benchmark full evaluation run performance."""

        def run() -> BenchmarkResult:
            return run_benchmark(benchmark_dataset, local_provider)

        result = benchmark(run)
        assert result.provider_name == "local"


# ============================================================================
# Integration with Real Providers (Optional)
# ============================================================================


@pytest.mark.skipif(
    True,  # Skip by default - enable with proper setup
    reason="Requires real embedding providers",
)
class TestRealProviderBenchmarks:
    """Benchmarks using real embedding providers.

    These tests are skipped by default and require proper setup of
    embedding providers (local sentence-transformers or OpenAI API key).
    """

    def test_real_local_provider_benchmark(
        self,
        benchmark: BenchmarkFixture,
        benchmark_dataset: BenchmarkDataset,
    ) -> None:
        """Benchmark with real local sentence-transformers provider."""
        # Skipped by default - parameters preserved for interface consistency
        # To enable: remove skipif decorator and implement real provider setup
        _ = benchmark, benchmark_dataset  # Mark as used for linter

    def test_real_openai_provider_benchmark(
        self,
        benchmark: BenchmarkFixture,
        benchmark_dataset: BenchmarkDataset,
    ) -> None:
        """Benchmark with real OpenAI embeddings provider."""
        # Skipped by default - parameters preserved for interface consistency
        # To enable: remove skipif decorator and implement real provider setup
        _ = benchmark, benchmark_dataset  # Mark as used for linter
