# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Integration tests for collection migration from legacy to unified schema.

Tests the full migration workflow including:
- Exporting points from legacy collections
- Transforming payloads to unified schema
- Creating unified collections with named vectors
- Bulk importing transformed points
- Rollback procedures
"""

import uuid
from typing import Generator

import pytest
import qdrant_client
from qdrant_client import models

from voogle.vector_migration import (
    MigrationPlan,
    MigrationStatus,
    MigrationStep,
    bulk_import,
    create_unified_collection,
    execute_migration,
    export_existing_points,
    rollback_migration,
    transform_payload,
)


@pytest.fixture
def memory_client() -> Generator[qdrant_client.QdrantClient, None, None]:
    """Create an in-memory Qdrant client for testing."""
    client = qdrant_client.QdrantClient(":memory:")
    yield client
    # Cleanup handled by in-memory client going out of scope


@pytest.fixture
def legacy_collection_name() -> str:
    """Generate a unique legacy collection name for testing."""
    return f"test_legacy_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def unified_collection_name() -> str:
    """Generate a unique unified collection name for testing."""
    return f"test_unified_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def seeded_legacy_collection(
    memory_client: qdrant_client.QdrantClient,
    legacy_collection_name: str,
) -> str:
    """Create and seed a legacy collection with test data."""
    # Create legacy collection (single vector)
    memory_client.create_collection(
        collection_name=legacy_collection_name,
        vectors_config=models.VectorParams(
            size=384,
            distance=models.Distance.COSINE,
        ),
    )

    # Seed with test points
    points = [
        models.PointStruct(
            id=i,
            vector=[0.1 * (i + 1)] * 384,  # Deterministic vectors
            payload={
                "episode": 100 + i,
                "channel": 1,
                "start_secs": i * 30,
                "end_secs": (i + 1) * 30,
                "text": f"Test transcript fragment {i}",
            },
        )
        for i in range(10)
    ]

    memory_client.upsert(
        collection_name=legacy_collection_name,
        points=points,
    )

    return legacy_collection_name


class TestTransformPayload:
    """Tests for payload transformation from legacy to unified schema."""

    def test_transforms_legacy_fields(self) -> None:
        """Verify legacy fields are transformed to unified schema."""
        legacy = {
            "episode": 123,
            "channel": 1,
            "start_secs": 60,
            "end_secs": 90,
            "text": "Hello world",
        }

        result = transform_payload(legacy)

        # Legacy fields preserved
        assert result["episode"] == 123
        assert result["channel"] == 1
        assert result["start_secs"] == 60
        assert result["end_secs"] == 90
        assert result["text"] == "Hello world"

        # Unified fields added
        assert result["fragment_id"] == "123_60"
        assert result["source_id"] == "123"
        assert result["source_type"] == "audio"
        assert result["location_type"] == "timestamp"
        assert result["start_time"] == 60.0
        assert result["end_time"] == 90.0

    def test_preserves_embedding_metadata(self) -> None:
        """Verify embedding metadata is preserved during transformation."""
        legacy = {
            "episode": 456,
            "channel": 2,
            "start_secs": 0,
            "end_secs": 30,
            "text": "Test",
            "embedding_model": "all-MiniLM-L6-v2",
            "embedding_provider": "sentence-transformers",
            "embedded_at": "2025-01-01T00:00:00Z",
        }

        result = transform_payload(legacy)

        assert result["embedding_model"] == "all-MiniLM-L6-v2"
        assert result["embedding_provider"] == "sentence-transformers"
        assert result["embedded_at"] == "2025-01-01T00:00:00Z"

    def test_handles_video_source_type(self) -> None:
        """Verify video source type is handled correctly."""
        legacy = {"episode": 789, "start_secs": 0, "end_secs": 60, "text": "Video"}

        result = transform_payload(legacy, source_type="video")

        assert result["source_type"] == "video"
        assert result["location_type"] == "timestamp"

    def test_handles_document_source_type(self) -> None:
        """Verify document source type does not add timestamp fields."""
        legacy = {"episode": 999, "start_secs": 0, "end_secs": 0, "text": "Document"}

        result = transform_payload(legacy, source_type="document")

        assert result["source_type"] == "document"
        assert "location_type" not in result


class TestExportExistingPoints:
    """Tests for exporting points from existing collections."""

    def test_exports_all_points(
        self,
        memory_client: qdrant_client.QdrantClient,
        seeded_legacy_collection: str,
    ) -> None:
        """Verify all points are exported from a collection."""
        batches = list(export_existing_points(
            memory_client,
            seeded_legacy_collection,
            batch_size=5,
        ))

        # Should have 2 batches of 5 points each
        assert len(batches) == 2
        assert len(batches[0]) == 5
        assert len(batches[1]) == 5

        # Verify point data
        all_points = [p for batch in batches for p in batch]
        assert len(all_points) == 10

    def test_exports_with_vectors(
        self,
        memory_client: qdrant_client.QdrantClient,
        seeded_legacy_collection: str,
    ) -> None:
        """Verify vectors are included in export."""
        batches = list(export_existing_points(
            memory_client,
            seeded_legacy_collection,
            with_vectors=True,
        ))

        first_point = batches[0][0]
        assert first_point.vector is not None
        assert len(first_point.vector) == 384

    def test_raises_for_nonexistent_collection(
        self,
        memory_client: qdrant_client.QdrantClient,
    ) -> None:
        """Verify error when collection doesn't exist."""
        with pytest.raises(ValueError, match="does not exist"):
            list(export_existing_points(memory_client, "nonexistent"))


