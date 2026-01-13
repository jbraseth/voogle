# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Context expansion service for retrieving surrounding fragments.

Provides the ContextExpander class for expanding search results with
surrounding context. Supports:
- Before/after fragment retrieval
- Token-limited expansion windows
- Document boundary respect
- Parent-child traversal for hierarchical content
- Efficient ordering queries
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

from qdrant_client import models

from voogle import vector

logger = logging.getLogger(__name__)


# Default token estimation: average ~4 characters per token (common heuristic)
CHARS_PER_TOKEN = 4


@dataclass(frozen=True)
class ExpandedFragment:
    """A fragment with its expanded context.

    Attributes:
        id: Unique identifier of the fragment.
        text: The original text content of the fragment.
        source_id: Identifier of the source document.
        start_time: Start time in seconds (for audio/video).
        end_time: End time in seconds (for audio/video).
        before_context: List of fragments before this one.
        after_context: List of fragments after this one.
        parent_id: Optional parent fragment ID (for hierarchical content).
    """

    id: str
    text: str
    source_id: str
    start_time: float | None = None
    end_time: float | None = None
    before_context: list[ContextFragment] = field(default_factory=list)
    after_context: list[ContextFragment] = field(default_factory=list)
    parent_id: str | None = None


@dataclass(frozen=True)
class ContextFragment:
    """A fragment used as context (before/after or parent/child).

    Attributes:
        id: Unique identifier of the fragment.
        text: The text content of the fragment.
        start_time: Start time in seconds (for audio/video).
        end_time: End time in seconds (for audio/video).
        token_count: Estimated token count for this fragment.
    """

    id: str
    text: str
    start_time: float | None = None
    end_time: float | None = None
    token_count: int = 0


@dataclass
class ExpansionConfig:
    """Configuration for context expansion.

    Attributes:
        max_tokens_before: Maximum tokens to include before the fragment.
        max_tokens_after: Maximum tokens to include after the fragment.
        max_fragments_before: Maximum number of fragments before.
        max_fragments_after: Maximum number of fragments after.
        respect_boundaries: Whether to stop at document boundaries.
        include_parent: Whether to include parent fragment if available.
        collection_name: Optional collection name override.
    """

    max_tokens_before: int = 500
    max_tokens_after: int = 500
    max_fragments_before: int = 5
    max_fragments_after: int = 5
    respect_boundaries: bool = True
    include_parent: bool = False
    collection_name: str | None = None


