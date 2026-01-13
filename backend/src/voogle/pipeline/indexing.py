# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Indexing stage for Qdrant upsert with metadata preservation and deduplication.

This module provides the IndexingStage class that handles the final stage of the
ingestion pipeline - storing embedded fragments into Qdrant vector database.

Features:
    - Batch upsert for efficient storage
    - Named vector assignment for multimodal support
    - Deduplication by content hash to prevent duplicates
    - Index optimization triggers for performance

Usage:
    from voogle.pipeline.indexing import IndexingStage

    stage = IndexingStage(collection_name="my_collection", batch_size=100)
    async for result in stage.process(embedded_fragments):
        print(f"Indexed: {result}")
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

import numpy as np
from qdrant_client import QdrantClient, models

from voogle.pipeline.base import Stage, StageError
from voogle.vector_schema import VectorName, get_collection_config

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class IndexingConfig:
    """Configuration for the indexing stage.

    Attributes:
        collection_name: Name of the Qdrant collection to upsert into.
        batch_size: Number of points to upsert in each batch.
        enable_deduplication: Whether to deduplicate by content hash.
        optimize_threshold: Number of points after which to trigger optimization.
        vector_name: Name of the vector field to use for storage.
        wait_for_upsert: Whether to wait for upsert to complete before returning.
    """

    collection_name: str = "vectordb"
    batch_size: int = 100
    enable_deduplication: bool = True
    optimize_threshold: int = 10000
    vector_name: str = VectorName.TEXT_DENSE.value
    wait_for_upsert: bool = True

    def __post_init__(self) -> None:
        """Validate indexing configuration."""
        if not self.collection_name:
            raise ValueError("collection_name cannot be empty")
        if self.batch_size < 1:
            raise ValueError(f"batch_size must be >= 1, got {self.batch_size}")
        if self.optimize_threshold < 1:
            raise ValueError(
                f"optimize_threshold must be >= 1, got {self.optimize_threshold}"
            )


@dataclass
class EmbeddedFragment:
    """A fragment with its embedding vector, ready for indexing.

    Attributes:
        id: Unique identifier for this fragment.
        text: The text content of this fragment.
        embedding: The embedding vector (numpy array or list of floats).
        source_id: Identifier of the source containing this fragment.
        source_type: Type of content source (audio, video, document, etc.).
        vector_name: Name of the vector field (for multimodal support).
        location: Source-specific location data.
        deep_link: URL or path to directly access this fragment.
        metadata: Additional source-specific metadata.
    """

    id: str
    text: str
    embedding: np.ndarray | list[float]
    source_id: str
    source_type: str = "text"
    vector_name: str = VectorName.TEXT_DENSE.value
    location: Optional[dict[str, Any]] = None
    deep_link: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def content_hash(self) -> str:
        """Generate a hash of the content for deduplication.

        The hash is based on text content, source_id, and location to uniquely
        identify a fragment regardless of when it was embedded.
        """
        data = f"{self.text}|{self.source_id}|{self.location}"
        return hashlib.sha256(data.encode("utf-8")).hexdigest()


@dataclass
class IndexingResult:
    """Result of indexing a batch of fragments.

    Attributes:
        point_ids: List of point IDs that were upserted.
        deduplicated_count: Number of fragments that were deduplicated.
        batch_size: Number of fragments in this batch.
        collection_name: Name of the collection where points were stored.
    """

    point_ids: list[str]
    deduplicated_count: int
    batch_size: int
    collection_name: str


def generate_point_id(content_hash: str) -> str:
    """Generate a deterministic Qdrant point ID from content hash.

    Using deterministic IDs makes upsert operations idempotent - if a job
    crashes and retries, it will overwrite the same points rather than
    creating duplicates.

    Args:
        content_hash: SHA256 hash of the fragment content.

    Returns:
        A deterministic UUID string for the Qdrant point.
    """
    # Use first 16 bytes of hash to create a UUID
    hash_bytes = bytes.fromhex(content_hash[:32])
    return str(uuid.UUID(bytes=hash_bytes, version=4))