class TestCreateUnifiedCollection:
    """Tests for creating unified multimodal collections."""

    def test_creates_collection_with_named_vectors(
        self,
        memory_client: qdrant_client.QdrantClient,
        unified_collection_name: str,
    ) -> None:
        """Verify collection is created with named vector config."""
        create_unified_collection(
            memory_client,
            unified_collection_name,
            text_dense_dim=384,
        )

        info = memory_client.get_collection(unified_collection_name)
        assert info.config is not None

    def test_raises_if_exists_without_recreate(
        self,
        memory_client: qdrant_client.QdrantClient,
        unified_collection_name: str,
    ) -> None:
        """Verify error when collection exists and recreate=False."""
        create_unified_collection(memory_client, unified_collection_name)

        with pytest.raises(ValueError, match="already exists"):
            create_unified_collection(
                memory_client,
                unified_collection_name,
                recreate=False,
            )

    def test_recreates_existing_collection(
        self,
        memory_client: qdrant_client.QdrantClient,
        unified_collection_name: str,
    ) -> None:
        """Verify collection is recreated when recreate=True."""
        create_unified_collection(memory_client, unified_collection_name)
        create_unified_collection(
            memory_client,
            unified_collection_name,
            recreate=True,
        )

        # Should not raise
        info = memory_client.get_collection(unified_collection_name)
        assert info is not None


class TestBulkImport:
    """Tests for bulk importing points to unified collections."""

    def test_imports_points_with_named_vectors(
        self,
        memory_client: qdrant_client.QdrantClient,
        unified_collection_name: str,
    ) -> None:
        """Verify points are imported with correct named vector format."""
        create_unified_collection(memory_client, unified_collection_name)

        # Create test records
        records = [
            models.Record(
                id=i,
                vector=[0.1] * 384,
                payload={"episode": i, "channel": 1, "start_secs": 0, "end_secs": 30, "text": f"Test {i}"},
            )
            for i in range(5)
        ]

        count = bulk_import(memory_client, unified_collection_name, records)

        assert count == 5

        # Verify points in collection
        info = memory_client.get_collection(unified_collection_name)
        assert info.points_count == 5

    def test_transforms_payloads_during_import(
        self,
        memory_client: qdrant_client.QdrantClient,
        unified_collection_name: str,
    ) -> None:
        """Verify payloads are transformed to unified schema during import."""
        create_unified_collection(memory_client, unified_collection_name)

        records = [
            models.Record(
                id=1,
                vector=[0.1] * 384,
                payload={"episode": 123, "channel": 1, "start_secs": 60, "end_secs": 90, "text": "Test"},
            )
        ]

        bulk_import(memory_client, unified_collection_name, records)

        # Retrieve and verify payload transformation
        results = memory_client.scroll(
            collection_name=unified_collection_name,
            with_payload=True,
            limit=1,
        )[0]

        payload = results[0].payload
        assert payload["fragment_id"] == "123_60"
        assert payload["source_type"] == "audio"


