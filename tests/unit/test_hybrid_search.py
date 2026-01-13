# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for hybrid search with sparse vectors and RRF fusion."""
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from voogle.embedding.sparse import (
    BM25Config,
    BM25Encoder,
    SparseEncoder,
    SparseVector,
    get_sparse_encoder,
)
from voogle.services.search import SearchMode, SearchQuery, SearchService
from voogle.vector_schema import VectorName, get_collection_config

pytestmark = pytest.mark.unit


class TestSparseVector:
    """Tests for SparseVector dataclass."""

    @pytest.mark.description("SparseVector creates with indices and values")
    def test_create_sparse_vector(self) -> None:
        vector = SparseVector(indices=[1, 5, 10], values=[0.5, 0.8, 0.3])
        assert vector.indices == [1, 5, 10]
        assert vector.values == [0.5, 0.8, 0.3]

    @pytest.mark.description("SparseVector to_dict returns correct format")
    def test_to_dict(self) -> None:
        vector = SparseVector(indices=[1, 2], values=[0.5, 0.6])
        result = vector.to_dict()
        assert result == {"indices": [1, 2], "values": [0.5, 0.6]}

    @pytest.mark.description("SparseVector len returns number of non-zero dimensions")
    def test_len(self) -> None:
        vector = SparseVector(indices=[1, 2, 3, 4], values=[0.1, 0.2, 0.3, 0.4])
        assert len(vector) == 4

    @pytest.mark.description("Empty SparseVector has length 0")
    def test_empty_vector(self) -> None:
        vector = SparseVector(indices=[], values=[])
        assert len(vector) == 0


class TestBM25Config:
    """Tests for BM25Config dataclass."""

    @pytest.mark.description("BM25Config uses sensible defaults")
    def test_default_config(self) -> None:
        config = BM25Config()
        assert config.k1 == 1.5
        assert config.b == 0.75
        assert config.avg_doc_length == 256.0
        assert config.min_token_length == 2
        assert isinstance(config.stopwords, set)
        assert "the" in config.stopwords

    @pytest.mark.description("BM25Config accepts custom parameters")
    def test_custom_config(self) -> None:
        config = BM25Config(k1=2.0, b=0.5, avg_doc_length=100.0)
        assert config.k1 == 2.0
        assert config.b == 0.5
        assert config.avg_doc_length == 100.0


class TestBM25Encoder:
    """Tests for BM25Encoder class."""

    @pytest.mark.description("BM25Encoder initializes with default config")
    def test_init_default(self) -> None:
        encoder = BM25Encoder()
        assert encoder.config.k1 == 1.5
        assert encoder.method_name == "bm25"

    @pytest.mark.description("BM25Encoder initializes with custom config")
    def test_init_custom(self) -> None:
        config = BM25Config(k1=2.0)
        encoder = BM25Encoder(config)
        assert encoder.config.k1 == 2.0

    @pytest.mark.description("BM25Encoder encodes simple text")
    def test_encode_simple(self) -> None:
        encoder = BM25Encoder()
        vector = encoder.encode("hello world")
        assert isinstance(vector, SparseVector)
        assert len(vector) > 0
        assert all(isinstance(i, int) for i in vector.indices)
        assert all(isinstance(v, float) for v in vector.values)

    @pytest.mark.description("BM25Encoder filters stopwords")
    def test_stopword_filtering(self) -> None:
        encoder = BM25Encoder()
        # "the" is a stopword
        vector1 = encoder.encode("the quick fox")
        vector2 = encoder.encode("quick fox")
        # Both should have same non-stopword tokens
        assert len(vector1) == len(vector2)

    @pytest.mark.description("BM25Encoder filters short tokens")
    def test_short_token_filtering(self) -> None:
        encoder = BM25Encoder()
        # "a" is too short (min_token_length=2)
        vector = encoder.encode("a big dog")
        # Should only include "big" and "dog"
        assert len(vector) == 2

    @pytest.mark.description("BM25Encoder returns empty for empty text")
    def test_encode_empty(self) -> None:
        encoder = BM25Encoder()
        vector = encoder.encode("")
        assert len(vector) == 0

    @pytest.mark.description("BM25Encoder returns empty for stopwords only")
    def test_encode_stopwords_only(self) -> None:
        encoder = BM25Encoder()
        vector = encoder.encode("the a an")
        assert len(vector) == 0

    @pytest.mark.description("BM25Encoder encodes batch correctly")
    def test_encode_batch(self) -> None:
        encoder = BM25Encoder()
        texts = ["hello world", "foo bar", "test query"]
        vectors = encoder.encode_batch(texts)
        assert len(vectors) == 3
        assert all(isinstance(v, SparseVector) for v in vectors)

    @pytest.mark.description("BM25Encoder term frequency affects weights")
    def test_term_frequency_weighting(self) -> None:
        encoder = BM25Encoder()
        # Repeated terms should have higher weight
        vector1 = encoder.encode("python")
        vector2 = encoder.encode("python python python")
        # Find the python term weight in each
        idx = vector1.indices[0]  # There's only one term
        weight1 = vector1.values[0]
        weight2 = vector2.values[vector2.indices.index(idx)]
        # More occurrences should give higher weight (with saturation)
        assert weight2 > weight1