class IndexingStage(Stage[EmbeddedFragment, IndexingResult]):
    """Pipeline stage for indexing embedded fragments into Qdrant.

    This stage handles the final step of the ingestion pipeline, storing
    embedded fragments into the Qdrant vector database with proper metadata
    and deduplication.

    Features:
        - Batch upsert for efficient storage
        - Named vector assignment for multimodal support
        - Deduplication by content hash to prevent duplicates
        - Index optimization triggers for performance

    Example:
        stage = IndexingStage(
            client=qdrant_client,
            config=IndexingConfig(batch_size=100)
        )

        async for result in pipeline.execute(embedded_fragments):
            print(f"Indexed {result.batch_size} fragments")
    """

    def __init__(
        self,
        client: Optional[QdrantClient] = None,
        config: Optional[IndexingConfig] = None,
    ):
        """Initialize the indexing stage.

        Args:
            client: Qdrant client instance. If None, must be set before processing.
            config: Indexing configuration. Uses defaults if not provided.
        """
        self._client = client
        self._config = config or IndexingConfig()
        self._points_indexed: int = 0
        self._seen_hashes: set[str] = set()
        self._batch: list[EmbeddedFragment] = []

    @property
    def name(self) -> str:
        """Return the name of this stage."""
        return "indexing"

    @property
    def client(self) -> Optional[QdrantClient]:
        """Return the Qdrant client."""
        return self._client

    @client.setter
    def client(self, value: QdrantClient) -> None:
        """Set the Qdrant client."""
        self._client = value

    @property
    def config(self) -> IndexingConfig:
        """Return the indexing configuration."""
        return self._config

    @property
    def points_indexed(self) -> int:
        """Return the total number of points indexed."""
        return self._points_indexed

    async def setup(self) -> None:
        """Initialize resources before processing begins.

        Ensures the target collection exists with proper schema.
        """
        if self._client is None:
            logger.warning("No Qdrant client configured, skipping collection check")
            return

        # Check if collection exists, create if needed
        try:
            if not self._client.collection_exists(self._config.collection_name):
                logger.info(
                    f"Creating collection '{self._config.collection_name}' with multimodal schema"
                )
                config = get_collection_config()
                self._client.create_collection(
                    collection_name=self._config.collection_name,
                    vectors_config=config.vectors_config,
                    sparse_vectors_config={
                        VectorName.TEXT_SPARSE.value: models.SparseVectorParams(
                            modifier=models.Modifier.IDF,
                        )
                    },
                    quantization_config=config.quantization_config,
                )
        except Exception as e:
            logger.error(f"Failed to ensure collection exists: {e}")
            raise StageError(self.name, f"Failed to ensure collection: {e}", cause=e)

    async def teardown(self) -> None:
        """Clean up resources after processing completes.

        Flushes any remaining batch and optionally triggers optimization.
        """
        # Flush remaining batch
        if self._batch:
            await self._flush_batch()

        # Trigger optimization if threshold reached
        if (
            self._client is not None
            and self._points_indexed >= self._config.optimize_threshold
        ):
            await self._trigger_optimization()

    async def process(
        self, items: AsyncIterator[EmbeddedFragment]
    ) -> AsyncIterator[IndexingResult]:
        """Process embedded fragments and index them into Qdrant.

        Args:
            items: Async iterator of embedded fragments to index.

        Yields:
            IndexingResult for each batch that is processed.

        Raises:
            StageError: If indexing fails.
        """
        if self._client is None:
            raise StageError(self.name, "No Qdrant client configured")

        async for fragment in items:
            # Check for deduplication
            if self._config.enable_deduplication:
                content_hash = fragment.content_hash
                if content_hash in self._seen_hashes:
                    logger.debug(f"Skipping duplicate fragment: {fragment.id}")
                    continue
                self._seen_hashes.add(content_hash)

            self._batch.append(fragment)

            # Flush batch if full
            if len(self._batch) >= self._config.batch_size:
                result = await self._flush_batch()
                yield result

    async def _flush_batch(self) -> IndexingResult:
        """Flush the current batch to Qdrant.

        Returns:
            IndexingResult with details about the upserted points.

        Raises:
            StageError: If upsert fails.
        """
        if not self._batch:
            return IndexingResult(
                point_ids=[],
                deduplicated_count=0,
                batch_size=0,
                collection_name=self._config.collection_name,
            )

        if self._client is None:
            raise StageError(self.name, "No Qdrant client configured")

        points = []
        point_ids = []

        for fragment in self._batch:
            point_id = generate_point_id(fragment.content_hash)
            point_ids.append(point_id)

            # Convert embedding to list if numpy array
            embedding = (
                fragment.embedding.tolist()
                if isinstance(fragment.embedding, np.ndarray)
                else fragment.embedding
            )

            # Build payload with metadata
            payload = self._build_payload(fragment)

            # Create point with named vector
            point = models.PointStruct(
                id=point_id,
                vector={fragment.vector_name: embedding},
                payload=payload,
            )
            points.append(point)

        try:
            self._client.upsert(
                collection_name=self._config.collection_name,
                points=points,
                wait=self._config.wait_for_upsert,
            )
            self._points_indexed += len(points)
            logger.info(
                f"Indexed {len(points)} points to '{self._config.collection_name}'"
            )
        except Exception as e:
            logger.error(f"Failed to upsert batch: {e}")
            raise StageError(self.name, f"Failed to upsert batch: {e}", cause=e)

        batch_size = len(self._batch)
        self._batch = []

        return IndexingResult(
            point_ids=point_ids,
            deduplicated_count=0,  # Already filtered during process()
            batch_size=batch_size,
            collection_name=self._config.collection_name,
        )

    def _build_payload(self, fragment: EmbeddedFragment) -> dict[str, Any]:
        """Build the payload dictionary for a Qdrant point.

        Args:
            fragment: The embedded fragment to build payload for.

        Returns:
            Dictionary of payload fields.
        """
        payload: dict[str, Any] = {
            "fragment_id": fragment.id,
            "text": fragment.text,
            "source_id": fragment.source_id,
            "source_type": fragment.source_type,
            "content_hash": fragment.content_hash,
            "indexed_at": datetime.now(timezone.utc).isoformat(),
        }

        if fragment.deep_link:
            payload["deep_link"] = fragment.deep_link

        if fragment.location:
            payload["location_type"] = fragment.location.get("type", "unknown")
            # Flatten location fields into payload
            for key, value in fragment.location.items():
                if key != "type":
                    payload[key] = value

        # Include any additional metadata
        if fragment.metadata:
            for key, value in fragment.metadata.items():
                # Avoid overwriting core fields
                if key not in payload:
                    payload[key] = value

        return payload

    async def _trigger_optimization(self) -> None:
        """Trigger index optimization in Qdrant.

        This optimizes the index structure for better query performance
        after bulk insertions.
        """
        if self._client is None:
            return

        try:
            logger.info(
                f"Triggering optimization for '{self._config.collection_name}' "
                f"after indexing {self._points_indexed} points"
            )
            # Update collection to trigger re-indexing optimization
            self._client.update_collection(
                collection_name=self._config.collection_name,
                optimizer_config=models.OptimizersConfigDiff(
                    indexing_threshold=20000,
                ),
            )
        except Exception as e:
            # Optimization failure is not critical, just log it
            logger.warning(f"Failed to trigger optimization: {e}")

    def __str__(self) -> str:
        """Return a string representation of this stage."""
        return (
            f"IndexingStage(collection='{self._config.collection_name}', "
            f"batch_size={self._config.batch_size}, "
            f"dedup={self._config.enable_deduplication})"
        )

    def __repr__(self) -> str:
        """Return a detailed representation of this stage."""
        return (
            f"IndexingStage(client={self._client!r}, "
            f"config={self._config!r}, "
            f"points_indexed={self._points_indexed})"
        )