class TestMigrationPlan:
    """Tests for the MigrationPlan dataclass."""

    def test_default_values(self) -> None:
        """Verify default plan values."""
        plan = MigrationPlan()

        assert plan.source_collection == "vectordb"
        assert plan.target_collection == "vectordb_unified"
        assert plan.batch_size == 1000
        assert plan.status == MigrationStatus.PENDING
        assert plan.preserve_source is True
        assert plan.verify_counts is True

    def test_auto_generates_backup_name(self) -> None:
        """Verify backup collection name is auto-generated."""
        plan = MigrationPlan(source_collection="test_source")

        assert plan.backup_collection is not None
        assert plan.backup_collection.startswith("test_source_backup_")

    def test_steps_property(self) -> None:
        """Verify migration steps are returned in order."""
        plan = MigrationPlan()

        assert plan.steps == [
            MigrationStep.EXPORT_POINTS,
            MigrationStep.CREATE_COLLECTION,
            MigrationStep.TRANSFORM_PAYLOADS,
            MigrationStep.BULK_IMPORT,
            MigrationStep.VERIFY_MIGRATION,
            MigrationStep.CLEANUP,
        ]

    def test_mark_step_complete(self) -> None:
        """Verify step completion tracking."""
        plan = MigrationPlan()

        plan.mark_step_complete(MigrationStep.EXPORT_POINTS)

        assert plan.is_step_complete(MigrationStep.EXPORT_POINTS)
        assert not plan.is_step_complete(MigrationStep.CREATE_COLLECTION)


class TestExecuteMigration:
    """Integration tests for full migration execution."""

    def test_successful_migration(
        self,
        memory_client: qdrant_client.QdrantClient,
        seeded_legacy_collection: str,
        unified_collection_name: str,
    ) -> None:
        """Verify successful end-to-end migration."""
        plan = MigrationPlan(
            source_collection=seeded_legacy_collection,
            target_collection=unified_collection_name,
            batch_size=5,
        )

        result = execute_migration(memory_client, plan)

        assert result.status == MigrationStatus.COMPLETED
        assert result.points_exported == 10
        assert result.points_imported == 10
        assert result.completed_at is not None

        # Verify target collection has all points
        info = memory_client.get_collection(unified_collection_name)
        assert info.points_count == 10

    def test_dry_run_makes_no_changes(
        self,
        memory_client: qdrant_client.QdrantClient,
        seeded_legacy_collection: str,
        unified_collection_name: str,
    ) -> None:
        """Verify dry run doesn't create target collection."""
        plan = MigrationPlan(
            source_collection=seeded_legacy_collection,
            target_collection=unified_collection_name,
        )

        result = execute_migration(memory_client, plan, dry_run=True)

        assert result.status == MigrationStatus.COMPLETED
        assert not memory_client.collection_exists(unified_collection_name)

    def test_fails_for_missing_source(
        self,
        memory_client: qdrant_client.QdrantClient,
        unified_collection_name: str,
    ) -> None:
        """Verify migration fails gracefully when source doesn't exist."""
        plan = MigrationPlan(
            source_collection="nonexistent",
            target_collection=unified_collection_name,
        )

        with pytest.raises(ValueError, match="not found"):
            execute_migration(memory_client, plan)

        assert plan.status == MigrationStatus.FAILED


class TestRollbackMigration:
    """Tests for migration rollback procedures."""

    def test_deletes_target_collection(
        self,
        memory_client: qdrant_client.QdrantClient,
        seeded_legacy_collection: str,
        unified_collection_name: str,
    ) -> None:
        """Verify rollback deletes the target collection."""
        # Create target collection
        create_unified_collection(memory_client, unified_collection_name)

        plan = MigrationPlan(
            source_collection=seeded_legacy_collection,
            target_collection=unified_collection_name,
        )

        success = rollback_migration(memory_client, plan)

        assert success
        assert plan.status == MigrationStatus.ROLLED_BACK
        assert not memory_client.collection_exists(unified_collection_name)

    def test_handles_missing_target(
        self,
        memory_client: qdrant_client.QdrantClient,
        seeded_legacy_collection: str,
    ) -> None:
        """Verify rollback succeeds even if target doesn't exist."""
        plan = MigrationPlan(
            source_collection=seeded_legacy_collection,
            target_collection="nonexistent_target",
        )

        success = rollback_migration(memory_client, plan)

        assert success
        assert plan.status == MigrationStatus.ROLLED_BACK
