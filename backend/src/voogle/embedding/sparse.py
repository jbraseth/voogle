# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Sparse embedding encoder for hybrid search.

Provides sparse vector generation using either:
- SPLADE (Sparse Lexical and Expansion Model) for learned sparse representations
- BM25 for traditional term-frequency based sparse vectors

Sparse embeddings complement dense embeddings in hybrid search by providing
keyword-based matching that captures exact term matches dense models might miss.

Usage:
    from voogle.embedding.sparse import SparseEncoder

    encoder = SparseEncoder()  # Uses default BM25
    sparse_vector = encoder.encode("search query")

    # For SPLADE (requires transformers/torch):
    encoder = SparseEncoder(method="splade")
"""

from __future__ import annotations

import functools
import logging
import re
from abc import ABC, abstractmethod
from collections import Counter
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SparseVector:
    """Sparse vector representation for Qdrant.

    Attributes:
        indices: List of non-zero dimension indices (vocabulary token IDs).
        values: List of weights for each non-zero dimension.
    """

    indices: list[int]
    values: list[float]

    def to_dict(self) -> dict:
        """Convert to Qdrant-compatible sparse vector format."""
        return {"indices": self.indices, "values": self.values}

    def __len__(self) -> int:
        """Return number of non-zero dimensions."""
        return len(self.indices)


class SparseEncoderBase(ABC):
    """Abstract base class for sparse encoders."""

    @abstractmethod
    def encode(self, text: str) -> SparseVector:
        """Encode text into a sparse vector.

        Args:
            text: Input text to encode.

        Returns:
            SparseVector with non-zero dimensions and weights.
        """
        ...

    @abstractmethod
    def encode_batch(self, texts: list[str]) -> list[SparseVector]:
        """Encode multiple texts into sparse vectors.

        Args:
            texts: List of input texts.

        Returns:
            List of SparseVector objects.
        """
        ...

    @property
    @abstractmethod
    def method_name(self) -> str:
        """Return the encoding method name."""
        ...


@dataclass
class BM25Config:
    """Configuration for BM25 sparse encoder.

    Attributes:
        k1: Term saturation parameter. Higher values give more weight to
            term frequency. Default 1.5 is a common choice.
        b: Length normalization parameter. 0 = no normalization,
            1 = full normalization. Default 0.75.
        avg_doc_length: Average document length for normalization.
            If None, uses a default of 256 tokens.
        min_token_length: Minimum token length to include. Default 2.
        stopwords: Set of words to exclude from indexing.
    """

    k1: float = 1.5
    b: float = 0.75
    avg_doc_length: float = 256.0
    min_token_length: int = 2
    stopwords: set[str] = field(default_factory=lambda: _DEFAULT_STOPWORDS.copy())


# Common English stopwords - kept minimal for search quality
_DEFAULT_STOPWORDS: set[str] = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "has", "he", "in", "is", "it", "its", "of", "on", "or", "that",
    "the", "to", "was", "were", "will", "with",
}


class BM25Encoder(SparseEncoderBase):
    """BM25-based sparse encoder.

    Uses term frequency with BM25 weighting for sparse vector generation.
    This is a simple, efficient approach that works well for keyword matching.

    The vocabulary is built from a hash of terms to create stable indices
    without requiring a pre-trained vocabulary.
    """

    # Vocabulary size for hash-based token IDs
    VOCAB_SIZE = 30522  # Match BERT vocabulary size for compatibility

    def __init__(self, config: Optional[BM25Config] = None) -> None:
        """Initialize BM25 encoder.

        Args:
            config: BM25 configuration. Uses defaults if None.
        """
        self.config = config or BM25Config()
        logger.info(f"Initialized BM25 encoder with k1={self.config.k1}, b={self.config.b}")

    @property
    def method_name(self) -> str:
        return "bm25"

    def _tokenize(self, text: str) -> list[str]:
        """Tokenize text into terms.

        Simple whitespace + punctuation tokenization with lowercasing.

        Args:
            text: Input text.

        Returns:
            List of lowercase tokens.
        """
        # Lowercase and split on non-alphanumeric
        tokens = re.findall(r"\b[a-z0-9]+\b", text.lower())
        # Filter by length and stopwords
        return [
            t for t in tokens
            if len(t) >= self.config.min_token_length
            and t not in self.config.stopwords
        ]

    def _term_to_index(self, term: str) -> int:
        """Convert a term to a vocabulary index using hashing.

        Args:
            term: Input term.

        Returns:
            Index in range [0, VOCAB_SIZE).
        """
        # Use a simple hash to get a stable index
        return hash(term) % self.VOCAB_SIZE

    def _compute_bm25_weight(
        self,
        term_freq: int,
        doc_length: int,
    ) -> float:
        """Compute BM25 weight for a term.

        Args:
            term_freq: Frequency of term in document.
            doc_length: Total tokens in document.

        Returns:
            BM25 weight (without IDF since that's applied by Qdrant).
        """
        k1 = self.config.k1
        b = self.config.b
        avg_dl = self.config.avg_doc_length

        # BM25 term frequency component
        # TF saturation: prevents very frequent terms from dominating
        numerator = term_freq * (k1 + 1)
        denominator = term_freq + k1 * (1 - b + b * (doc_length / avg_dl))

        return numerator / denominator

    def encode(self, text: str) -> SparseVector:
        """Encode text into a BM25-weighted sparse vector.

        Args:
            text: Input text to encode.

        Returns:
            SparseVector with term indices and BM25 weights.
        """
        tokens = self._tokenize(text)
        if not tokens:
            return SparseVector(indices=[], values=[])

        doc_length = len(tokens)
        term_freqs = Counter(tokens)

        indices = []
        values = []

        for term, freq in term_freqs.items():
            idx = self._term_to_index(term)
            weight = self._compute_bm25_weight(freq, doc_length)
            indices.append(idx)
            values.append(weight)

        return SparseVector(indices=indices, values=values)

    def encode_batch(self, texts: list[str]) -> list[SparseVector]:
        """Encode multiple texts into BM25-weighted sparse vectors.

        Args:
            texts: List of input texts.

        Returns:
            List of SparseVector objects.
        """
        return [self.encode(text) for text in texts]


class SPLADEEncoder(SparseEncoderBase):
    """SPLADE-based sparse encoder using learned sparse representations.

    SPLADE (Sparse Lexical and Expansion Model) uses a pre-trained language
    model to generate sparse representations that include term expansion.
    This captures semantic relationships while maintaining interpretability.

    Requires: transformers, torch (optional dependencies).
    """

    DEFAULT_MODEL = "naver/splade-cocondenser-ensembledistil"

    def __init__(self, model_name: Optional[str] = None) -> None:
        """Initialize SPLADE encoder.

        Args:
            model_name: HuggingFace model name. Uses default if None.

        Raises:
            ImportError: If transformers/torch not installed.
        """
        try:
            import torch
            from transformers import AutoModelForMaskedLM, AutoTokenizer
        except ImportError as e:
            raise ImportError(
                "SPLADE encoder requires 'transformers' and 'torch'. "
                "Install with: pip install transformers torch"
            ) from e

        self._model_name = model_name or self.DEFAULT_MODEL
        logger.info(f"Loading SPLADE model: {self._model_name}")

        self._tokenizer = AutoTokenizer.from_pretrained(self._model_name)
        self._model = AutoModelForMaskedLM.from_pretrained(self._model_name)
        self._model.eval()

        # Move to GPU if available
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        self._model.to(self._device)

        logger.info(f"SPLADE encoder initialized on {self._device}")

    @property
    def method_name(self) -> str:
        return "splade"

    def encode(self, text: str) -> SparseVector:
        """Encode text using SPLADE.

        Args:
            text: Input text to encode.

        Returns:
            SparseVector with vocabulary indices and SPLADE weights.
        """
        import torch

        # Tokenize
        inputs = self._tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True,
        )
        inputs = {k: v.to(self._device) for k, v in inputs.items()}

        # Get logits
        with torch.no_grad():
            outputs = self._model(**inputs)
            logits = outputs.logits

        # SPLADE aggregation: max over sequence, then ReLU + log1p
        # This creates sparse representations with term expansion
        splade_rep = torch.max(
            torch.log1p(torch.relu(logits)) * inputs["attention_mask"].unsqueeze(-1),
            dim=1,
        ).values

        # Extract non-zero indices and values
        sparse_rep = splade_rep.squeeze(0)
        nonzero_mask = sparse_rep > 0
        indices = torch.where(nonzero_mask)[0].cpu().tolist()
        values = sparse_rep[nonzero_mask].cpu().tolist()

        return SparseVector(indices=indices, values=values)

    def encode_batch(self, texts: list[str]) -> list[SparseVector]:
        """Encode multiple texts using SPLADE.

        Args:
            texts: List of input texts.

        Returns:
            List of SparseVector objects.
        """
        # For simplicity, encode one at a time
        # Could be optimized with batched inference
        return [self.encode(text) for text in texts]


class SparseEncoder:
    """Factory class for sparse encoding.

    Creates the appropriate sparse encoder based on the specified method.
    Provides a unified interface for both BM25 and SPLADE encoding.

    Example:
        encoder = SparseEncoder()  # Default BM25
        vector = encoder.encode("search query")

        encoder = SparseEncoder(method="splade")  # SPLADE
        vector = encoder.encode("search query")
    """

    def __init__(
        self,
        method: str = "bm25",
        bm25_config: Optional[BM25Config] = None,
        splade_model: Optional[str] = None,
    ) -> None:
        """Initialize sparse encoder.

        Args:
            method: Encoding method - "bm25" or "splade".
            bm25_config: Configuration for BM25 encoder (if method="bm25").
            splade_model: Model name for SPLADE encoder (if method="splade").

        Raises:
            ValueError: If method is not supported.
        """
        self._method = method.lower()

        if self._method == "bm25":
            self._encoder: SparseEncoderBase = BM25Encoder(bm25_config)
        elif self._method == "splade":
            self._encoder = SPLADEEncoder(splade_model)
        else:
            raise ValueError(
                f"Unknown sparse encoding method: {method}. "
                "Supported methods: 'bm25', 'splade'"
            )

        logger.info(f"Created SparseEncoder with method={self._method}")

    def __str__(self) -> str:
        """Return string representation."""
        return f"SparseEncoder(method={self._method})"

    def __repr__(self) -> str:
        """Return detailed string representation."""
        return f"SparseEncoder(method={self._method!r}, encoder={self._encoder!r})"

    @property
    def method(self) -> str:
        """Return the encoding method name."""
        return self._method

    def encode(self, text: str) -> SparseVector:
        """Encode text into a sparse vector.

        Args:
            text: Input text to encode.

        Returns:
            SparseVector with non-zero dimensions and weights.
        """
        return self._encoder.encode(text)

    def encode_batch(self, texts: list[str]) -> list[SparseVector]:
        """Encode multiple texts into sparse vectors.

        Args:
            texts: List of input texts.

        Returns:
            List of SparseVector objects.
        """
        return self._encoder.encode_batch(texts)


@functools.cache
def get_sparse_encoder(method: str = "bm25") -> SparseEncoder:
    """Get a cached sparse encoder instance.

    This function caches encoders by method to avoid repeated initialization.

    Args:
        method: Encoding method - "bm25" or "splade".

    Returns:
        Cached SparseEncoder instance.
    """
    return SparseEncoder(method=method)