class ContextExpander:
    """Service for expanding fragments with surrounding context.

    Retrieves surrounding fragments from the vector database and builds
    expanded context windows while respecting token limits and document
    boundaries.
    """

    def __init__(
        self,
        qdrant_client: vector.qdrant_client.QdrantClient | None = None,
        default_collection: str = "vectordb",
    ) -> None:
        """Initialize the context expander.

        Args:
            qdrant_client: Qdrant client for vector database operations.
                If None, uses the configured client from settings.
            default_collection: Default collection name to use.
        """
        self._qdrant_client = qdrant_client
        self._default_collection = default_collection

    @property
    def qdrant_client(self) -> vector.qdrant_client.QdrantClient:
        """Get or lazily initialize the Qdrant client."""
        if self._qdrant_client is None:
            self._qdrant_client = vector.get_configured_client()
        return self._qdrant_client

    def __str__(self) -> str:
        """Return string representation of the expander."""
        return f"ContextExpander(collection={self._default_collection!r})"

    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (
            f"ContextExpander("
            f"qdrant_client={self._qdrant_client!r}, "
            f"default_collection={self._default_collection!r})"
        )

    def estimate_tokens(self, text: str) -> int:
        """Estimate the number of tokens in a text string.

        Uses a simple character-based heuristic. For more accurate
        estimation, consider using a tokenizer.

        Args:
            text: The text to estimate tokens for.

        Returns:
            Estimated token count.
        """
        return max(1, len(text) // CHARS_PER_TOKEN)

    def expand(
        self,
        fragment_id: str,
        source_id: str,
        config: ExpansionConfig | None = None,
    ) -> ExpandedFragment | None:
        """Expand a fragment with surrounding context.

        Args:
            fragment_id: The ID of the fragment to expand.
            source_id: The source document ID for boundary detection.
            config: Optional expansion configuration.

        Returns:
            ExpandedFragment with context, or None if fragment not found.
        """
        if config is None:
            config = ExpansionConfig()

        collection_name = config.collection_name or self._default_collection

        # Retrieve the original fragment
        original = self._get_fragment(fragment_id, collection_name)
        if original is None:
            logger.warning(f"Fragment {fragment_id} not found in {collection_name}")
            return None

        # Get before context
        before_context = self._get_before_context(
            source_id=source_id,
            reference_time=original.get("start_time") or original.get("start_secs"),
            max_tokens=config.max_tokens_before,
            max_fragments=config.max_fragments_before,
            collection_name=collection_name,
            respect_boundaries=config.respect_boundaries,
        )

        # Get after context
        after_context = self._get_after_context(
            source_id=source_id,
            reference_time=original.get("end_time") or original.get("end_secs"),
            max_tokens=config.max_tokens_after,
            max_fragments=config.max_fragments_after,
            collection_name=collection_name,
            respect_boundaries=config.respect_boundaries,
        )

        # Get parent if requested
        parent_id = None
        if config.include_parent:
            parent_id = original.get("parent_id")

        return ExpandedFragment(
            id=fragment_id,
            text=original.get("text", ""),
            source_id=source_id,
            start_time=original.get("start_time") or original.get("start_secs"),
            end_time=original.get("end_time") or original.get("end_secs"),
            before_context=before_context,
            after_context=after_context,
            parent_id=parent_id,
        )

    def expand_batch(
        self,
        fragment_ids: list[str],
        source_ids: list[str],
        config: ExpansionConfig | None = None,
    ) -> list[ExpandedFragment | None]:
        """Expand multiple fragments with surrounding context.

        Args:
            fragment_ids: List of fragment IDs to expand.
            source_ids: List of source document IDs (parallel to fragment_ids).
            config: Optional expansion configuration.

        Returns:
            List of ExpandedFragment objects (None for fragments not found).
        """
        if len(fragment_ids) != len(source_ids):
            raise ValueError(
                f"fragment_ids and source_ids must have same length: "
                f"{len(fragment_ids)} != {len(source_ids)}"
            )

        return [
            self.expand(frag_id, src_id, config)
            for frag_id, src_id in zip(fragment_ids, source_ids)
        ]

    def get_parent(
        self,
        fragment_id: str,
        collection_name: str | None = None,
    ) -> ContextFragment | None:
        """Get the parent fragment for hierarchical content.

        Args:
            fragment_id: The ID of the child fragment.
            collection_name: Optional collection name override.

        Returns:
            Parent ContextFragment or None if no parent exists.
        """
        coll = collection_name or self._default_collection
        fragment = self._get_fragment(fragment_id, coll)
        if fragment is None:
            return None

        parent_id = fragment.get("parent_id")
        if parent_id is None:
            return None

        parent = self._get_fragment(parent_id, coll)
        if parent is None:
            return None

        text = parent.get("text", "")
        return ContextFragment(
            id=parent_id,
            text=text,
            start_time=parent.get("start_time") or parent.get("start_secs"),
            end_time=parent.get("end_time") or parent.get("end_secs"),
            token_count=self.estimate_tokens(text),
        )

    def get_children(
        self,
        parent_id: str,
        collection_name: str | None = None,
        max_children: int = 10,
    ) -> list[ContextFragment]:
        """Get child fragments for hierarchical content.

        Args:
            parent_id: The ID of the parent fragment.
            collection_name: Optional collection name override.
            max_children: Maximum number of children to return.

        Returns:
            List of child ContextFragment objects ordered by position.
        """
        coll = collection_name or self._default_collection

        try:
            # Query for fragments with this parent_id
            results = self.qdrant_client.scroll(
                collection_name=coll,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="parent_id",
                            match=models.MatchValue(value=parent_id),
                        )
                    ]
                ),
                limit=max_children,
                with_payload=True,
            )

            points = results[0] if results else []
            children = []
            for point in points:
                payload = point.payload or {}
                text = payload.get("text", "")
                children.append(
                    ContextFragment(
                        id=str(point.id),
                        text=text,
                        start_time=payload.get("start_time") or payload.get("start_secs"),
                        end_time=payload.get("end_time") or payload.get("end_secs"),
                        token_count=self.estimate_tokens(text),
                    )
                )

            # Sort by start_time for proper ordering
            children.sort(key=lambda x: x.start_time or 0)
            return children

        except Exception as e:
            logger.error(f"Error fetching children for {parent_id}: {e}")
            return []

    def _get_fragment(
        self,
        fragment_id: str,
        collection_name: str,
    ) -> dict | None:
        """Retrieve a single fragment's payload by ID.

        Args:
            fragment_id: The fragment ID to retrieve.
            collection_name: The collection to query.

        Returns:
            Fragment payload dict or None if not found.
        """
        try:
            results = self.qdrant_client.retrieve(
                collection_name=collection_name,
                ids=[fragment_id],
                with_payload=True,
            )
            if results:
                return results[0].payload or {}
            return None
        except Exception as e:
            logger.error(f"Error retrieving fragment {fragment_id}: {e}")
            return None

    def _get_before_context(
        self,
        source_id: str,
        reference_time: float | None,
        max_tokens: int,
        max_fragments: int,
        collection_name: str,
        respect_boundaries: bool,
    ) -> list[ContextFragment]:
        """Get fragments before the reference time.

        Args:
            source_id: Source document ID for filtering.
            reference_time: Time to search before (exclusive).
            max_tokens: Maximum total tokens to include.
            max_fragments: Maximum number of fragments.
            collection_name: Collection to query.
            respect_boundaries: Whether to stop at document boundaries.

        Returns:
            List of ContextFragment objects in chronological order.
        """
        if reference_time is None:
            return []

        # Build filter for same source, before reference time
        filter_conditions: list[models.Condition] = self._build_source_filter(
            source_id, respect_boundaries
        )
        filter_conditions.append(
            models.FieldCondition(
                key="end_time",
                range=models.Range(lt=reference_time),
            )
        )

        try:
            # Get fragments before, ordered by end_time descending (closest first)
            results = self.qdrant_client.scroll(
                collection_name=collection_name,
                scroll_filter=models.Filter(must=filter_conditions),
                limit=max_fragments * 2,  # Fetch extra in case some are filtered
                with_payload=True,
                order_by=models.OrderBy(
                    key="end_time",
                    direction=models.Direction.DESC,
                ),
            )

            points = results[0] if results else []
            return self._collect_fragments_with_token_limit(
                points, max_tokens, max_fragments, reverse=True
            )

        except Exception as e:
            logger.warning(f"Error fetching before context: {e}, trying fallback")
            # Fallback: try with start_secs for legacy schema
            return self._get_before_context_legacy(
                source_id, reference_time, max_tokens, max_fragments, collection_name
            )

    def _get_before_context_legacy(
        self,
        source_id: str,
        reference_time: float,
        max_tokens: int,
        max_fragments: int,
        collection_name: str,
    ) -> list[ContextFragment]:
        """Fallback for legacy schema using start_secs/end_secs."""
        try:
            # Try with legacy field names
            filter_conditions: list[models.Condition] = [
                models.FieldCondition(
                    key="episode",
                    match=models.MatchValue(value=int(source_id)),
                ),
                models.FieldCondition(
                    key="end_secs",
                    range=models.Range(lt=int(reference_time)),
                ),
            ]

            results = self.qdrant_client.scroll(
                collection_name=collection_name,
                scroll_filter=models.Filter(must=filter_conditions),
                limit=max_fragments * 2,
                with_payload=True,
            )

            points = results[0] if results else []
            # Sort manually since legacy may not support order_by
            points.sort(
                key=lambda p: p.payload.get("end_secs", 0) if p.payload else 0,
                reverse=True,
            )
            return self._collect_fragments_with_token_limit(
                points, max_tokens, max_fragments, reverse=True
            )

        except Exception as e:
            logger.error(f"Error in legacy before context: {e}")
            return []

    def _get_after_context(
        self,
        source_id: str,
        reference_time: float | None,
        max_tokens: int,
        max_fragments: int,
        collection_name: str,
        respect_boundaries: bool,
    ) -> list[ContextFragment]:
        """Get fragments after the reference time.

        Args:
            source_id: Source document ID for filtering.
            reference_time: Time to search after (exclusive).
            max_tokens: Maximum total tokens to include.
            max_fragments: Maximum number of fragments.
            collection_name: Collection to query.
            respect_boundaries: Whether to stop at document boundaries.

        Returns:
            List of ContextFragment objects in chronological order.
        """
        if reference_time is None:
            return []

        # Build filter for same source, after reference time
        filter_conditions: list[models.Condition] = self._build_source_filter(
            source_id, respect_boundaries
        )
        filter_conditions.append(
            models.FieldCondition(
                key="start_time",
                range=models.Range(gt=reference_time),
            )
        )

        try:
            # Get fragments after, ordered by start_time ascending (closest first)
            results = self.qdrant_client.scroll(
                collection_name=collection_name,
                scroll_filter=models.Filter(must=filter_conditions),
                limit=max_fragments * 2,
                with_payload=True,
                order_by=models.OrderBy(
                    key="start_time",
                    direction=models.Direction.ASC,
                ),
            )

            points = results[0] if results else []
            return self._collect_fragments_with_token_limit(
                points, max_tokens, max_fragments, reverse=False
            )

        except Exception as e:
            logger.warning(f"Error fetching after context: {e}, trying fallback")
            # Fallback: try with start_secs for legacy schema
            return self._get_after_context_legacy(
                source_id, reference_time, max_tokens, max_fragments, collection_name
            )

    def _get_after_context_legacy(
        self,
        source_id: str,
        reference_time: float,
        max_tokens: int,
        max_fragments: int,
        collection_name: str,
    ) -> list[ContextFragment]:
        """Fallback for legacy schema using start_secs/end_secs."""
        try:
            filter_conditions: list[models.Condition] = [
                models.FieldCondition(
                    key="episode",
                    match=models.MatchValue(value=int(source_id)),
                ),
                models.FieldCondition(
                    key="start_secs",
                    range=models.Range(gt=int(reference_time)),
                ),
            ]

            results = self.qdrant_client.scroll(
                collection_name=collection_name,
                scroll_filter=models.Filter(must=filter_conditions),
                limit=max_fragments * 2,
                with_payload=True,
            )

            points = results[0] if results else []
            # Sort manually
            points.sort(
                key=lambda p: p.payload.get("start_secs", 0) if p.payload else 0
            )
            return self._collect_fragments_with_token_limit(
                points, max_tokens, max_fragments, reverse=False
            )

        except Exception as e:
            logger.error(f"Error in legacy after context: {e}")
            return []

    def _build_source_filter(
        self,
        source_id: str,
        respect_boundaries: bool,
    ) -> list[models.Condition]:
        """Build filter conditions for source document.

        Args:
            source_id: Source document ID.
            respect_boundaries: Whether to filter by source.

        Returns:
            List of filter conditions.
        """
        if not respect_boundaries:
            return []

        # Try to parse as int for legacy episode field
        try:
            episode_id = int(source_id)
            return [
                models.FieldCondition(
                    key="episode",
                    match=models.MatchValue(value=episode_id),
                )
            ]
        except ValueError:
            # Use source_id field for new schema
            return [
                models.FieldCondition(
                    key="source_id",
                    match=models.MatchValue(value=source_id),
                )
            ]

    def _collect_fragments_with_token_limit(
        self,
        points: list,
        max_tokens: int,
        max_fragments: int,
        reverse: bool,
    ) -> list[ContextFragment]:
        """Collect fragments while respecting token and count limits.

        Args:
            points: Qdrant points to process.
            max_tokens: Maximum total tokens.
            max_fragments: Maximum number of fragments.
            reverse: Whether to reverse the final order.

        Returns:
            List of ContextFragment objects.
        """
        fragments = []
        total_tokens = 0

        for point in points:
            if len(fragments) >= max_fragments:
                break

            payload = point.payload or {}
            text = payload.get("text", "")
            token_count = self.estimate_tokens(text)

            # Check if adding this fragment exceeds token limit
            if total_tokens + token_count > max_tokens:
                break

            fragments.append(
                ContextFragment(
                    id=str(point.id),
                    text=text,
                    start_time=payload.get("start_time") or payload.get("start_secs"),
                    end_time=payload.get("end_time") or payload.get("end_secs"),
                    token_count=token_count,
                )
            )
            total_tokens += token_count

        if reverse:
            fragments.reverse()

        return fragments

    def get_full_context_text(
        self,
        expanded: ExpandedFragment,
        separator: str = " ",
    ) -> str:
        """Combine before context, fragment, and after context into text.

        Args:
            expanded: The expanded fragment.
            separator: Separator between fragments.

        Returns:
            Combined text with context.
        """
        parts = []
        parts.extend(f.text for f in expanded.before_context)
        parts.append(expanded.text)
        parts.extend(f.text for f in expanded.after_context)
        return separator.join(parts)

    def get_context_token_count(self, expanded: ExpandedFragment) -> int:
        """Get total token count for the expanded context.

        Args:
            expanded: The expanded fragment.

        Returns:
            Total estimated token count.
        """
        total = self.estimate_tokens(expanded.text)
        total += sum(f.token_count for f in expanded.before_context)
        total += sum(f.token_count for f in expanded.after_context)
        return total
