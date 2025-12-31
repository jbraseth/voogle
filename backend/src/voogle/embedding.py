# Copyright (c) 2023 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Functions to create vectors (embeddings) representing fragments of
transcriptions (fragment length is configurable).

See https://www.sbert.net/examples/applications/semantic-search/README.html

"""
import functools
import logging
import typing
from typing import Protocol

import numpy as np
import openai
import sentence_transformers
import torch
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from voogle import models, storage
from voogle import transcription as tr
from voogle.chunking import DEFAULT_CONFIG, ChunkingConfig

logger = logging.getLogger(__name__)

Embeddings = typing.Union[list[torch.Tensor], np.ndarray, torch.Tensor]


class EmbeddingsProvider(Protocol):
    """Protocol defining the interface for embedding providers.

    Any class implementing these methods can be used as an embeddings provider.
    This follows the composition over inheritance principle.
    """

    def get_embedding_dimension(self) -> int:
        """Return the dimensionality of embeddings produced by this provider."""
        ...

    def encode_texts(self, texts: list[str]) -> Embeddings:
        """Encode a list of texts into embeddings."""
        ...

    def encode_single(self, text: str) -> Embeddings:
        """Encode a single text into an embedding (used for queries)."""
        ...


class LocalEmbeddingsProvider:
    """Wrapper around sentence-transformers for local embeddings generation."""

    def __init__(self, model: sentence_transformers.SentenceTransformer) -> None:
        self.model = model

    def get_embedding_dimension(self) -> int:
        dim = self.model.get_sentence_embedding_dimension()
        if dim is None:
            raise ValueError("Model does not have a sentence embedding dimension")
        return dim

    def encode_texts(self, texts: list[str]) -> Embeddings:
        return self.model.encode(texts)

    def encode_single(self, text: str) -> Embeddings:
        return self.model.encode([text])


class OpenAIEmbeddingsProvider:
    """Provider using OpenAI's embeddings API."""

    # Hardcoded defaults - these rarely need changing
    MAX_RETRIES = 3
    TIMEOUT_SECONDS = 60
    MAX_BATCH_SIZE = 100

    def __init__(self, api_key: str, model: str = "text-embedding-3-small") -> None:
        self.client = openai.OpenAI(
            api_key=api_key, timeout=self.TIMEOUT_SECONDS, max_retries=0
        )
        self.model = model
        self._dimension = 1536  # text-embedding-3-small dimension

        logger.info(f"initialized OpenAI embeddings provider with model={model}")

    def get_embedding_dimension(self) -> int:
        return self._dimension

    def _call_api(self, texts: list[str]) -> list[list[float]]:
        """Call OpenAI API with retry logic. Fails loud on non-retryable errors."""
        logger.info(f"calling OpenAI embeddings API for {len(texts)} texts")

        retryer = retry(
            stop=stop_after_attempt(self.MAX_RETRIES),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=retry_if_exception_type((openai.APIError, openai.APITimeoutError)),
            reraise=True,
        )

        @retryer
        def _do_call() -> openai.types.CreateEmbeddingResponse:
            return self.client.embeddings.create(
                input=texts,
                model=self.model,
            )

        try:
            response = _do_call()

            # Log cost tracking info
            total_tokens = response.usage.total_tokens
            estimated_cost = (total_tokens / 1_000_000) * 0.02  # $0.02 per 1M tokens
            logger.info(
                "openai_embeddings_call",
                extra={
                    "texts_count": len(texts),
                    "total_tokens": total_tokens,
                    "estimated_cost_usd": estimated_cost,
                    "model": self.model,
                },
            )

            return [item.embedding for item in response.data]

        except openai.AuthenticationError as e:
            # Non-retryable - fail immediately
            logger.error(f"OpenAI authentication failed: {e}", exc_info=True)
            raise ValueError(f"Invalid OPENAI_API_KEY: {e}") from e
        except openai.RateLimitError as e:
            # Check if it's quota exhaustion (not retryable) vs temporary rate limit
            if "insufficient_quota" in str(e):
                logger.error(f"OpenAI quota exhausted - not retrying: {e}")
                raise ValueError(f"OpenAI quota exhausted: {e}") from e
            # Temporary rate limit - retryable
            logger.warning(f"OpenAI rate limit hit, will retry: {e}")
            raise

    def encode_texts(self, texts: list[str]) -> Embeddings:
        """Encode texts in batches to respect API limits."""
        if len(texts) == 0:
            return np.array([])

        # Batch processing for large inputs
        all_embeddings = []
        for i in range(0, len(texts), self.MAX_BATCH_SIZE):
            batch = texts[i : i + self.MAX_BATCH_SIZE]
            batch_embeddings = self._call_api(batch)
            all_embeddings.extend(batch_embeddings)

        return np.array(all_embeddings)

    def encode_single(self, text: str) -> Embeddings:
        """Encode single text (used for queries)."""
        embeddings = self._call_api([text])
        return np.array(embeddings)


DEFAULT_FRAGMENT_WORDS = 40
# see https://www.sbert.net/docs/pretrained_models.html
# TODO: I could try a multilingual model that will generate aligned
# vector spaces, i.e. similar inputs in different languages are mapped
# close in vector space.
# see https://www.sbert.net/docs/pretrained_models.html#multi-lingual-models
DEFAULT_EMBEDDINGS_MODEL = "BAAI/bge-small-en-v1.5"
EMBEDDINGS_SIZE = 384


class Fragment(typing.NamedTuple):
    """A fragment represents the minimum amount of data to be stored
    in the vector database.
    """

    start_idx: int
    end_idx: int
    start_secs: float
    end_secs: float
    text: str


