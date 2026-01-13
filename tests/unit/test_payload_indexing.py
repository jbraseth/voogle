# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for payload indexing optimization.

Tests the payload index configuration for optimal filter performance
with tenant isolation support (V5).
"""

from unittest.mock import MagicMock

import pytest
from qdrant_client import models
from voogle.vector_schema import (
    PRIMARY_PAYLOAD_INDEXES,
    CollectionIndexReport,
    PayloadIndexConfig,
    PayloadIndexStatus,
    ensure_primary_indexes,
    get_collection_index_status,
    get_payload_indexes,
    get_tenant_indexes,
)


class TestPayloadIndexConfig:
    """Tests for PayloadIndexConfig dataclass."""

    def test_default_values(self):
        """PayloadIndexConfig should default is_tenant to False."""
        config = PayloadIndexConfig(
            field_name="test_field",
            field_type=models.PayloadSchemaType.KEYWORD,
        )
        assert config.field_name == "test_field"
        assert config.field_type == models.PayloadSchemaType.KEYWORD
        assert config.is_tenant is False

    def test_tenant_field(self):
        """PayloadIndexConfig should support tenant marking."""
        config = PayloadIndexConfig(
            field_name="corpus_id",
            field_type=models.PayloadSchemaType.KEYWORD,
            is_tenant=True,
        )
        assert config.is_tenant is True

    def test_immutable(self):
        """PayloadIndexConfig should be immutable (frozen dataclass)."""
        config = PayloadIndexConfig(
            field_name="test",
            field_type=models.PayloadSchemaType.KEYWORD,
        )
        with pytest.raises(AttributeError):
            config.field_name = "modified"  # type: ignore[misc]


class TestPrimaryPayloadIndexes:
    """Tests for PRIMARY_PAYLOAD_INDEXES constant."""

    def test_has_corpus_id(self):
        """Primary indexes should include corpus_id as tenant field."""
        corpus_idx = next(
            (idx for idx in PRIMARY_PAYLOAD_INDEXES if idx.field_name == "corpus_id"),
            None,
        )
        assert corpus_idx is not None
        assert corpus_idx.field_type == models.PayloadSchemaType.KEYWORD
        assert corpus_idx.is_tenant is True

    def test_has_content_type(self):
        """Primary indexes should include content_type."""
        content_type_idx = next(
            (idx for idx in PRIMARY_PAYLOAD_INDEXES if idx.field_name == "content_type"),
            None,
        )
        assert content_type_idx is not None
        assert content_type_idx.field_type == models.PayloadSchemaType.KEYWORD
        assert content_type_idx.is_tenant is False

    def test_has_source_id(self):
        """Primary indexes should include source_id as UUID."""
        source_idx = next(
            (idx for idx in PRIMARY_PAYLOAD_INDEXES if idx.field_name == "source_id"),
            None,
        )
        assert source_idx is not None
        assert source_idx.field_type == models.PayloadSchemaType.UUID
        assert source_idx.is_tenant is False

    def test_has_created_at(self):
        """Primary indexes should include created_at as datetime."""
        created_idx = next(
            (idx for idx in PRIMARY_PAYLOAD_INDEXES if idx.field_name == "created_at"),
            None,
        )
        assert created_idx is not None
        assert created_idx.field_type == models.PayloadSchemaType.DATETIME
        assert created_idx.is_tenant is False

    def test_index_count(self):
        """Should have exactly 4 primary indexes."""
        assert len(PRIMARY_PAYLOAD_INDEXES) == 4


class TestGetPayloadIndexes:
    """Tests for get_payload_indexes function."""

    def test_returns_list(self):
        """get_payload_indexes should return a list."""
        indexes = get_payload_indexes()
        assert isinstance(indexes, list)

    def test_contains_all_primary_indexes(self):
        """get_payload_indexes should contain all primary indexes."""
        indexes = get_payload_indexes()
        assert len(indexes) == len(PRIMARY_PAYLOAD_INDEXES)
        for idx in PRIMARY_PAYLOAD_INDEXES:
            assert idx in indexes

    def test_returns_copy(self):
        """get_payload_indexes should return a copy, not the original."""
        indexes1 = get_payload_indexes()
        indexes2 = get_payload_indexes()
        assert indexes1 is not indexes2

    def test_all_are_payload_index_config(self):
        """All items should be PayloadIndexConfig instances."""
        indexes = get_payload_indexes()
        for idx in indexes:
            assert isinstance(idx, PayloadIndexConfig)

    def test_expected_field_names(self):
        """Should have the expected field names."""
        indexes = get_payload_indexes()
        field_names = {idx.field_name for idx in indexes}
        expected = {"corpus_id", "content_type", "source_id", "created_at"}
        assert field_names == expected


class TestGetTenantIndexes:
    """Tests for get_tenant_indexes function."""

    def test_returns_only_tenant_indexes(self):
        """get_tenant_indexes should return only indexes marked as tenant."""
        tenant_indexes = get_tenant_indexes()
        for idx in tenant_indexes:
            assert idx.is_tenant is True

    def test_includes_corpus_id(self):
        """Tenant indexes should include corpus_id."""
        tenant_indexes = get_tenant_indexes()
        field_names = {idx.field_name for idx in tenant_indexes}
        assert "corpus_id" in field_names

    def test_excludes_non_tenant_fields(self):
        """Tenant indexes should not include non-tenant fields."""
        tenant_indexes = get_tenant_indexes()
        field_names = {idx.field_name for idx in tenant_indexes}
        # These are not tenant fields
        assert "content_type" not in field_names
        assert "source_id" not in field_names
        assert "created_at" not in field_names


class TestPayloadIndexStatus:
    """Tests for PayloadIndexStatus dataclass."""

    def test_required_fields(self):
        """PayloadIndexStatus should require field_name and indexed."""
        status = PayloadIndexStatus(
            field_name="test_field",
            indexed=True,
        )
        assert status.field_name == "test_field"
        assert status.indexed is True

    def test_optional_fields(self):
        """PayloadIndexStatus should support optional fields."""
        status = PayloadIndexStatus(
            field_name="test_field",
            indexed=True,
            index_type="keyword",
            points_count=100,
        )
        assert status.index_type == "keyword"
        assert status.points_count == 100

    def test_optional_fields_default_none(self):
        """Optional fields should default to None."""
        status = PayloadIndexStatus(field_name="test", indexed=False)
        assert status.index_type is None
        assert status.points_count is None


class TestCollectionIndexReport:
    """Tests for CollectionIndexReport dataclass."""

    def test_all_fields(self):
        """CollectionIndexReport should contain all expected fields."""
        report = CollectionIndexReport(
            collection_name="test_collection",
            indexes=[
                PayloadIndexStatus(field_name="corpus_id", indexed=True),
            ],
            missing_primary_indexes=["content_type", "source_id"],
            has_tenant_index=True,
        )
        assert report.collection_name == "test_collection"
        assert len(report.indexes) == 1
        assert len(report.missing_primary_indexes) == 2
        assert report.has_tenant_index is True


class TestGetCollectionIndexStatus:
    """Tests for get_collection_index_status function."""

    def test_raises_for_nonexistent_collection(self):
        """Should raise ValueError for non-existent collection."""
        mock_client = MagicMock()
        mock_client.collection_exists.return_value = False

        with pytest.raises(ValueError, match="does not exist"):
            get_collection_index_status(mock_client, "nonexistent")

    def test_reports_existing_indexes(self):
        """Should report existing indexes from collection schema."""
        mock_client = MagicMock()
        mock_client.collection_exists.return_value = True

        mock_field_info = MagicMock()
        mock_field_info.data_type = "keyword"
        mock_field_info.points = 100

        mock_collection_info = MagicMock()
        mock_collection_info.payload_schema = {
            "corpus_id": mock_field_info,
        }
        mock_client.get_collection.return_value = mock_collection_info

        report = get_collection_index_status(mock_client, "test_collection")

        assert report.collection_name == "test_collection"
        assert len(report.indexes) == 1
        assert report.indexes[0].field_name == "corpus_id"
        assert report.indexes[0].indexed is True
        assert report.has_tenant_index is True

    def test_reports_missing_primary_indexes(self):
        """Should report missing primary indexes."""
        mock_client = MagicMock()
        mock_client.collection_exists.return_value = True

        mock_collection_info = MagicMock()
        mock_collection_info.payload_schema = {}  # No indexes
        mock_client.get_collection.return_value = mock_collection_info

        report = get_collection_index_status(mock_client, "test_collection")

        # All primary indexes should be missing
        expected_missing = {"corpus_id", "content_type", "source_id", "created_at"}
        assert set(report.missing_primary_indexes) == expected_missing
        assert report.has_tenant_index is False


class TestEnsurePrimaryIndexes:
    """Tests for ensure_primary_indexes function."""

    def test_raises_for_nonexistent_collection(self):
        """Should raise ValueError for non-existent collection."""
        mock_client = MagicMock()
        mock_client.collection_exists.return_value = False

        with pytest.raises(ValueError, match="does not exist"):
            ensure_primary_indexes(mock_client, "nonexistent")

    def test_creates_missing_indexes(self):
        """Should create missing primary indexes."""
        mock_client = MagicMock()
        mock_client.collection_exists.return_value = True

        # No existing indexes
        mock_collection_info = MagicMock()
        mock_collection_info.payload_schema = {}
        mock_client.get_collection.return_value = mock_collection_info

        created = ensure_primary_indexes(mock_client, "test_collection")

        # Should have called create_payload_index for each primary index
        assert mock_client.create_payload_index.call_count == 4
        assert len(created) == 4
        assert set(created) == {"corpus_id", "content_type", "source_id", "created_at"}

    def test_skips_existing_indexes(self):
        """Should not recreate existing indexes."""
        mock_client = MagicMock()
        mock_client.collection_exists.return_value = True

        # All indexes exist
        mock_field_info = MagicMock()
        mock_collection_info = MagicMock()
        mock_collection_info.payload_schema = {
            "corpus_id": mock_field_info,
            "content_type": mock_field_info,
            "source_id": mock_field_info,
            "created_at": mock_field_info,
        }
        mock_client.get_collection.return_value = mock_collection_info

        created = ensure_primary_indexes(mock_client, "test_collection")

        # Should not create any indexes
        assert mock_client.create_payload_index.call_count == 0
        assert created == []

    def test_idempotent(self):
        """Should be idempotent - safe to call multiple times."""
        mock_client = MagicMock()
        mock_client.collection_exists.return_value = True

        mock_collection_info = MagicMock()
        mock_collection_info.payload_schema = {}
        mock_client.get_collection.return_value = mock_collection_info

        # Call twice
        ensure_primary_indexes(mock_client, "test_collection")

        # Reset to simulate indexes now existing
        mock_field_info = MagicMock()
        mock_collection_info.payload_schema = {
            "corpus_id": mock_field_info,
            "content_type": mock_field_info,
            "source_id": mock_field_info,
            "created_at": mock_field_info,
        }

        mock_client.create_payload_index.reset_mock()
        ensure_primary_indexes(mock_client, "test_collection")

        # Second call should not create anything
        assert mock_client.create_payload_index.call_count == 0
