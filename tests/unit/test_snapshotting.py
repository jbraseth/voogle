# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for SnapshotService web content snapshotting."""
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from voogle.durability.snapshot import (
    RetentionPolicy,
    SnapshotConfig,
    SnapshotMetadata,
    SnapshotService,
)

pytestmark = pytest.mark.unit


class TestSnapshotMetadata:
    """Tests for SnapshotMetadata dataclass."""

    @pytest.mark.description("SnapshotMetadata stores all required fields")
    def test_metadata_creation(self) -> None:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        metadata = SnapshotMetadata(
            content_hash="abc123",
            url="https://example.com",
            captured_at=now,
            size_bytes=1024,
        )
        assert metadata.content_hash == "abc123"
        assert metadata.url == "https://example.com"
        assert metadata.captured_at == now
        assert metadata.size_bytes == 1024
        assert metadata.content_type == "text/html"
        assert metadata.expires_at is None

    @pytest.mark.description("SnapshotMetadata to_dict serializes correctly")
    def test_metadata_to_dict(self) -> None:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        expires = now + timedelta(days=30)
        metadata = SnapshotMetadata(
            content_hash="abc123",
            url="https://example.com",
            captured_at=now,
            size_bytes=1024,
            content_type="text/html",
            expires_at=expires,
            custom_metadata={"key": "value"},
        )
        result = metadata.to_dict()
        assert result["content_hash"] == "abc123"
        assert result["url"] == "https://example.com"
        assert result["captured_at"] == now.isoformat()
        assert result["expires_at"] == expires.isoformat()
        assert result["custom_metadata"] == {"key": "value"}

    @pytest.mark.description("SnapshotMetadata from_dict deserializes correctly")
    def test_metadata_from_dict(self) -> None:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        data = {
            "content_hash": "abc123",
            "url": "https://example.com",
            "captured_at": now.isoformat(),
            "size_bytes": 1024,
            "content_type": "text/html",
            "expires_at": None,
            "custom_metadata": {},
        }
        metadata = SnapshotMetadata.from_dict(data)
        assert metadata.content_hash == "abc123"
        assert metadata.url == "https://example.com"
        assert metadata.size_bytes == 1024

    @pytest.mark.description("SnapshotMetadata round-trips through dict")
    def test_metadata_round_trip(self) -> None:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        original = SnapshotMetadata(
            content_hash="xyz789",
            url="https://test.com/page",
            captured_at=now,
            size_bytes=2048,
            expires_at=now + timedelta(days=7),
            custom_metadata={"source": "test"},
        )
        data = original.to_dict()
        restored = SnapshotMetadata.from_dict(data)
        assert restored.content_hash == original.content_hash
        assert restored.url == original.url
        assert restored.size_bytes == original.size_bytes


class TestRetentionPolicy:
    """Tests for RetentionPolicy configuration."""

    @pytest.mark.description("RetentionPolicy has sensible defaults")
    def test_default_values(self) -> None:
        policy = RetentionPolicy()
        assert policy.max_age_days == 30
        assert policy.max_snapshots_per_url == 10
        assert policy.max_total_size_bytes == 0
        assert policy.cleanup_on_store is True

    @pytest.mark.description("RetentionPolicy accepts custom values")
    def test_custom_values(self) -> None:
        policy = RetentionPolicy(
            max_age_days=90,
            max_snapshots_per_url=5,
            max_total_size_bytes=1024 * 1024 * 100,
            cleanup_on_store=False,
        )
        assert policy.max_age_days == 90
        assert policy.max_snapshots_per_url == 5
        assert policy.max_total_size_bytes == 1024 * 1024 * 100
        assert policy.cleanup_on_store is False


class TestSnapshotConfig:
    """Tests for SnapshotConfig configuration."""

    @pytest.mark.description("SnapshotConfig defaults to local storage")
    def test_default_backend(self) -> None:
        config = SnapshotConfig()
        assert config.storage_backend == "local"
        assert config.storage_path is not None

    @pytest.mark.description("SnapshotConfig accepts S3 configuration")
    def test_s3_config(self) -> None:
        config = SnapshotConfig(
            storage_backend="s3",
            s3_bucket="my-bucket",
            s3_prefix="web-snapshots/",
        )
        assert config.storage_backend == "s3"
        assert config.s3_bucket == "my-bucket"
        assert config.s3_prefix == "web-snapshots/"


