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
    transcription: tr.Transcription, max_fragment_words: int
) -> list[Fragment]:
    """Group all the words from the given transcription in fragments
    (the minimum unit used to create embeddings) with the configured
    max words.

    """
    fragments: list[Fragment] = []
    fragment_start_idx = None
    fragment_start_time = None
    fragment_text = ""
    for i, sentence in enumerate(transcription):
        sentence_start_time, sentence_end_time, text = sentence
        if fragment_start_time is None:
            fragment_start_time = sentence_start_time
        if fragment_start_idx is None:
            fragment_start_idx = i
        fragment_text += text
        if len(fragment_text.split(" ")) >= max_fragment_words:
            fragments.append(
                Fragment(
                    start_idx=fragment_start_idx,
                    end_idx=i,
                    start_secs=fragment_start_time,
                    end_secs=sentence_end_time,
                    text=fragment_text,
                )
            )
            # append previous fragment and start a new one
            fragment_text = ""
            fragment_start_idx, fragment_start_time = None, None
        elif i == len(transcription) - 1:
            fragments.append(
                Fragment(
                    start_idx=fragment_start_idx,
                    end_idx=i,
                    start_secs=fragment_start_time,
                    end_secs=sentence_end_time,
                    text=fragment_text,
                )
            )
    return fragments


def _transcription_embeddings(
    transcription: tr.Transcription,
    provider: EmbeddingsProvider,
    max_fragment_words: int,
) -> tuple[Embeddings, list[Fragment]]:
    fragments = calculate_fragments(transcription, max_fragment_words)
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
    max_fragment_words: int,
) -> tuple[Embeddings, list[Fragment]]:
    """Return a list of embeddings for the transcription of the given
    episode.

    """
    logger.info(f"obtaining embeddings for episode {episode.pk}: {episode.title}")
    trfile = await storage.transcription_file(episode)
    if not trfile.exists():
        raise ValueError(f"cannot find transcription for {episode.pk}")
    return _transcription_embeddings(
        tr.read_transcription(trfile), provider, max_fragment_words
    )
