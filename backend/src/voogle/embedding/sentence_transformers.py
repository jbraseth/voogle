# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""SentenceTransformers embedding provider implementation.

Implements the EmbeddingProvider interface using sentence-transformers library
for local text embedding generation. Supports configurable model selection,
GPU acceleration, and batch processing.

Usage:
    from voogle.embedding.sentence_transformers import SentenceTransformersProvider

    # Default model (all-MiniLM-L6-v2)
    provider = SentenceTransformersProvider()

    # Custom model with GPU
    provider = SentenceTransformersProvider(
        model_id="BAAI/bge-small-en-v1.5",
        device="cuda",
    )

    # Single embedding
    result = provider.embed_text("Hello world")
    print(result.vector)

    # Batch embedding
    results = provider.embed_text_batch(["Hello", "World"])
"""

from __future__ import annotations

import functools
import logging
from pathlib import Path
from typing import TYPE_CHECKING, overload

from voogle.embedding.provider import (
    ContentModality,
    EmbeddingProvider,
    EmbeddingResult,
    ProviderMetadata,
)

if TYPE_CHECKING:
    import sentence_transformers

logger = logging.getLogger(__name__)

# Default model - matches existing codebase default
DEFAULT_MODEL_ID = "all-MiniLM-L6-v2"

# Model configurations with known dimensions
MODEL_DIMENSIONS: dict[str, int] = {
    "all-MiniLM-L6-v2": 384,
    "all-MiniLM-L12-v2": 384,
    "all-mpnet-base-v2": 768,
    "BAAI/bge-small-en-v1.5": 384,
    "BAAI/bge-base-en-v1.5": 768,
    "BAAI/bge-large-en-v1.5": 1024,
}

# Default batch size for sentence-transformers (memory efficient default)
DEFAULT_BATCH_SIZE = 32


@functools.cache
def _load_model(
    model_id: str, device: str | None = None
) -> sentence_transformers.SentenceTransformer:
    """Load and cache a SentenceTransformer model.

    Args:
        model_id: HuggingFace model identifier or local path.
        device: Device to load model on ('cpu', 'cuda', 'cuda:0', etc.).
                If None, sentence-transformers auto-selects.

    Returns:
        Loaded SentenceTransformer model instance.
    """
    import sentence_transformers as st

    logger.info(f"Loading SentenceTransformer model: {model_id} (device={device})")
    return st.SentenceTransformer(model_id, device=device)


class SentenceTransformersProvider(EmbeddingProvider):
    """Embedding provider using sentence-transformers library.

    Provides local text embedding generation using pre-trained transformer models.
    Supports GPU acceleration and efficient batch processing.

    Attributes:
        model_id: The HuggingFace model identifier being used.
        device: The compute device (cpu, cuda, etc.).
    """

    def __init__(
        self,
        model_id: str = DEFAULT_MODEL_ID,
        device: str | None = None,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        """Initialize the SentenceTransformers provider.

        Args:
            model_id: HuggingFace model identifier (e.g., 'all-MiniLM-L6-v2',
                     'BAAI/bge-small-en-v1.5'). Defaults to all-MiniLM-L6-v2.
            device: Compute device to use. Options:
                   - None: Auto-select (GPU if available, else CPU)
                   - 'cpu': Force CPU
                   - 'cuda': Use default CUDA device
                   - 'cuda:0', 'cuda:1': Use specific CUDA device
            batch_size: Maximum batch size for batch operations.
        """
        self._model_id = model_id
        self._device = device
        self._batch_size = batch_size
        self._model: sentence_transformers.SentenceTransformer | None = None
        self._dimensions: int | None = None

    @property
    def _loaded_model(self) -> sentence_transformers.SentenceTransformer:
        """Lazy-load the model on first use."""
        if self._model is None:
            self._model = _load_model(self._model_id, self._device)
        return self._model

    def _get_dimensions(self) -> int:
        """Get the embedding dimensions, either from cache or model."""
        if self._dimensions is not None:
            return self._dimensions

        # Check known models first
        if self._model_id in MODEL_DIMENSIONS:
            self._dimensions = MODEL_DIMENSIONS[self._model_id]
        else:
            # Query the model
            dim = self._loaded_model.get_sentence_embedding_dimension()
            if dim is None:
                raise ValueError(
                    f"Model {self._model_id} does not report embedding dimensions"
                )
            self._dimensions = dim

        return self._dimensions

    @property
    def metadata(self) -> ProviderMetadata:
        """Return metadata describing this provider's capabilities."""
        return ProviderMetadata(
            provider_id="sentence-transformers",
            model_id=self._model_id,
            supported_modalities=frozenset([ContentModality.TEXT]),
            dimensions=self._get_dimensions(),
            max_batch_size=self._batch_size,
            description=f"Local text embeddings using {self._model_id}",
        )

    @overload
    def embed_text(self, text: str) -> EmbeddingResult: ...

    @overload
    def embed_text(self, text: list[str]) -> list[EmbeddingResult]: ...

    def embed_text(
        self, text: str | list[str]
    ) -> EmbeddingResult | list[EmbeddingResult]:
        """Generate embedding(s) for the given text input.

        This method accepts both single strings and lists of strings for
        flexibility. When called with a string, returns a single EmbeddingResult.
        When called with a list, returns a list of EmbeddingResults.

        Args:
            text: Either a single text string or a list of text strings.

        Returns:
            EmbeddingResult for single string input, or list of EmbeddingResults
            for list input.

        Raises:
            ValueError: If text is empty or list is empty.
        """
        # Handle list input
        if isinstance(text, list):
            return self.embed_text_batch(text)

        # Handle single string
        if not text:
            raise ValueError("text cannot be empty")

        # Generate embedding (encode returns ndarray even for single input)
        embeddings = self._loaded_model.encode(
            [text],
            batch_size=1,
            show_progress_bar=False,
            convert_to_numpy=True,
        )

        dimensions = self._get_dimensions()
        return EmbeddingResult(
            vector=embeddings[0].tolist(),
            dimensions=dimensions,
            model_id=self._model_id,
        )

    def embed_text_batch(self, texts: list[str]) -> list[EmbeddingResult]:
        """Generate embeddings for multiple texts efficiently.

        Overrides the base implementation to use sentence-transformers'
        native batching for better performance.

        Args:
            texts: List of text content to embed.

        Returns:
            List of EmbeddingResult objects in the same order as inputs.

        Raises:
            ValueError: If batch size exceeds max_batch_size or texts is empty.
        """
        if len(texts) > self.metadata.max_batch_size:
            raise ValueError(
                f"Batch size {len(texts)} exceeds maximum {self.metadata.max_batch_size}"
            )

        if not texts:
            return []

        # Generate embeddings using native batching
        embeddings = self._loaded_model.encode(
            texts,
            batch_size=self._batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
        )

        # Build results
        dimensions = self._get_dimensions()
        results = []
        for embedding in embeddings:
            results.append(
                EmbeddingResult(
                    vector=embedding.tolist(),
                    dimensions=dimensions,
                    model_id=self._model_id,
                )
            )

        return results

    def embed_image(self, image: bytes | Path) -> EmbeddingResult:
        """Not supported - SentenceTransformers is text-only.

        Raises:
            NotImplementedError: Always, as this provider only supports text.
        """
        raise NotImplementedError(
            "SentenceTransformersProvider does not support image embeddings. "
            "Use a multimodal provider like CLIP for image embeddings."
        )

    def embed_audio(self, audio: bytes | Path) -> EmbeddingResult:
        """Not supported - SentenceTransformers is text-only.

        Raises:
            NotImplementedError: Always, as this provider only supports text.
        """
        raise NotImplementedError(
            "SentenceTransformersProvider does not support audio embeddings. "
            "Use a specialized audio embedding provider."
        )

    def embed_video(self, video: bytes | Path) -> EmbeddingResult:
        """Not supported - SentenceTransformers is text-only.

        Raises:
            NotImplementedError: Always, as this provider only supports text.
        """
        raise NotImplementedError(
            "SentenceTransformersProvider does not support video embeddings. "
            "Use a specialized video embedding provider."
        )

    @property
    def device(self) -> str:
        """Return the device the model is loaded on."""
        return str(self._loaded_model.device)

    def __repr__(self) -> str:
        """Return string representation of the provider."""
        return (
            f"SentenceTransformersProvider("
            f"model_id={self._model_id!r}, "
            f"device={self._device!r}, "
            f"batch_size={self._batch_size})"
        )
