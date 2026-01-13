# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Web content snapshotting service for durability.

This module provides a SnapshotService for capturing and storing web content
snapshots with content-addressed storage, timestamp recording, and configurable
retention policies.

Features:
- HTML snapshot storage (local filesystem or S3-compatible)
- Content-addressed keys using SHA-256 hashing
- Timestamp recording for version tracking
- Configurable retention policies
- Retrieval API for accessing stored snapshots
"""
from __future__ import annotations

import hashlib
import json
import logging
import pathlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from voogle import settings

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    """Get current UTC datetime (extracted for testability)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


@dataclass(frozen=True)
class SnapshotMetadata:
    """Metadata for a stored snapshot.

    Attributes:
        content_hash: SHA-256 hash of the content (content-addressed key).
        url: Original URL of the web content.
        captured_at: Timestamp when the snapshot was captured.
        size_bytes: Size of the stored content in bytes.
        content_type: MIME type of the content.
        expires_at: Optional expiration timestamp based on retention policy.
        custom_metadata: Optional additional metadata.
    """

    content_hash: str
    url: str
    captured_at: datetime
    size_bytes: int
    content_type: str = "text/html"
    expires_at: datetime | None = None
    custom_metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert metadata to a dictionary for JSON serialization."""
        return {
            "content_hash": self.content_hash,
            "url": self.url,
            "captured_at": self.captured_at.isoformat(),
            "size_bytes": self.size_bytes,
            "content_type": self.content_type,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "custom_metadata": self.custom_metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SnapshotMetadata:
        """Create metadata from a dictionary."""
        return cls(
            content_hash=data["content_hash"],
            url=data["url"],
            captured_at=datetime.fromisoformat(data["captured_at"]),
            size_bytes=data["size_bytes"],
            content_type=data.get("content_type", "text/html"),
            expires_at=(
                datetime.fromisoformat(data["expires_at"])
                if data.get("expires_at")
                else None
            ),
            custom_metadata=data.get("custom_metadata", {}),
        )


@dataclass
class RetentionPolicy:
    """Configuration for snapshot retention.

    Attributes:
        max_age_days: Maximum age of snapshots before expiration (0 = no limit).
        max_snapshots_per_url: Maximum number of snapshots to keep per URL (0 = no limit).
        max_total_size_bytes: Maximum total storage size (0 = no limit).
        cleanup_on_store: Whether to run cleanup automatically on each store.
    """

    max_age_days: int = 30
    max_snapshots_per_url: int = 10
    max_total_size_bytes: int = 0
    cleanup_on_store: bool = True


@dataclass
class SnapshotConfig:
    """Configuration for the SnapshotService.

    Attributes:
        storage_backend: Storage backend type ("local" or "s3").
        storage_path: Path for local storage.
        s3_bucket: S3 bucket name (if using S3).
        s3_prefix: S3 key prefix for snapshots.
        retention: Retention policy configuration.
    """

    storage_backend: str = "local"
    storage_path: pathlib.Path | None = None
    s3_bucket: str | None = None
    s3_prefix: str = "snapshots/"
    retention: RetentionPolicy = field(default_factory=RetentionPolicy)

    def __post_init__(self) -> None:
        """Set default storage path if not provided."""
        if self.storage_path is None:
            self.storage_path = settings.settings.data_dir / "snapshots"


@dataclass(frozen=True)
class Snapshot:
    """A web content snapshot.

    Attributes:
        content: The HTML content.
        metadata: Snapshot metadata.
    """

    content: str
    metadata: SnapshotMetadata


class SnapshotService:
    """Service for capturing and storing web content snapshots.

    Provides content-addressed storage for HTML snapshots with support
    for local filesystem or S3-compatible storage backends.

    Example:
        >>> service = SnapshotService()
        >>> metadata = service.store("<html>...</html>", "https://example.com")
        >>> snapshot = service.retrieve(metadata.content_hash)
        >>> if snapshot:
        ...     print(snapshot.content)
    """

    def __init__(self, config: SnapshotConfig | None = None) -> None:
        """Initialize the snapshot service.

        Args:
            config: Optional configuration. Uses defaults if not provided.
        """
        self._config = config or SnapshotConfig()
        self._s3_client: Any = None
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        """Ensure storage backend is properly initialized."""
        if self._config.storage_backend == "local":
            if self._config.storage_path is not None:
                self._config.storage_path.mkdir(parents=True, exist_ok=True)
                # Create subdirectories for organization
                (self._config.storage_path / "content").mkdir(exist_ok=True)
                (self._config.storage_path / "metadata").mkdir(exist_ok=True)

    @property
    def s3_client(self) -> Any:
        """Get or lazily initialize the S3 client."""
        if self._s3_client is None and self._config.storage_backend == "s3":
            try:
                import boto3
                self._s3_client = boto3.client("s3")
            except ImportError:
                raise ImportError(
                    "boto3 is required for S3 storage. Install with: pip install boto3"
                )
        return self._s3_client

    def __str__(self) -> str:
        """Return string representation of the service."""
        return f"SnapshotService(backend={self._config.storage_backend!r})"

    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (
            f"SnapshotService("
            f"config={self._config!r})"
        )

    @staticmethod
    def compute_content_hash(content: str) -> str:
        """Compute SHA-256 hash for content-addressed storage.

        Args:
            content: The content to hash.

        Returns:
            Hexadecimal SHA-256 hash string.
        """
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def store(
        self,
        content: str,
        url: str,
        content_type: str = "text/html",
        custom_metadata: dict[str, Any] | None = None,
    ) -> SnapshotMetadata:
        """Store a web content snapshot.

        Args:
            content: The HTML content to store.
            url: Original URL of the content.
            content_type: MIME type of the content.
            custom_metadata: Optional additional metadata.

        Returns:
            Metadata for the stored snapshot.
        """
        content_hash = self.compute_content_hash(content)
        captured_at = _utcnow()
        size_bytes = len(content.encode("utf-8"))

        # Calculate expiration based on retention policy
        expires_at = None
        if self._config.retention.max_age_days > 0:
            expires_at = captured_at + timedelta(days=self._config.retention.max_age_days)

        metadata = SnapshotMetadata(
            content_hash=content_hash,
            url=url,
            captured_at=captured_at,
            size_bytes=size_bytes,
            content_type=content_type,
            expires_at=expires_at,
            custom_metadata=custom_metadata or {},
        )

        if self._config.storage_backend == "local":
            self._store_local(content, metadata)
        else:
            self._store_s3(content, metadata)

        # Run cleanup if configured
        if self._config.retention.cleanup_on_store:
            self._cleanup_expired()

        logger.info(f"Stored snapshot {content_hash[:12]} for {url}")
        return metadata

    def _store_local(self, content: str, metadata: SnapshotMetadata) -> None:
        """Store content to local filesystem.

        Args:
            content: The content to store.
            metadata: Snapshot metadata.
        """
        if self._config.storage_path is None:
            raise ValueError("Storage path not configured")

        # Use first 2 chars of hash for directory sharding
        shard = metadata.content_hash[:2]
        content_dir = self._config.storage_path / "content" / shard
        content_dir.mkdir(parents=True, exist_ok=True)

        # Store content
        content_file = content_dir / f"{metadata.content_hash}.html"
        content_file.write_text(content, encoding="utf-8")

        # Store metadata
        metadata_dir = self._config.storage_path / "metadata" / shard
        metadata_dir.mkdir(parents=True, exist_ok=True)
        metadata_file = metadata_dir / f"{metadata.content_hash}.json"
        metadata_file.write_text(
            json.dumps(metadata.to_dict(), indent=2), encoding="utf-8"
        )

        # Maintain URL index for quick lookups
        self._update_url_index(metadata)

    def _store_s3(self, content: str, metadata: SnapshotMetadata) -> None:
        """Store content to S3.

        Args:
            content: The content to store.
            metadata: Snapshot metadata.
        """
        if self._config.s3_bucket is None:
            raise ValueError("S3 bucket not configured")

        prefix = self._config.s3_prefix
        content_key = f"{prefix}content/{metadata.content_hash[:2]}/{metadata.content_hash}.html"
        metadata_key = f"{prefix}metadata/{metadata.content_hash[:2]}/{metadata.content_hash}.json"

        # Store content
        self.s3_client.put_object(
            Bucket=self._config.s3_bucket,
            Key=content_key,
            Body=content.encode("utf-8"),
            ContentType=metadata.content_type,
        )

        # Store metadata
        self.s3_client.put_object(
            Bucket=self._config.s3_bucket,
            Key=metadata_key,
            Body=json.dumps(metadata.to_dict()).encode("utf-8"),
            ContentType="application/json",
        )

    def _update_url_index(self, metadata: SnapshotMetadata) -> None:
        """Update the URL index for quick lookups.

        Args:
            metadata: Snapshot metadata to index.
        """
        if self._config.storage_path is None:
            return

        index_dir = self._config.storage_path / "index"
        index_dir.mkdir(parents=True, exist_ok=True)

        # Use URL hash as filename to avoid filesystem path issues
        url_hash = hashlib.sha256(metadata.url.encode("utf-8")).hexdigest()[:16]
        index_file = index_dir / f"{url_hash}.json"

        # Load existing index or create new
        index_data: dict[str, list[dict[str, Any]]] = {"snapshots": []}
        if index_file.exists():
            index_data = json.loads(index_file.read_text(encoding="utf-8"))

        # Add new snapshot entry
        index_data["snapshots"].append({
            "content_hash": metadata.content_hash,
            "captured_at": metadata.captured_at.isoformat(),
        })

        # Enforce max_snapshots_per_url limit
        max_per_url = self._config.retention.max_snapshots_per_url
        if max_per_url > 0 and len(index_data["snapshots"]) > max_per_url:
            # Sort by captured_at and keep only the most recent
            index_data["snapshots"].sort(key=lambda x: x["captured_at"], reverse=True)
            removed = index_data["snapshots"][max_per_url:]
            index_data["snapshots"] = index_data["snapshots"][:max_per_url]
            # Delete old snapshots
            for entry in removed:
                self._delete_snapshot(entry["content_hash"])

        index_file.write_text(json.dumps(index_data, indent=2), encoding="utf-8")

    def retrieve(self, content_hash: str) -> Snapshot | None:
        """Retrieve a snapshot by its content hash.

        Args:
            content_hash: The SHA-256 hash of the content.

        Returns:
            The Snapshot if found, None otherwise.
        """
        if self._config.storage_backend == "local":
            return self._retrieve_local(content_hash)
        return self._retrieve_s3(content_hash)

    def _retrieve_local(self, content_hash: str) -> Snapshot | None:
        """Retrieve content from local filesystem.

        Args:
            content_hash: The content hash to retrieve.

        Returns:
            Snapshot if found, None otherwise.
        """
        if self._config.storage_path is None:
            return None

        shard = content_hash[:2]
        content_file = (
            self._config.storage_path / "content" / shard / f"{content_hash}.html"
        )
        metadata_file = (
            self._config.storage_path / "metadata" / shard / f"{content_hash}.json"
        )

        if not content_file.exists() or not metadata_file.exists():
            return None

        content = content_file.read_text(encoding="utf-8")
        metadata_dict = json.loads(metadata_file.read_text(encoding="utf-8"))
        metadata = SnapshotMetadata.from_dict(metadata_dict)

        # Check if snapshot has expired
        if metadata.expires_at and metadata.expires_at < _utcnow():
            logger.debug(f"Snapshot {content_hash[:12]} has expired")
            return None

        return Snapshot(content=content, metadata=metadata)

    def _retrieve_s3(self, content_hash: str) -> Snapshot | None:
        """Retrieve content from S3.

        Args:
            content_hash: The content hash to retrieve.

        Returns:
            Snapshot if found, None otherwise.
        """
        if self._config.s3_bucket is None:
            return None

        prefix = self._config.s3_prefix
        content_key = f"{prefix}content/{content_hash[:2]}/{content_hash}.html"
        metadata_key = f"{prefix}metadata/{content_hash[:2]}/{content_hash}.json"

        try:
            content_response = self.s3_client.get_object(
                Bucket=self._config.s3_bucket, Key=content_key
            )
            metadata_response = self.s3_client.get_object(
                Bucket=self._config.s3_bucket, Key=metadata_key
            )

            content = content_response["Body"].read().decode("utf-8")
            metadata_dict = json.loads(metadata_response["Body"].read().decode("utf-8"))
            metadata = SnapshotMetadata.from_dict(metadata_dict)

            # Check expiration
            if metadata.expires_at and metadata.expires_at < _utcnow():
                return None

            return Snapshot(content=content, metadata=metadata)
        except Exception as e:
            logger.debug(f"Failed to retrieve snapshot {content_hash[:12]}: {e}")
            return None

    def list_snapshots_for_url(self, url: str) -> list[SnapshotMetadata]:
        """List all snapshots for a given URL.

        Args:
            url: The URL to list snapshots for.

        Returns:
            List of SnapshotMetadata objects, ordered by capture time (newest first).
        """
        if self._config.storage_backend == "local":
            return self._list_snapshots_local(url)
        return self._list_snapshots_s3(url)

    def _list_snapshots_local(self, url: str) -> list[SnapshotMetadata]:
        """List snapshots from local storage.

        Args:
            url: The URL to list snapshots for.

        Returns:
            List of SnapshotMetadata objects.
        """
        if self._config.storage_path is None:
            return []

        url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
        index_file = self._config.storage_path / "index" / f"{url_hash}.json"

        if not index_file.exists():
            return []

        index_data = json.loads(index_file.read_text(encoding="utf-8"))
        snapshots = []

        for entry in index_data.get("snapshots", []):
            content_hash = entry["content_hash"]
            shard = content_hash[:2]
            metadata_file = (
                self._config.storage_path / "metadata" / shard / f"{content_hash}.json"
            )
            if metadata_file.exists():
                metadata_dict = json.loads(metadata_file.read_text(encoding="utf-8"))
                metadata = SnapshotMetadata.from_dict(metadata_dict)
                # Skip expired snapshots
                if metadata.expires_at is None or metadata.expires_at >= _utcnow():
                    snapshots.append(metadata)

        # Sort by captured_at descending (newest first)
        snapshots.sort(key=lambda m: m.captured_at, reverse=True)
        return snapshots

    def _list_snapshots_s3(self, url: str) -> list[SnapshotMetadata]:  # noqa: ARG002
        """List snapshots from S3 storage.

        Args:
            url: The URL to list snapshots for.

        Returns:
            List of SnapshotMetadata objects.
        """
        # S3 implementation would require scanning or maintaining an index
        # For now, return empty list (can be extended with DynamoDB or similar)
        logger.warning("S3 snapshot listing not yet implemented")
        return []

    def delete(self, content_hash: str) -> bool:
        """Delete a snapshot by its content hash.

        Args:
            content_hash: The SHA-256 hash of the content to delete.

        Returns:
            True if deleted, False if not found.
        """
        if self._config.storage_backend == "local":
            return self._delete_snapshot(content_hash)
        return self._delete_s3(content_hash)

    def _delete_snapshot(self, content_hash: str) -> bool:
        """Delete content from local filesystem.

        Args:
            content_hash: The content hash to delete.

        Returns:
            True if deleted, False if not found.
        """
        if self._config.storage_path is None:
            return False

        shard = content_hash[:2]
        content_file = (
            self._config.storage_path / "content" / shard / f"{content_hash}.html"
        )
        metadata_file = (
            self._config.storage_path / "metadata" / shard / f"{content_hash}.json"
        )

        deleted = False
        if content_file.exists():
            content_file.unlink()
            deleted = True
        if metadata_file.exists():
            metadata_file.unlink()
            deleted = True

        if deleted:
            logger.debug(f"Deleted snapshot {content_hash[:12]}")

        return deleted

    def _delete_s3(self, content_hash: str) -> bool:
        """Delete content from S3.

        Args:
            content_hash: The content hash to delete.

        Returns:
            True if deleted, False otherwise.
        """
        if self._config.s3_bucket is None:
            return False

        prefix = self._config.s3_prefix
        content_key = f"{prefix}content/{content_hash[:2]}/{content_hash}.html"
        metadata_key = f"{prefix}metadata/{content_hash[:2]}/{content_hash}.json"

        try:
            self.s3_client.delete_objects(
                Bucket=self._config.s3_bucket,
                Delete={"Objects": [{"Key": content_key}, {"Key": metadata_key}]},
            )
            return True
        except Exception as e:
            logger.error(f"Failed to delete S3 snapshot {content_hash[:12]}: {e}")
            return False

    def _cleanup_expired(self) -> int:
        """Clean up expired snapshots.

        Returns:
            Number of snapshots deleted.
        """
        if self._config.storage_backend != "local":
            return 0

        if self._config.storage_path is None:
            return 0

        deleted_count = 0
        now = _utcnow()
        metadata_dir = self._config.storage_path / "metadata"

        if not metadata_dir.exists():
            return 0

        for shard_dir in metadata_dir.iterdir():
            if not shard_dir.is_dir():
                continue
            for metadata_file in shard_dir.glob("*.json"):
                try:
                    metadata_dict = json.loads(metadata_file.read_text(encoding="utf-8"))
                    expires_at_str = metadata_dict.get("expires_at")
                    if expires_at_str:
                        expires_at = datetime.fromisoformat(expires_at_str)
                        if expires_at < now:
                            content_hash = metadata_dict["content_hash"]
                            if self._delete_snapshot(content_hash):
                                deleted_count += 1
                except Exception as e:
                    logger.warning(f"Error processing {metadata_file}: {e}")

        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} expired snapshots")

        return deleted_count

    def cleanup(self) -> int:
        """Manually trigger cleanup of expired snapshots.

        Returns:
            Number of snapshots deleted.
        """
        return self._cleanup_expired()

    def get_storage_stats(self) -> dict[str, Any]:
        """Get storage statistics.

        Returns:
            Dictionary with storage statistics.
        """
        if self._config.storage_backend != "local":
            return {"backend": "s3", "stats_not_available": True}

        if self._config.storage_path is None:
            return {"backend": "local", "error": "no storage path"}

        total_size = 0
        snapshot_count = 0
        content_dir = self._config.storage_path / "content"

        if content_dir.exists():
            for shard_dir in content_dir.iterdir():
                if shard_dir.is_dir():
                    for content_file in shard_dir.glob("*.html"):
                        total_size += content_file.stat().st_size
                        snapshot_count += 1

        return {
            "backend": "local",
            "storage_path": str(self._config.storage_path),
            "snapshot_count": snapshot_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
        }

    def exists(self, content_hash: str) -> bool:
        """Check if a snapshot exists.

        Args:
            content_hash: The SHA-256 hash of the content.

        Returns:
            True if the snapshot exists, False otherwise.
        """
        if self._config.storage_backend == "local":
            if self._config.storage_path is None:
                return False
            shard = content_hash[:2]
            content_file = (
                self._config.storage_path / "content" / shard / f"{content_hash}.html"
            )
            return content_file.exists()
        else:
            # For S3, try to head the object
            if self._config.s3_bucket is None:
                return False
            prefix = self._config.s3_prefix
            content_key = f"{prefix}content/{content_hash[:2]}/{content_hash}.html"
            try:
                self.s3_client.head_object(
                    Bucket=self._config.s3_bucket, Key=content_key
                )
                return True
            except Exception:
                return False

    def get_metadata(self, content_hash: str) -> SnapshotMetadata | None:
        """Get metadata for a snapshot without retrieving content.

        Args:
            content_hash: The SHA-256 hash of the content.

        Returns:
            SnapshotMetadata if found, None otherwise.
        """
        if self._config.storage_backend == "local":
            if self._config.storage_path is None:
                return None
            shard = content_hash[:2]
            metadata_file = (
                self._config.storage_path / "metadata" / shard / f"{content_hash}.json"
            )
            if not metadata_file.exists():
                return None
            metadata_dict = json.loads(metadata_file.read_text(encoding="utf-8"))
            return SnapshotMetadata.from_dict(metadata_dict)
        else:
            # S3 retrieval
            if self._config.s3_bucket is None:
                return None
            prefix = self._config.s3_prefix
            metadata_key = f"{prefix}metadata/{content_hash[:2]}/{content_hash}.json"
            try:
                response = self.s3_client.get_object(
                    Bucket=self._config.s3_bucket, Key=metadata_key
                )
                metadata_dict = json.loads(response["Body"].read().decode("utf-8"))
                return SnapshotMetadata.from_dict(metadata_dict)
            except Exception:
                return None