class TestSnapshotServiceInit:
    """Tests for SnapshotService initialization."""

    @pytest.mark.description("SnapshotService initializes with default config")
    def test_init_default(self, tmp_path: Path) -> None:
        config = SnapshotConfig(storage_path=tmp_path / "snapshots")
        service = SnapshotService(config=config)
        assert service._config.storage_backend == "local"

    @pytest.mark.description("SnapshotService creates storage directories")
    def test_init_creates_directories(self, tmp_path: Path) -> None:
        storage_path = tmp_path / "snapshots"
        config = SnapshotConfig(storage_path=storage_path)
        SnapshotService(config=config)
        assert (storage_path / "content").exists()
        assert (storage_path / "metadata").exists()

    @pytest.mark.description("SnapshotService __str__ returns readable representation")
    def test_str_representation(self, tmp_path: Path) -> None:
        config = SnapshotConfig(storage_path=tmp_path / "snapshots")
        service = SnapshotService(config=config)
        assert "SnapshotService" in str(service)
        assert "local" in str(service)


class TestContentHashing:
    """Tests for content-addressed storage hashing."""

    @pytest.mark.description("compute_content_hash returns SHA-256 hex digest")
    def test_compute_hash(self) -> None:
        content = "<html><body>Hello World</body></html>"
        result = SnapshotService.compute_content_hash(content)
        expected = hashlib.sha256(content.encode("utf-8")).hexdigest()
        assert result == expected
        assert len(result) == 64  # SHA-256 produces 64 hex characters

    @pytest.mark.description("Same content produces same hash")
    def test_hash_deterministic(self) -> None:
        content = "<html><body>Test Content</body></html>"
        hash1 = SnapshotService.compute_content_hash(content)
        hash2 = SnapshotService.compute_content_hash(content)
        assert hash1 == hash2

    @pytest.mark.description("Different content produces different hash")
    def test_hash_different_content(self) -> None:
        content1 = "<html><body>Content A</body></html>"
        content2 = "<html><body>Content B</body></html>"
        hash1 = SnapshotService.compute_content_hash(content1)
        hash2 = SnapshotService.compute_content_hash(content2)
        assert hash1 != hash2


class TestSnapshotStorage:
    """Tests for snapshot storage operations."""

    @pytest.mark.description("store saves content and returns metadata")
    def test_store_basic(self, tmp_path: Path) -> None:
        config = SnapshotConfig(
            storage_path=tmp_path / "snapshots",
            retention=RetentionPolicy(cleanup_on_store=False),
        )
        service = SnapshotService(config=config)

        content = "<html><body>Test Page</body></html>"
        url = "https://example.com/page"

        metadata = service.store(content, url)

        assert metadata.url == url
        assert metadata.size_bytes == len(content.encode("utf-8"))
        assert metadata.content_hash == SnapshotService.compute_content_hash(content)

    @pytest.mark.description("store creates sharded directory structure")
    def test_store_creates_shards(self, tmp_path: Path) -> None:
        config = SnapshotConfig(
            storage_path=tmp_path / "snapshots",
            retention=RetentionPolicy(cleanup_on_store=False),
        )
        service = SnapshotService(config=config)

        content = "<html><body>Sharded Test</body></html>"
        metadata = service.store(content, "https://example.com")

        shard = metadata.content_hash[:2]
        content_file = (
            tmp_path / "snapshots" / "content" / shard / f"{metadata.content_hash}.html"
        )
        metadata_file = (
            tmp_path / "snapshots" / "metadata" / shard / f"{metadata.content_hash}.json"
        )

        assert content_file.exists()
        assert metadata_file.exists()

    @pytest.mark.description("store records custom metadata")
    def test_store_custom_metadata(self, tmp_path: Path) -> None:
        config = SnapshotConfig(
            storage_path=tmp_path / "snapshots",
            retention=RetentionPolicy(cleanup_on_store=False),
        )
        service = SnapshotService(config=config)

        content = "<html><body>Custom</body></html>"
        custom = {"source": "crawler", "depth": 2}

        metadata = service.store(content, "https://example.com", custom_metadata=custom)

        assert metadata.custom_metadata == custom


