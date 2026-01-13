# Copyright (c) 2023 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Embedding module - re-exports from legacy module for backward compatibility.

This module was converted from a single file to a package to support the new
multimodal EmbeddingProvider abstraction. All existing imports continue to work.

For the new multimodal provider interface, use:
    from voogle.embedding.provider import EmbeddingProvider, EmbeddingResult
"""

# Re-export everything from the legacy module for backward compatibility
from voogle.embedding.legacy import (
    DEFAULT_EMBEDDINGS_MODEL,
    DEFAULT_FRAGMENT_WORDS,
    EMBEDDINGS_SIZE,
    Embeddings,
    EmbeddingsProvider,
    Fragment,
    LocalEmbeddingsProvider,
    OpenAIEmbeddingsProvider,
    calculate_fragments,
    episode_embeddings,
    get_embeddings_provider,
    get_embeddings_provider_by_name,
    load_embeddings_model,
    text2embedding,
)

# New multimodal provider interface
from voogle.embedding.provider import (
    ContentModality,
    CostInfo,
    EmbeddingProvider,
    EmbeddingResult,
    ProviderMetadata,
)

# SentenceTransformers provider implementation
from voogle.embedding.sentence_transformers import SentenceTransformersProvider

# LanguageBind multimodal provider implementation
from voogle.embedding.languagebind import LanguageBindProvider

# AWS Nova Bedrock provider implementation
from voogle.embedding.aws_nova import AWSNovaProvider, is_aws_nova_enabled

# Sparse encoder for hybrid search
from voogle.embedding.sparse import (
    BM25Config,
    BM25Encoder,
    SparseEncoder,
    SparseVector,
    get_sparse_encoder,
)

__all__ = [
    # Legacy exports (backward compatibility)
    "DEFAULT_EMBEDDINGS_MODEL",
    "DEFAULT_FRAGMENT_WORDS",
    "EMBEDDINGS_SIZE",
    "Embeddings",
    "EmbeddingsProvider",
    "Fragment",
    "LocalEmbeddingsProvider",
    "OpenAIEmbeddingsProvider",
    "calculate_fragments",
    "episode_embeddings",
    "get_embeddings_provider",
    "get_embeddings_provider_by_name",
    "load_embeddings_model",
    "text2embedding",
    # New multimodal provider interface
    "ContentModality",
    "CostInfo",
    "EmbeddingProvider",
    "EmbeddingResult",
    "ProviderMetadata",
    # Provider implementations
    "SentenceTransformersProvider",
    "LanguageBindProvider",
    "AWSNovaProvider",
    "is_aws_nova_enabled",
    # Sparse encoder for hybrid search
    "BM25Config",
    "BM25Encoder",
    "SparseEncoder",
    "SparseVector",
    "get_sparse_encoder",
]