@functools.cache
def load_embeddings_model(name: str) -> sentence_transformers.SentenceTransformer:
    """Load transformer model from its name.

    This function uses cache so that the first time a model is loaded
    it is cached, and later function executions will just use the
    cached instance.
    """
    logger.info(f"loading and caching transformer model {name}")
    return sentence_transformers.SentenceTransformer(name)


@functools.cache
def get_embeddings_provider() -> EmbeddingsProvider:
    """Factory function to return configured embeddings provider.

    Auto-detects provider based on settings.openai_api_key presence:
    - If OPENAI_API_KEY is set → OpenAI provider
    - Otherwise → Local sentence-transformers provider

    Uses cache so provider is loaded once and reused.
    """
    from voogle import settings as app_settings

    if app_settings.settings.embeddings_provider == "openai":
        if not app_settings.settings.openai_api_key:
            raise ValueError(
                "OpenAI embeddings provider selected but OPENAI_API_KEY not set. "
                "Set the environment variable or remove it to use local embeddings."
            )

        logger.info("using OpenAI embeddings provider")
        return OpenAIEmbeddingsProvider(
            api_key=app_settings.settings.openai_api_key,
            model=app_settings.settings.openai_model,
        )
    else:
        logger.info(f"using local embeddings provider with model={DEFAULT_EMBEDDINGS_MODEL}")
        model = load_embeddings_model(DEFAULT_EMBEDDINGS_MODEL)
        return LocalEmbeddingsProvider(model)


def calculate_fragments(
    transcription: tr.Transcription,
    config_or_max_words: int | ChunkingConfig = DEFAULT_CONFIG,
) -> list[Fragment]:
    """Group all the words from the given transcription in fragments.

    Args:
        transcription: List of (start_time, end_time, text) tuples.
        config_or_max_words: Either a ChunkingConfig or an int for backward
            compatibility (treated as chunk_size_words with no overlap).

    Returns:
        List of Fragment objects representing chunks of text.
    """
    # Backward compatibility: accept int for max_fragment_words
    if isinstance(config_or_max_words, int):
        config = ChunkingConfig(
            chunk_size_words=config_or_max_words,
            chunk_overlap_words=0,
            min_chunk_length_words=1,
        )
    else:
        config = config_or_max_words

    fragments: list[Fragment] = []
    # Track sentences for overlap: list of (sentence_idx, start_time, end_time, text)
    current_sentences: list[tuple[int, float, float, str]] = []
    current_text = ""

    for i, sentence in enumerate(transcription):
        sentence_start_time, sentence_end_time, text = sentence
        current_sentences.append((i, sentence_start_time, sentence_end_time, text))
        current_text += text

        # Check if we've reached chunk size (match original: split on " ")
        if len(current_text.split(" ")) >= config.chunk_size_words:
            # Build fragment from current sentences
            fragment = _build_fragment_from_sentences(current_sentences)
            if len(fragment.text.split()) >= config.min_chunk_length_words:
                fragments.append(fragment)

            # Calculate overlap: keep sentences from the end that sum to >= overlap words
            if config.chunk_overlap_words > 0:
                overlap_sentences: list[tuple[int, float, float, str]] = []
                overlap_text = ""
                for sent in reversed(current_sentences):
                    if len(overlap_text.split(" ")) >= config.chunk_overlap_words:
                        break
                    overlap_sentences.insert(0, sent)
                    overlap_text = sent[3] + overlap_text
                current_sentences = overlap_sentences
                current_text = "".join(s[3] for s in current_sentences)
            else:
                current_sentences = []
                current_text = ""

    # Handle remaining sentences
    if current_sentences:
        fragment = _build_fragment_from_sentences(current_sentences)
        if len(fragment.text.split()) >= config.min_chunk_length_words:
            fragments.append(fragment)

    return fragments


def _build_fragment_from_sentences(
    sentences: list[tuple[int, float, float, str]]
) -> Fragment:
    """Build a Fragment from a list of sentence tuples (idx, start, end, text)."""
    return Fragment(
        start_idx=sentences[0][0],
        end_idx=sentences[-1][0],
        start_secs=sentences[0][1],
        end_secs=sentences[-1][2],
        text="".join(s[3] for s in sentences),
    )


def _transcription_embeddings(
    transcription: tr.Transcription,
    provider: EmbeddingsProvider,
    config_or_max_words: int | ChunkingConfig = DEFAULT_CONFIG,
) -> tuple[Embeddings, list[Fragment]]:
    fragments = calculate_fragments(transcription, config_or_max_words)
    logger.info(f"encoding {len(fragments)} fragments...")
    embeddings = provider.encode_texts([f.text for f in fragments])
    return embeddings, fragments


def text2embedding(text: str, provider: EmbeddingsProvider) -> Embeddings:
    """Return embedding from the given text."""
    logger.info(f"encoding text: {text}")
    return provider.encode_single(text)


async def episode_embeddings(
    episode: models.Episode,
    provider: EmbeddingsProvider,
    config_or_max_words: int | ChunkingConfig = DEFAULT_CONFIG,
) -> tuple[Embeddings, list[Fragment]]:
    """Return a list of embeddings for the transcription of the given episode.

    Args:
        episode: Episode to generate embeddings for.
        provider: Embeddings provider (local or OpenAI).
        config_or_max_words: ChunkingConfig or int for backward compatibility.

    Returns:
        Tuple of (embeddings, fragments).

    Raises:
        ValueError: If transcription file not found.
    """
    logger.info(f"obtaining embeddings for episode {episode.pk}: {episode.title}")
    trfile = await storage.transcription_file(episode)
    if not trfile.exists():
        raise ValueError(f"cannot find transcription for {episode.pk}")
    return _transcription_embeddings(
        tr.read_transcription(trfile), provider, config_or_max_words
    )