class TestSparseEncoder:
    """Tests for SparseEncoder factory class."""

    @pytest.mark.description("SparseEncoder creates BM25 encoder by default")
    def test_default_method(self) -> None:
        encoder = SparseEncoder()
        assert encoder.method == "bm25"
        assert "bm25" in str(encoder)

    @pytest.mark.description("SparseEncoder creates BM25 encoder explicitly")
    def test_bm25_method(self) -> None:
        encoder = SparseEncoder(method="bm25")
        assert encoder.method == "bm25"

    @pytest.mark.description("SparseEncoder raises for unknown method")
    def test_unknown_method_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown sparse encoding method"):
            SparseEncoder(method="unknown")

    @pytest.mark.description("SparseEncoder encode delegates to underlying encoder")
    def test_encode_delegation(self) -> None:
        encoder = SparseEncoder()
        vector = encoder.encode("test query")
        assert isinstance(vector, SparseVector)

    @pytest.mark.description("SparseEncoder encode_batch delegates correctly")
    def test_encode_batch_delegation(self) -> None:
        encoder = SparseEncoder()
        vectors = encoder.encode_batch(["hello", "world"])
        assert len(vectors) == 2

    @pytest.mark.description("SparseEncoder accepts BM25 config")
    def test_bm25_config(self) -> None:
        config = BM25Config(k1=3.0)
        encoder = SparseEncoder(method="bm25", bm25_config=config)
        assert encoder._encoder.config.k1 == 3.0


class TestGetSparseEncoder:
    """Tests for get_sparse_encoder cached factory."""

    @pytest.mark.description("get_sparse_encoder returns BM25 by default")
    def test_default_encoder(self) -> None:
        # Clear cache first
        get_sparse_encoder.cache_clear()
        encoder = get_sparse_encoder()
        assert encoder.method == "bm25"

    @pytest.mark.description("get_sparse_encoder caches encoder instances")
    def test_caching(self) -> None:
        get_sparse_encoder.cache_clear()
        encoder1 = get_sparse_encoder("bm25")
        encoder2 = get_sparse_encoder("bm25")
        assert encoder1 is encoder2


class TestVectorSchemaWithSparse:
    """Tests for vector schema with sparse vector support."""

    @pytest.mark.description("Collection config includes sparse vector")
    def test_config_includes_sparse(self) -> None:
        config = get_collection_config()
        assert VectorName.TEXT_SPARSE.value in config.vectors_config

    @pytest.mark.description("Sparse vector uses SparseVectorParams")
    def test_sparse_vector_params(self) -> None:
        from qdrant_client import models

        config = get_collection_config()
        sparse_config = config.vectors_config[VectorName.TEXT_SPARSE.value]
        assert isinstance(sparse_config, models.SparseVectorParams)


class TestSearchServiceWithSparse:
    """Tests for SearchService with sparse encoder."""

    @pytest.mark.description("SearchService initializes with sparse encoder")
    def test_init_with_sparse_encoder(self) -> None:
        mock_encoder = MagicMock()
        service = SearchService(sparse_encoder=mock_encoder)
        assert service._sparse_encoder == mock_encoder

    @pytest.mark.description("SearchService lazy-loads sparse encoder")
    def test_lazy_load_sparse_encoder(self) -> None:
        service = SearchService()
        assert service._sparse_encoder is None
        # Access triggers lazy load
        encoder = service.sparse_encoder
        assert encoder is not None
        assert encoder.method == "bm25"

    @pytest.mark.description("SearchService repr includes sparse encoder")
    def test_repr_includes_sparse(self) -> None:
        service = SearchService()
        result = repr(service)
        assert "sparse_encoder" in result