class TestSnapshotRetrieval:
    """Tests for snapshot retrieval operations."""

    @pytest.mark.description("retrieve returns stored snapshot")
    def test_retrieve_basic(self, tmp_path: Path) -> None:
        config = SnapshotConfig(
            storage_path=tmp_path / "snapshots",
            retention=RetentionPolicy(cleanup_on_store=False),
        )
        service = SnapshotService(config=config)

        content = "<html><body>Retrieve Test</body></html>"
        url = "https://example.com/retrieve"

        metadata = service.store(content, url)
        snapshot = service.retrieve(metadata.content_hash)

        assert snapshot is not None
        assert snapshot.content == content
        assert snapshot.metadata.url == url

    @pytest.mark.description("retrieve returns None for non-existent hash")
    def test_retrieve_not_found(self, tmp_path: Path) -> None:
        config = SnapshotConfig(
            storage_path=tmp_path / "snapshots",
            retention=RetentionPolicy(cleanup_on_store=False),
        )
        service = SnapshotService(config=config)

        result = service.retrieve("nonexistent" * 8)
        assert result is None

    @pytest.mark.description("retrieve returns None for expired snapshot")
    def test_retrieve_expired(self, tmp_path: Path) -> None:
        config = SnapshotConfig(
            storage_path=tmp_path / "snapshots",
            retention=RetentionPolicy(max_age_days=1, cleanup_on_store=False),
        )
        service = SnapshotService(config=config)

        content = "<html><body>Expiring</body></html>"
        metadata = service.store(content, "https://example.com")

        # Manually set expires_at to the past
        shard = metadata.content_hash[:2]
        metadata_file = (
            tmp_path / "snapshots" / "metadata" / shard / f"{metadata.content_hash}.json"
        )
        metadata_dict = json.loads(metadata_file.read_text())
        metadata_dict["expires_at"] = (datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=1)).isoformat()
        metadata_file.write_text(json.dumps(metadata_dict))

        result = service.retrieve(metadata.content_hash)
        assert result is None


class TestSnapshotListing:
    """Tests for listing snapshots."""

    @pytest.mark.description("list_snapshots_for_url returns snapshots for URL")
    def test_list_snapshots(self, tmp_path: Path) -> None:
        config = SnapshotConfig(
            storage_path=tmp_path / "snapshots",
            retention=RetentionPolicy(cleanup_on_store=False),
        )
        service = SnapshotService(config=config)

        url = "https://example.com/list-test"
        service.store("<html>Version 1</html>", url)
        service.store("<html>Version 2</html>", url)

        snapshots = service.list_snapshots_for_url(url)
        assert len(snapshots) == 2

    @pytest.mark.description("list_snapshots_for_url returns empty for unknown URL")
    def test_list_snapshots_unknown_url(self, tmp_path: Path) -> None:
        config = SnapshotConfig(
            storage_path=tmp_path / "snapshots",
            retention=RetentionPolicy(cleanup_on_store=False),
        )
        service = SnapshotService(config=config)

        snapshots = service.list_snapshots_for_url("https://unknown.com")
        assert snapshots == []

    @pytest.mark.description("list_snapshots_for_url returns newest first")
    def test_list_snapshots_order(self, tmp_path: Path) -> None:
        config = SnapshotConfig(
            storage_path=tmp_path / "snapshots",
            retention=RetentionPolicy(cleanup_on_store=False),
        )
        service = SnapshotService(config=config)

        url = "https://example.com/order-test"
        service.store("<html>First</html>", url)
        service.store("<html>Second</html>", url)
        service.store("<html>Third</html>", url)

        snapshots = service.list_snapshots_for_url(url)
        assert len(snapshots) == 3
        # Verify newest is first (timestamps should be in descending order)
        for i in range(len(snapshots) - 1):
            assert snapshots[i].captured_at >= snapshots[i + 1].captured_at


class TestSnapshotDeletion:
    """Tests for snapshot deletion."""

    @pytest.mark.description("delete removes snapshot files")
    def test_delete_basic(self, tmp_path: Path) -> None:
        config = SnapshotConfig(
            storage_path=tmp_path / "snapshots",
            retention=RetentionPolicy(cleanup_on_store=False),
        )
        service = SnapshotService(config=config)

        content = "<html><body>Delete Me</body></html>"
        metadata = service.store(content, "https://example.com")

        assert service.exists(metadata.content_hash)

        result = service.delete(metadata.content_hash)
        assert result is True
        assert not service.exists(metadata.content_hash)

    @pytest.mark.description("delete returns False for non-existent snapshot")
    def test_delete_not_found(self, tmp_path: Path) -> None:
        config = SnapshotConfig(
            storage_path=tmp_path / "snapshots",
            retention=RetentionPolicy(cleanup_on_store=False),
        )
        service = SnapshotService(config=config)

        result = service.delete("nonexistent" * 8)
        assert result is False


