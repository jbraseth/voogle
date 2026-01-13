# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Fragment dataclass for representing searchable content units.

A Fragment represents the atomic unit of searchable content in Voogle,
regardless of the source type (audio, video, document, etc.). It provides
polymorphic location support for different content types.

This module also provides content-addressed ID generation for fragments,
enabling stable IDs for change detection and deduplication.

Graceful Degradation:
    Fragments include metadata for graceful UI degradation when source
    locations become unavailable:
    - location_confidence: Indicates reliability of the location
    - fallback_url: Alternative URL when primary is unavailable
    - archive_url: Archive.org snapshot URL for broken sources
    - last_known_good: Timestamp when location was last verified
"""
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class ContentType(Enum):
    """Type of content source for a fragment.

    Used to determine how to interpret location and deep_link fields.
    """

    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    SLIDE = "slide"
    TEXT = "text"
    EMAIL = "email"


class LocationConfidence(Enum):
    """Confidence level for fragment location availability.

    Used by clients to decide how to present location-dependent features.
    For example, a video player button might be disabled when confidence
    is LOW or UNAVAILABLE.

    Attributes:
        HIGH: Location verified within 24 hours, highly reliable.
        MEDIUM: Location verified within 7 days, likely available.
        LOW: Location not verified recently or had intermittent failures.
        UNAVAILABLE: Location is known to be broken or inaccessible.
    """

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class Fragment:
    """A searchable unit of content from any source type.

    Represents a fragment of text that has been indexed for semantic search,
    along with its source information and relevance score.

    Attributes:
        id: Unique identifier for this fragment.
        text: The text content of this fragment.
        score: Relevance score from semantic search (0.0 to 1.0).
        source_id: Identifier of the source containing this fragment.
        source_type: Type of content source (audio, video, document, etc.).
        location: Source-specific location data (e.g., timestamp for audio,
            page number for documents). None if not applicable.
        deep_link: URL or path to directly access this fragment in context.
            None if not available.
        metadata: Additional source-specific metadata as key-value pairs.
        location_confidence: Confidence level for location availability.
            Defaults to HIGH for newly indexed content. Used by clients
            to gracefully degrade UI when locations may be unavailable.
        fallback_url: Alternative URL to use when primary location fails.
            May point to a different CDN, mirror, or cached version.
        archive_url: Archive.org Wayback Machine URL for this content.
            Populated when original source becomes unavailable.
        last_known_good: Timestamp when location was last verified accessible.
            None if never validated. Used to calculate location_confidence.
    """

    id: str
    text: str
    score: float
    source_id: str
    source_type: ContentType
    location: Optional[Any] = None
    deep_link: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    location_confidence: LocationConfidence = LocationConfidence.HIGH
    fallback_url: Optional[str] = None
    archive_url: Optional[str] = None
    last_known_good: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validate fragment data after initialization."""
        if not self.id:
            raise ValueError("id cannot be empty")
        if not self.text:
            raise ValueError("text cannot be empty")
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(f"score must be between 0.0 and 1.0, got {self.score}")
        if not self.source_id:
            raise ValueError("source_id cannot be empty")


def generate_fragment_id(
    source_id: str,
    content: str,
    location: dict[str, Any] | None = None,
) -> str:
    """Generate a stable, content-addressed fragment ID.

    Creates a deterministic ID from the hash of source_id + content + location,
    using SHA-256 truncated to 128 bits (32 hex characters). This enables:
    - Stable IDs that survive re-indexing of unchanged content
    - Change detection by comparing old and new IDs
    - Deduplication of identical fragments

    Args:
        source_id: Identifier of the source containing this fragment.
        content: The text content of the fragment.
        location: Optional location data (dict) to include in the hash.
            If provided, it's JSON-serialized with sorted keys for determinism.

    Returns:
        A 32-character hexadecimal string (128-bit hash).

    Raises:
        ValueError: If source_id or content is empty.

    Examples:
        >>> generate_fragment_id("src1", "hello world", {})
        'a3c25f9d8b7e6c4f2a1b0d9e8c7f6a5b'  # example, actual hash will differ
        >>> generate_fragment_id("src1", "hello world", {"page": 1})
        # Different hash due to location
    """
    if not source_id:
        raise ValueError("source_id cannot be empty")
    if not content:
        raise ValueError("content cannot be empty")

    # Build the canonical string for hashing
    location_str = json.dumps(location or {}, sort_keys=True, separators=(",", ":"))
    canonical = f"{source_id}|{content}|{location_str}"

    # SHA-256, truncated to 128 bits (32 hex chars)
    full_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return full_hash[:32]


def detect_collision(
    id1: str,
    id2: str,
    source_id1: str,
    content1: str,
    location1: dict[str, Any] | None,
    source_id2: str,
    content2: str,
    location2: dict[str, Any] | None,
) -> bool:
    """Detect if two fragment IDs represent a hash collision.

    A collision occurs when two different inputs produce the same truncated hash.
    This function checks whether matching IDs came from identical or different inputs.

    Args:
        id1: First fragment ID.
        id2: Second fragment ID.
        source_id1: Source ID of first fragment.
        content1: Content of first fragment.
        location1: Location of first fragment.
        source_id2: Source ID of second fragment.
        content2: Content of second fragment.
        location2: Location of second fragment.

    Returns:
        True if IDs match but inputs differ (collision), False otherwise.
    """
    if id1 != id2:
        return False

    # IDs match - check if inputs are identical
    location_str1 = json.dumps(location1 or {}, sort_keys=True, separators=(",", ":"))
    location_str2 = json.dumps(location2 or {}, sort_keys=True, separators=(",", ":"))

    return not (
        source_id1 == source_id2
        and content1 == content2
        and location_str1 == location_str2
    )


def detect_content_change(
    old_id: str,
    new_source_id: str,
    new_content: str,
    new_location: dict[str, Any] | None = None,
) -> bool:
    """Detect if content has changed by comparing fragment IDs.

    Computes a new ID from the given inputs and compares it to the old ID.
    Different IDs indicate the content has changed.

    Args:
        old_id: The previously computed fragment ID.
        new_source_id: Source ID for the new/current content.
        new_content: The new/current content text.
        new_location: Optional location data for the new content.

    Returns:
        True if content has changed (IDs differ), False if unchanged.

    Examples:
        >>> old_id = generate_fragment_id("src1", "hello", {})
        >>> detect_content_change(old_id, "src1", "hello", {})
        False  # Content unchanged
        >>> detect_content_change(old_id, "src1", "hello world", {})
        True   # Content changed
    """
    new_id = generate_fragment_id(new_source_id, new_content, new_location)
    return old_id != new_id