class TestSearchModeEnum:
    """Tests for SearchMode enum."""

    @pytest.mark.description("SearchMode has dense, sparse, and hybrid modes")
    def test_search_modes(self) -> None:
        assert SearchMode.DENSE.value == "dense"
        assert SearchMode.SPARSE.value == "sparse"
        assert SearchMode.HYBRID.value == "hybrid"

    @pytest.mark.description("SearchMode can be created from string")
    def test_from_string(self) -> None:
        assert SearchMode("dense") == SearchMode.DENSE
        assert SearchMode("sparse") == SearchMode.SPARSE
        assert SearchMode("hybrid") == SearchMode.HYBRID


class TestSearchQueryWithMode:
    """Tests for SearchQuery with mode parameter."""

    @pytest.mark.description("SearchQuery defaults to DENSE mode")
    def test_default_mode(self) -> None:
        query = SearchQuery(query_text="test")
        assert query.mode == SearchMode.DENSE

    @pytest.mark.description("SearchQuery accepts HYBRID mode")
    def test_hybrid_mode(self) -> None:
        query = SearchQuery(query_text="test", mode=SearchMode.HYBRID)
        assert query.mode == SearchMode.HYBRID

    @pytest.mark.description("SearchQuery accepts SPARSE mode")
    def test_sparse_mode(self) -> None:
        query = SearchQuery(query_text="test", mode=SearchMode.SPARSE)
        assert query.mode == SearchMode.SPARSE


class TestHybridSearchIntegration:
    """Integration tests for hybrid search with mocked dependencies."""

    @pytest.mark.description("Hybrid search falls back when sparse not available")
    def test_hybrid_fallback_no_sparse(self) -> None:
        mock_provider = MagicMock()
        mock_provider.provider_name = "local"

        mock_client = MagicMock()
        mock_client.get_collection.return_value = MagicMock(
            config=MagicMock(
                params=MagicMock(
                    vectors={"text_dense": MagicMock()},  # Named vectors
                    sparse_vectors=None,  # No sparse vectors
                )
            )
        )
        mock_client.query_points.return_value = MagicMock(
            points=[
                MagicMock(
                    id="result-1",
                    score=0.9,
                    payload={"text": "Result text", "episode": 1},
                ),
            ]
        )

        service = SearchService(
            embeddings_provider=mock_provider,
            qdrant_client=mock_client,
        )

        with patch("voogle.services.search.emb.text2embedding") as mock_embed:
            mock_embed.return_value = np.array([[0.1] * 384])

            query = SearchQuery(query_text="test query", mode=SearchMode.HYBRID)
            response = service.search(query)

        # Should still return results (falls back to dense)
        assert len(response.results) > 0

    @pytest.mark.description("Sparse search generates sparse vectors")
    def test_sparse_search_generates_vectors(self) -> None:
        mock_provider = MagicMock()
        mock_provider.provider_name = "local"

        mock_client = MagicMock()
        mock_client.get_collection.return_value = MagicMock(
            config=MagicMock(
                params=MagicMock(
                    vectors={"text_dense": MagicMock()},
                    sparse_vectors={VectorName.TEXT_SPARSE.value: MagicMock()},
                )
            )
        )
        mock_client.query_points.return_value = MagicMock(
            points=[
                MagicMock(
                    id="result-1",
                    score=0.85,
                    payload={"text": "Sparse result", "episode": 2},
                ),
            ]
        )

        mock_sparse = MagicMock()
        mock_sparse.encode.return_value = SparseVector(
            indices=[100, 200, 300],
            values=[0.5, 0.8, 0.3],
        )

        service = SearchService(
            embeddings_provider=mock_provider,
            qdrant_client=mock_client,
            sparse_encoder=mock_sparse,
        )

        with patch("voogle.services.search.emb.text2embedding") as mock_embed:
            mock_embed.return_value = np.array([[0.1] * 384])

            query = SearchQuery(query_text="test query", mode=SearchMode.SPARSE)
            response = service.search(query)

        # Sparse encoder should be called
        mock_sparse.encode.assert_called_once_with("test query")
        assert len(response.results) == 1