class TestRetentionEnforcement:
    """Tests for retention policy enforcement."""

    @pytest.mark.description("max_snapshots_per_url limits stored snapshots")
    def test_max_snapshots_per_url(self, tmp_path: Path) -> None:
        config = SnapshotConfig(
            storage_path=tmp_path / "snapshots",
            retention=RetentionPolicy(max_snapshots_per_url=2, cleanup_on_store=False),
        )
        service = SnapshotService(config=config)

        url = "https://example.com/retention-test"
        service.store("<html>Version 1</html>", url)
        service.store("<html>Version 2</html>", url)
        service.store("<html>Version 3</html>", url)

        snapshots = service.list_snapshots_for_url(url)
        assert len(snapshots) == 2

    @pytest.mark.description("cleanup removes expired snapshots")
    def test_cleanup_expired(self, tmp_path: Path) -> None:
        config = SnapshotConfig(
            storage_path=tmp_path / "snapshots",
            retention=RetentionPolicy(max_age_days=1, cleanup_on_store=False),
        )
        service = SnapshotService(config=config)

        content = "<html><body>Old Content</body></html>"
        metadata = service.store(content, "https://example.com")

        # Manually expire the snapshot
        shard = metadata.content_hash[:2]
        metadata_file = (
            tmp_path / "snapshots" / "metadata" / shard / f"{metadata.content_hash}.json"
        )
        metadata_dict = json.loads(metadata_file.read_text())
        metadata_dict["expires_at"] = (datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=1)).isoformat()
        metadata_file.write_text(json.dumps(metadata_dict))

        deleted_count = service.cleanup()
        assert deleted_count == 1
        assert not service.exists(metadata.content_hash)


class TestStorageStats:
    """Tests for storage statistics."""

    @pytest.mark.description("get_storage_stats returns correct statistics")
    def test_storage_stats(self, tmp_path: Path) -> None:
        config = SnapshotConfig(
            storage_path=tmp_path / "snapshots",
            retention=RetentionPolicy(cleanup_on_store=False),
        )
        service = SnapshotService(config=config)

        content1 = "<html>Content 1</html>"
        content2 = "<html>Content 2 with more data</html>"
        service.store(content1, "https://example.com/1")
        service.store(content2, "https://example.com/2")

        stats = service.get_storage_stats()
        assert stats["backend"] == "local"
        assert stats["snapshot_count"] == 2
        assert stats["total_size_bytes"] > 0


class TestExistsAndGetMetadata:
    """Tests for exists and get_metadata methods."""

    @pytest.mark.description("exists returns True for stored snapshot")
    def test_exists_true(self, tmp_path: Path) -> None:
        config = SnapshotConfig(
            storage_path=tmp_path / "snapshots",
            retention=RetentionPolicy(cleanup_on_store=False),
        )
        service = SnapshotService(config=config)

        content = "<html>Exists Test</html>"
        metadata = service.store(content, "https://example.com")

        assert service.exists(metadata.content_hash) is True

    @pytest.mark.description("exists returns False for missing snapshot")
    def test_exists_false(self, tmp_path: Path) -> None:
        config = SnapshotConfig(
            storage_path=tmp_path / "snapshots",
            retention=RetentionPolicy(cleanup_on_store=False),
        )
        service = SnapshotService(config=config)

        assert service.exists("nonexistent" * 8) is False

    @pytest.mark.description("get_metadata returns metadata without content")
    def test_get_metadata(self, tmp_path: Path) -> None:
        config = SnapshotConfig(
            storage_path=tmp_path / "snapshots",
            retention=RetentionPolicy(cleanup_on_store=False),
        )
        service = SnapshotService(config=config)

        content = "<html>Metadata Test</html>"
        stored_metadata = service.store(content, "https://example.com/meta")

        retrieved_metadata = service.get_metadata(stored_metadata.content_hash)
        assert retrieved_metadata is not None
        assert retrieved_metadata.content_hash == stored_metadata.content_hash
        assert retrieved_metadata.url == stored_metadata.url

    @pytest.mark.description("get_metadata returns None for missing snapshot")
    def test_get_metadata_not_found(self, tmp_path: Path) -> None:
        config = SnapshotConfig(
            storage_path=tmp_path / "snapshots",
            retention=RetentionPolicy(cleanup_on_store=False),
        )
        service = SnapshotService(config=config)

        result = service.get_metadata("nonexistent" * 8)
        assert result is None
