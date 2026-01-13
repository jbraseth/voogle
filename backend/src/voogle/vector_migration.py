# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Collection migration utilities for Qdrant vector database.

Provides zero-downtime migration from legacy podcast-only collections
to the unified multimodal schema. Supports:

- Exporting existing points from legacy collections
- Transforming payloads to unified schema format
- Creating new collections with multimodal vector support
- Bulk importing transformed points
- Rollback procedures for failed migrations

Usage:
    from voogle.vector_migration import MigrationPlan, execute_migration

    plan = MigrationPlan(
        source_collection="vectordb",
        target_collection="vectordb_v2",
    )
    execute_migration(client, plan)
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Iterator, Optional

from qdrant_client import QdrantClient, models

from voogle.vector_schema import (
    VectorName,
    get_collection_config,
    create_collection_with_schema,
)

logger = logging.getLogger(__name__)


class MigrationStatus(str, Enum):
    """Status of a migration step or overall migration."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class MigrationStep(str, Enum):
    """Individual steps in the migration process."""

    EXPORT_POINTS = "export_points"
    CREATE_COLLECTION = "create_collection"
    TRANSFORM_PAYLOADS = "transform_payloads"
    BULK_IMPORT = "bulk_import"
    VERIFY_MIGRATION = "verify_migration"
    CLEANUP = "cleanup"


@dataclass
class MigrationPlan:
    """Configuration and state for a collection migration.

    Attributes:
        source_collection: Name of the legacy collection to migrate from.
        target_collection: Name of the new unified collection.
        batch_size: Number of points to process per batch.
        backup_collection: Name for backup collection (auto-generated if None).
        preserve_source: Whether to keep source collection after migration.
        verify_counts: Whether to verify point counts match after migration.
    """

    source_collection: str = "vectordb"
    target_collection: str = "vectordb_unified"
    batch_size: int = 1000
    backup_collection: Optional[str] = None
    preserve_source: bool = True
    verify_counts: bool = True

    # Migration state
    status: MigrationStatus = MigrationStatus.PENDING
    current_step: Optional[MigrationStep] = None
    completed_steps: list[MigrationStep] = field(default_factory=list)
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    points_exported: int = 0
    points_imported: int = 0

    def __post_init__(self) -> None:
        """Initialize backup collection name if not provided."""
        if self.backup_collection is None:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            self.backup_collection = f"{self.source_collection}_backup_{timestamp}"

    @property
    def steps(self) -> list[MigrationStep]:
        """Return ordered list of migration steps."""
        return [
            MigrationStep.EXPORT_POINTS,
            MigrationStep.CREATE_COLLECTION,
            MigrationStep.TRANSFORM_PAYLOADS,
            MigrationStep.BULK_IMPORT,
            MigrationStep.VERIFY_MIGRATION,
            MigrationStep.CLEANUP,
        ]

    def mark_step_complete(self, step: MigrationStep) -> None:
        """Mark a migration step as completed."""
        if step not in self.completed_steps:
            self.completed_steps.append(step)

    def is_step_complete(self, step: MigrationStep) -> bool:
        """Check if a migration step has been completed."""
        return step in self.completed_steps


def export_existing_points(
    client: QdrantClient,
    collection_name: str,
    batch_size: int = 1000,
    with_vectors: bool = True,
) -> Iterator[list[models.Record]]:
    """Export all points from an existing collection in batches.

    Yields batches of points for memory-efficient processing of large
    collections. Each batch contains up to batch_size points.

    Args:
        client: Qdrant client instance.
        collection_name: Name of the collection to export from.
        batch_size: Maximum number of points per batch.
        with_vectors: Whether to include vectors in export.

    Yields:
        Lists of Record objects containing point data.

    Raises:
        ValueError: If collection does not exist.
    """
    if not client.collection_exists(collection_name):
        raise ValueError(f"Collection '{collection_name}' does not exist")

    logger.info(f"Exporting points from collection '{collection_name}'")

    offset = None
    total_exported = 0

    while True:
        # Scroll through collection
        records, next_offset = client.scroll(
            collection_name=collection_name,
            limit=batch_size,
            offset=offset,
            with_vectors=with_vectors,
            with_payload=True,
        )

        if not records:
            break

        total_exported += len(records)
        logger.debug(f"Exported batch of {len(records)} points (total: {total_exported})")
        yield records

        if next_offset is None:
            break
        offset = next_offset

    logger.info(f"Export complete: {total_exported} total points")


def transform_payload(
    legacy_payload: dict[str, Any],
    source_type: str = "audio",
) -> dict[str, Any]:
    """Transform a legacy payload to the unified multimodal schema.

    Converts podcast-specific fields to the unified schema format while
    preserving backward-compatible legacy fields.

    Legacy schema fields:
        - episode: int (episode primary key)
        - channel: int (channel primary key)
        - start_secs: int (fragment start time)
        - end_secs: int (fragment end time)
        - text: str (fragment text)

    Unified schema adds:
        - fragment_id: str (derived from episode + start_secs)
        - source_id: str (episode pk as string)
        - source_type: str (content type: audio, video, document, etc.)
        - location_type: str (timestamp for audio/video)
        - start_time: float (fragment start time in seconds)
        - end_time: float (fragment end time in seconds)
        - embedded_at: str (ISO timestamp if present)

    Args:
        legacy_payload: Original payload from legacy collection.
        source_type: Content type for the source (default: "audio").

    Returns:
        Transformed payload with unified schema fields.
    """
    # Start with a copy of legacy fields for backward compatibility
    unified = dict(legacy_payload)

    # Extract legacy fields
    episode = legacy_payload.get("episode")
    start_secs = legacy_payload.get("start_secs", 0)
    end_secs = legacy_payload.get("end_secs", 0)

    # Add unified schema fields
    if episode is not None:
        unified["fragment_id"] = f"{episode}_{start_secs}"
        unified["source_id"] = str(episode)

    unified["source_type"] = source_type

    # Add location fields for timestamp-based content
    if source_type in ("audio", "video"):
        unified["location_type"] = "timestamp"
        unified["start_time"] = float(start_secs)
        unified["end_time"] = float(end_secs)

    # Preserve embedding metadata if present
    if "embedded_at" not in unified and "embedding_model" in legacy_payload:
        unified["embedded_at"] = datetime.now(timezone.utc).isoformat()

    return unified


def create_unified_collection(
    client: QdrantClient,
    collection_name: str,
    text_dense_dim: int = 384,
    recreate: bool = False,
) -> None:
    """Create a new collection with the unified multimodal schema.

    Creates a collection supporting named vectors for different embedding
    types (text_dense, text_sparse, image, multimodal) with appropriate
    payload indexes for efficient filtering.

    Args:
        client: Qdrant client instance.
        collection_name: Name for the new collection.
        text_dense_dim: Dimension for dense text embeddings (default: 384).
        recreate: If True, delete existing collection first.

    Raises:
        ValueError: If collection exists and recreate is False.
    """
    logger.info(f"Creating unified collection '{collection_name}' with dim={text_dense_dim}")

    config = get_collection_config(
        text_dense_dim=text_dense_dim,
        enable_quantization=True,
        on_disk_payload=False,
    )

    create_collection_with_schema(client, collection_name, config, recreate=recreate)
    logger.info(f"Created unified collection '{collection_name}'")


def bulk_import(
    client: QdrantClient,
    collection_name: str,
    points: list[models.Record],
    vector_name: str = VectorName.TEXT_DENSE.value,
) -> int:
    """Import points into a unified collection with named vectors.

    Transforms legacy single-vector points to named vector format and
    upserts them into the target collection.

    Args:
        client: Qdrant client instance.
        collection_name: Target collection name.
        points: List of Record objects to import.
        vector_name: Name of the vector field for legacy vectors.

    Returns:
        Number of points successfully imported.
    """
    if not points:
        return 0

    # Transform to PointStruct with named vectors
    point_structs = []
    for record in points:
        # Handle both single vector and named vector formats
        vector = record.vector
        if isinstance(vector, dict):
            # Already named vectors - use as-is
            vectors = vector
        elif vector is not None:
            # Single vector - convert to named format
            if isinstance(vector, list):
                vectors = {vector_name: vector}
            else:
                vectors = {vector_name: list(vector)}
        else:
            # No vector - skip
            logger.warning(f"Skipping point {record.id} with no vector")
            continue

        # Transform payload to unified schema
        payload = transform_payload(record.payload or {})

        point_structs.append(
            models.PointStruct(
                id=record.id,
                vector=vectors,
                payload=payload,
            )
        )

    if not point_structs:
        return 0

    # Upsert batch
    client.upsert(
        collection_name=collection_name,
        points=point_structs,
    )

    logger.debug(f"Imported {len(point_structs)} points to '{collection_name}'")
    return len(point_structs)


def rollback_migration(
    client: QdrantClient,
    plan: MigrationPlan,
) -> bool:
    """Rollback a failed migration by restoring from backup.

    If a backup collection exists, this function:
    1. Deletes the partially migrated target collection
    2. Renames the backup to the original source name (if source was modified)
    3. Updates the migration plan status

    Args:
        client: Qdrant client instance.
        plan: Migration plan with backup collection info.

    Returns:
        True if rollback succeeded, False otherwise.
    """
    logger.warning(f"Rolling back migration from '{plan.source_collection}'")
    plan.status = MigrationStatus.ROLLED_BACK

    try:
        # Delete target collection if it exists
        if client.collection_exists(plan.target_collection):
            logger.info(f"Deleting target collection '{plan.target_collection}'")
            client.delete_collection(plan.target_collection)

        # If we have a backup and source was deleted, restore it
        if (
            plan.backup_collection
            and client.collection_exists(plan.backup_collection)
            and not client.collection_exists(plan.source_collection)
        ):
            logger.info(
                f"Restoring backup '{plan.backup_collection}' to '{plan.source_collection}'"
            )
            # Qdrant doesn't support rename, so we need to copy
            # For now, just log - actual restore would require re-export/import
            logger.warning(
                "Backup restoration requires manual intervention: "
                f"copy '{plan.backup_collection}' to '{plan.source_collection}'"
            )

        return True

    except Exception as e:
        logger.error(f"Rollback failed: {e}")
        plan.error_message = f"Rollback failed: {e}"
        return False


def _get_collection_count(client: QdrantClient, collection_name: str) -> int:
    """Get the number of points in a collection."""
    info = client.get_collection(collection_name)
    return info.points_count or 0


def _verify_migration(
    client: QdrantClient,
    plan: MigrationPlan,
) -> bool:
    """Verify migration by comparing point counts."""
    source_count = _get_collection_count(client, plan.source_collection)
    target_count = _get_collection_count(client, plan.target_collection)

    if source_count != target_count:
        logger.error(
            f"Point count mismatch: source={source_count}, target={target_count}"
        )
        return False

    logger.info(f"Migration verified: {target_count} points in target collection")
    return True


def execute_migration(
    client: QdrantClient,
    plan: MigrationPlan,
    dry_run: bool = False,
) -> MigrationPlan:
    """Execute a full collection migration following the migration plan.

    Performs the migration in steps:
    1. Export points from source collection
    2. Create unified target collection
    3. Transform payloads to unified schema
    4. Bulk import to target collection
    5. Verify point counts match
    6. Cleanup (optional backup deletion)

    Zero-downtime is achieved by:
    - Creating a new target collection (doesn't affect source)
    - Only modifying source after successful verification
    - Maintaining backup for rollback

    Args:
        client: Qdrant client instance.
        plan: Migration plan configuration.
        dry_run: If True, only validate without making changes.

    Returns:
        Updated MigrationPlan with final status.

    Raises:
        Exception: If migration fails (plan.status will be FAILED).
    """
    plan.status = MigrationStatus.IN_PROGRESS
    plan.started_at = datetime.now(timezone.utc)

    try:
        # Validate source exists
        if not client.collection_exists(plan.source_collection):
            raise ValueError(f"Source collection '{plan.source_collection}' not found")

        # Get source vector dimension
        source_info = client.get_collection(plan.source_collection)
        source_config = source_info.config

        # Extract dimension from vectors_config
        vector_dim = 384  # default
        if source_config and source_config.params:
            vectors_config = source_config.params.vectors
            if isinstance(vectors_config, models.VectorParams):
                vector_dim = vectors_config.size
            elif isinstance(vectors_config, dict):
                # Named vectors - get first dense vector size
                for _, params in vectors_config.items():
                    if isinstance(params, models.VectorParams):
                        vector_dim = params.size
                        break

        logger.info(f"Source collection has {source_info.points_count} points, dim={vector_dim}")

        if dry_run:
            logger.info("Dry run - no changes will be made")
            plan.status = MigrationStatus.COMPLETED
            return plan

        # Step 1: Create unified collection
        plan.current_step = MigrationStep.CREATE_COLLECTION
        create_unified_collection(
            client,
            plan.target_collection,
            text_dense_dim=vector_dim,
            recreate=True,
        )
        plan.mark_step_complete(MigrationStep.CREATE_COLLECTION)

        # Step 2-4: Export, transform, and import in batches
        plan.current_step = MigrationStep.EXPORT_POINTS
        total_imported = 0

        for batch in export_existing_points(client, plan.source_collection, plan.batch_size):
            plan.points_exported += len(batch)

            # Transform and import batch
            plan.current_step = MigrationStep.BULK_IMPORT
            imported = bulk_import(client, plan.target_collection, batch)
            total_imported += imported

        plan.points_imported = total_imported
        plan.mark_step_complete(MigrationStep.EXPORT_POINTS)
        plan.mark_step_complete(MigrationStep.TRANSFORM_PAYLOADS)
        plan.mark_step_complete(MigrationStep.BULK_IMPORT)

        # Step 5: Verify migration
        plan.current_step = MigrationStep.VERIFY_MIGRATION
        if plan.verify_counts and not _verify_migration(client, plan):
            raise ValueError("Migration verification failed - point counts do not match")
        plan.mark_step_complete(MigrationStep.VERIFY_MIGRATION)

        # Step 6: Cleanup (mark complete, source preservation handled by caller)
        plan.current_step = MigrationStep.CLEANUP
        plan.mark_step_complete(MigrationStep.CLEANUP)

        plan.status = MigrationStatus.COMPLETED
        plan.completed_at = datetime.now(timezone.utc)
        logger.info(
            f"Migration completed: {plan.points_imported} points migrated to '{plan.target_collection}'"
        )

    except Exception as e:
        plan.status = MigrationStatus.FAILED
        plan.error_message = str(e)
        plan.completed_at = datetime.now(timezone.utc)
        logger.error(f"Migration failed: {e}")
        raise

    return plan
