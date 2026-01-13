# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Embedding provider abstraction layer.

Defines the EmbeddingProvider ABC for swappable embedding providers with support
for text, image, audio, and video modalities. Providers implement specific methods
for each modality they support.

Usage:
    from voogle.embedding.provider import EmbeddingProvider, EmbeddingResult

    class MyProvider(EmbeddingProvider):
        def embed_text(self, text: str) -> EmbeddingResult:
            vector = self._compute_embedding(text)
            return EmbeddingResult(
                vector=vector,
                dimensions=len(vector),
                model_id=self.metadata.model_id,
            )
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Union


class ContentModality(Enum):
    """Content modalities supported by embedding providers.

    Providers declare which modalities they support via their metadata.
    """

    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"


@dataclass(frozen=True)
class EmbeddingResult:
    """Result of an embedding operation.

    Attributes:
        vector: The embedding vector as a list of floats.
        dimensions: The dimensionality of the embedding vector.
        model_id: Identifier of the model that produced this embedding.
        tokens_used: Optional count of tokens consumed (for cost tracking).
    """

    vector: list[float]
    dimensions: int
    model_id: str
    tokens_used: Optional[int] = None

    def __post_init__(self) -> None:
        """Validate embedding result after initialization."""
        if len(self.vector) != self.dimensions:
            raise ValueError(
                f"Vector length ({len(self.vector)}) does not match "
                f"declared dimensions ({self.dimensions})"
            )
        if self.dimensions <= 0:
            raise ValueError(f"Dimensions must be positive, got {self.dimensions}")


@dataclass(frozen=True)
class CostInfo:
    """Cost information for an embedding provider.

    Attributes:
        cost_per_token: Cost per token in USD (for text embeddings).
        cost_per_image: Cost per image in USD (for image embeddings).
        cost_per_second_audio: Cost per second in USD (for audio embeddings).
        cost_per_second_video: Cost per second in USD (for video embeddings).
    """

    cost_per_token: Optional[float] = None
    cost_per_image: Optional[float] = None
    cost_per_second_audio: Optional[float] = None
    cost_per_second_video: Optional[float] = None


@dataclass(frozen=True)
class ProviderMetadata:
    """Metadata describing an embedding provider's capabilities.

    Attributes:
        provider_id: Unique identifier for this provider (e.g., 'openai', 'local').
        model_id: The specific model being used (e.g., 'text-embedding-3-small').
        supported_modalities: Set of content modalities this provider can embed.
        dimensions: The dimensionality of embeddings produced by this provider.
        max_batch_size: Maximum number of items that can be embedded in one call.
        cost_info: Optional cost information for billing/budgeting.
        description: Human-readable description of the provider.
    """

    provider_id: str
    model_id: str
    supported_modalities: frozenset[ContentModality]
    dimensions: int
    max_batch_size: int = 1
    cost_info: Optional[CostInfo] = None
    description: str = ""

    def __post_init__(self) -> None:
        """Validate metadata after initialization."""
        if not self.provider_id:
            raise ValueError("provider_id cannot be empty")
        if not self.model_id:
            raise ValueError("model_id cannot be empty")
        if not self.supported_modalities:
            raise ValueError("supported_modalities cannot be empty")
        if self.dimensions <= 0:
            raise ValueError(f"dimensions must be positive, got {self.dimensions}")
        if self.max_batch_size <= 0:
            raise ValueError(
                f"max_batch_size must be positive, got {self.max_batch_size}"
            )

    def supports(self, modality: ContentModality) -> bool:
        """Check if this provider supports a given modality."""
        return modality in self.supported_modalities


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers.

    Embedding providers generate vector representations (embeddings) from various
    content types. Each provider declares its supported modalities via metadata
    and implements the corresponding embed_* methods.

    Subclasses must:
    1. Implement the `metadata` property returning ProviderMetadata
    2. Implement embed_* methods for each modality they support
    3. Raise NotImplementedError for unsupported modalities

    Example:
        class OpenAITextProvider(EmbeddingProvider):
            @property
            def metadata(self) -> ProviderMetadata:
                return ProviderMetadata(
                    provider_id="openai",
                    model_id="text-embedding-3-small",
                    supported_modalities=frozenset([ContentModality.TEXT]),
                    dimensions=1536,
                    max_batch_size=100,
                )

            def embed_text(self, text: str) -> EmbeddingResult:
                # Implementation here
                ...
    """

    @property
    @abstractmethod
    def metadata(self) -> ProviderMetadata:
        """Return metadata describing this provider's capabilities."""
        ...

    @abstractmethod
    def embed_text(self, text: str) -> EmbeddingResult:
        """Generate an embedding for the given text.

        Args:
            text: The text content to embed.

        Returns:
            EmbeddingResult containing the embedding vector.

        Raises:
            NotImplementedError: If this provider does not support text embeddings.
            ValueError: If the input text is invalid.
        """
        ...

    @abstractmethod
    def embed_image(self, image: Union[bytes, Path]) -> EmbeddingResult:
        """Generate an embedding for the given image.

        Args:
            image: Either raw image bytes or a path to an image file.

        Returns:
            EmbeddingResult containing the embedding vector.

        Raises:
            NotImplementedError: If this provider does not support image embeddings.
            ValueError: If the image is invalid or cannot be processed.
            FileNotFoundError: If image is a path that doesn't exist.
        """
        ...

    @abstractmethod
    def embed_audio(self, audio: Union[bytes, Path]) -> EmbeddingResult:
        """Generate an embedding for the given audio.

        Args:
            audio: Either raw audio bytes or a path to an audio file.

        Returns:
            EmbeddingResult containing the embedding vector.

        Raises:
            NotImplementedError: If this provider does not support audio embeddings.
            ValueError: If the audio is invalid or cannot be processed.
            FileNotFoundError: If audio is a path that doesn't exist.
        """
        ...

    @abstractmethod
    def embed_video(self, video: Union[bytes, Path]) -> EmbeddingResult:
        """Generate an embedding for the given video.

        Args:
            video: Either raw video bytes or a path to a video file.

        Returns:
            EmbeddingResult containing the embedding vector.

        Raises:
            NotImplementedError: If this provider does not support video embeddings.
            ValueError: If the video is invalid or cannot be processed.
            FileNotFoundError: If video is a path that doesn't exist.
        """
        ...

    def embed_text_batch(self, texts: list[str]) -> list[EmbeddingResult]:
        """Generate embeddings for multiple texts.

        Default implementation calls embed_text for each item. Providers can
        override this for more efficient batch processing.

        Args:
            texts: List of text content to embed.

        Returns:
            List of EmbeddingResult objects in the same order as inputs.

        Raises:
            NotImplementedError: If this provider does not support text embeddings.
            ValueError: If batch size exceeds max_batch_size or inputs are invalid.
        """
        if len(texts) > self.metadata.max_batch_size:
            raise ValueError(
                f"Batch size {len(texts)} exceeds maximum {self.metadata.max_batch_size}"
            )
        return [self.embed_text(text) for text in texts]

    def supports_modality(self, modality: ContentModality) -> bool:
        """Check if this provider supports a given content modality.

        Args:
            modality: The content modality to check.

        Returns:
            True if the provider supports this modality.
        """
        return self.metadata.supports(modality)
