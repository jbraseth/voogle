# Copyright (c) 2022-2023 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Functions to store and retrieve information from/to the vector
database.
"""

import functools
import hashlib
import logging
import pathlib
import uuid
from datetime import datetime, timezone
from functools import cache
from typing import NamedTuple, Optional, Union

import numpy as np
import qdrant_client
from qdrant_client import models
from sklearn.decomposition import PCA

from voogle import embedding, settings, storage
from voogle.models import Episode

DEFAULT_COLLECTION: str = "vectordb"

logger = logging.getLogger(__name__)


def generate_point_id(episode_pk: str, fragment_start_idx: int) -> str:
    """Generate a deterministic Qdrant point ID as a valid UUID.

    Using deterministic IDs makes upsert operations idempotent - if a job
    crashes and retries, it will overwrite the same points rather than
    creating duplicates.

    The UUID is generated from a hash of the episode ID and fragment index,
    ensuring the same inputs always produce the same UUID.

    Args:
        episode_pk: The episode's primary key.
        fragment_start_idx: The fragment's start index in the transcription.

    Returns:
        A deterministic UUID string for the Qdrant point.
    """
    # Create a deterministic hash from the episode and fragment info
    data = f"{episode_pk}-{fragment_start_idx}".encode("utf-8")
    hash_bytes = hashlib.md5(data).digest()  # noqa: S324 - not for security
    # Use UUID version 3 (MD5-based) namespace UUID format
    return str(uuid.UUID(bytes=hash_bytes, version=3))


def get_collection_name(provider_name: str) -> str:
    """Return collection name based on embeddings provider.

    Separate collections ensure embeddings from different models/providers
    don't mix (different dimensions require different vector configs).
    """
    if provider_name == "openai":
        return f"{DEFAULT_COLLECTION}-openai"
    return DEFAULT_COLLECTION  # "vectordb" for local


def get_experiment_collection_name(experiment_name: str, provider_name: str) -> str:
    """Return collection name for A/B testing experiments.

    Args:
        experiment_name: Name of the experiment (e.g., "60word", "overlap10").
        provider_name: Embeddings provider name ("local" or "openai").

    Returns:
        Collection name like "vectordb-60word" or "vectordb-openai-60word".
    """
    base = get_collection_name(provider_name)
    return f"{base}-{experiment_name}"


class QueryResponse(NamedTuple):
    score: float
    episode: int
    channel: int
    start_secs: int
    end_secs: int
    text: str


@functools.cache
def get_client(
    host: Optional[str] = None,
    port: Optional[int] = None,
    path: Optional[Union[str, pathlib.Path]] = None,
) -> qdrant_client.QdrantClient:
    """Return vector database client, that can be connected to a
    server if host and port are given, a local model persisted in disk
    if a path is given or just in memory if no argument is provided.

    """
    logger.info(f"obtaining qdrant client {host=} {port=} {path=}")
    if host and port:
        return qdrant_client.QdrantClient(host=host, port=port)
    elif path:
        return qdrant_client.QdrantClient(path=str(path))
    return qdrant_client.QdrantClient(":memory:")


@functools.cache
def get_configured_client() -> qdrant_client.QdrantClient:
    """Return the vector database client configured in app settings."""
    if settings.settings.qdrant_use_file:
        return get_client(path=storage.vectordb_path())
    return get_client(
        host=settings.settings.qdrant_host, port=settings.settings.qdrant_port
    )


def create_collection(
    client: qdrant_client.QdrantClient,
    name: str,
    vector_dimension: int,
) -> None:
    """Create a collection in the vector database with the given name.

    If the collection already exists, it is deleted first.
    """
    logger.info(f"creating qdrant collection {name} with dimension={vector_dimension}")
    if client.collection_exists(name):
        logger.info(f"collection {name} exists, deleting it first")
        client.delete_collection(name)
    client.create_collection(
        collection_name=name,
        vectors_config=models.VectorParams(
            size=vector_dimension,  # type: ignore[arg-type]
            distance=models.Distance.COSINE,
        ),
    )


@cache
def ensure_collection(
    client: qdrant_client.QdrantClient,
    collection_name: str,
    vector_dimension: int,
) -> None:
    logger.info(f"trying to find collection {collection_name}")
    collections = client.get_collections().collections
    logger.debug(f"available collections: {collections}")
    found = [c for c in collections if c.name == collection_name]
    if not found:
        logger.info("collection not found, creating it")
        create_collection(client, collection_name, vector_dimension)


def _gen_metadata(
    fragment: embedding.Fragment,
    episode: Episode,
    provider: Optional[embedding.EmbeddingsProvider] = None,
) -> dict:
    """Generate metadata payload for a fragment stored in Qdrant.

    Args:
        fragment: The text fragment being stored.
        episode: The episode this fragment belongs to.
        provider: Optional embeddings provider to include model/provider metadata.

    Returns:
        Dictionary of metadata fields for the Qdrant payload.
    """
    if episode.channel is None:
        raise ValueError(f"Episode {episode.pk} has no associated channel")

    metadata = {
        "episode": episode.pk,
        "channel": episode.channel.pk,
        "start_secs": fragment.start_secs,
        "end_secs": fragment.end_secs,
        "text": fragment.text,
    }

    if provider is not None:
        metadata["embedding_model"] = provider.model_name
        metadata["embedding_provider"] = provider.provider_name
        metadata["embedded_at"] = datetime.now(timezone.utc).isoformat()

    return metadata


async def add_episode(
    episode: Episode,
    client: qdrant_client.QdrantClient,
    embeddings: embedding.Embeddings,
    collection_name: str,
    fragments: list[embedding.Fragment],
    provider: Optional[embedding.EmbeddingsProvider] = None,
) -> None:
    """Store the given embeddings from an episode in the vector database.

    Args:
        episode: Episode to store embeddings for.
        client: Qdrant client.
        embeddings: Embedding vectors to store.
        collection_name: Target collection name.
        fragments: Text fragments corresponding to embeddings.
        provider: Optional embeddings provider for metadata (model, provider, timestamp).
    """
    if episode.embeddings:
        raise ValueError(f"Episode {episode.pk} already stored in the vector db")
    # Use upsert with deterministic IDs for idempotent retries
    client.upsert(
        collection_name=collection_name,
        points=[
            models.PointStruct(
                id=generate_point_id(str(episode.pk), fragment.start_idx),
                vector=emb.tolist(),
                payload=_gen_metadata(fragment, episode, provider),
            )
            for emb, fragment in zip(embeddings, fragments)
        ],
    )
    episode.embeddings = True
    await episode.update()
    return


def search(
    client: qdrant_client.QdrantClient,
    query_embedding: embedding.Embeddings,
    collection_name: str,
    num_results: int,
    query_filter: Optional[models.Filter] = None,
) -> list[QueryResponse]:
    """Perform a query with the given vector database and embeddings."""
    # Use query_points (search is deprecated in newer qdrant-client)
    results = client.query_points(
        collection_name=collection_name,
        query=query_embedding[0].tolist(),
        query_filter=query_filter,
        limit=num_results,
    ).points
    # Extract only the fields QueryResponse expects, ignoring metadata fields
    return [
        QueryResponse(
            score=r.score,
            episode=r.payload["episode"],  # type: ignore[index]
            channel=r.payload["channel"],  # type: ignore[index]
            start_secs=r.payload["start_secs"],  # type: ignore[index]
            end_secs=r.payload["end_secs"],  # type: ignore[index]
            text=r.payload["text"],  # type: ignore[index]
        )
        for r in results
    ]


class SearchResultWithVector(NamedTuple):
    response: QueryResponse
    vector: np.ndarray


def search_with_vectors(
    client: qdrant_client.QdrantClient,
    query_embedding: embedding.Embeddings,
    collection_name: str,
    num_results: int,
    query_filter: Optional[models.Filter] = None,
) -> list[SearchResultWithVector]:
    """Perform a query and return results with their embedding vectors.

    This is used for visualization where we need both the query results
    and their embedding vectors for 2D projection.
    """
    results = client.query_points(
        collection_name=collection_name,
        query=query_embedding[0].tolist(),
        query_filter=query_filter,
        limit=num_results,
        with_vectors=True,
    ).points

    return [
        SearchResultWithVector(
            response=QueryResponse(
                score=r.score,
                episode=r.payload["episode"],  # type: ignore[index]
                channel=r.payload["channel"],  # type: ignore[index]
                start_secs=r.payload["start_secs"],  # type: ignore[index]
                end_secs=r.payload["end_secs"],  # type: ignore[index]
                text=r.payload["text"],  # type: ignore[index]
            ),
            vector=np.array(r.vector),
        )
        for r in results
    ]


class ProjectedPoint(NamedTuple):
    x: float
    y: float
    fragment_id: str
    label: str
    preview: str
    score: float


class ProjectionResult(NamedTuple):
    points: list[ProjectedPoint]
    query_point: Optional[tuple[float, float]]


def project_embeddings_2d(
    query_embedding: embedding.Embeddings,
    result_embeddings: list[np.ndarray],
    results: list[QueryResponse],
) -> ProjectionResult:
    """Project query and result embeddings to 2D using PCA.

    Args:
        query_embedding: The query embedding vector (shape: (1, dim) or (dim,)).
        result_embeddings: List of result embedding vectors.
        results: List of QueryResponse objects with metadata.

    Returns:
        ProjectionResult with 2D coordinates for all points.

    Raises:
        ValueError: If fewer than 2 result embeddings are provided.
    """
    if len(result_embeddings) < 2:
        raise ValueError("At least 2 result embeddings required for projection")

    # Flatten query embedding if needed
    query_vec = np.array(query_embedding).flatten()

    # Stack all embeddings: query first, then results
    all_embeddings = np.vstack([query_vec.reshape(1, -1)] + [e.reshape(1, -1) for e in result_embeddings])

    # Check for degenerate case: all embeddings identical
    if np.allclose(all_embeddings, all_embeddings[0]):
        raise ValueError("All embeddings are identical, cannot compute projection")

    # Apply PCA to reduce to 2D
    n_components = min(2, all_embeddings.shape[0], all_embeddings.shape[1])
    pca = PCA(n_components=n_components)
    projected = pca.fit_transform(all_embeddings)

    # Handle edge case where PCA only returns 1 component
    if projected.shape[1] == 1:
        projected = np.hstack([projected, np.zeros((projected.shape[0], 1))])

    # Extract query point (first row)
    query_x, query_y = float(projected[0, 0]), float(projected[0, 1])

    # Build result points (rows 1 onwards)
    points = []
    for i, r in enumerate(results):
        x, y = float(projected[i + 1, 0]), float(projected[i + 1, 1])
        # Create a human-readable label
        label = f"{r.text[:30]}..." if len(r.text) > 30 else r.text
        preview = r.text[:50] if len(r.text) > 50 else r.text
        points.append(ProjectedPoint(
            x=x,
            y=y,
            fragment_id=f"{r.episode}_{r.start_secs}",
            label=label,
            preview=preview,
            score=r.score,
        ))

    return ProjectionResult(points=points, query_point=(query_x, query_y))
