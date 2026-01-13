# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""MCP expand tool for context expansion with document boundary respect.

Provides the primary MCP tool for expanding search result fragments with
surrounding context. Supports directional expansion (before/after/both),
token-limited windows, and document boundary respect.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from voogle.services.expansion import (
    ContextExpander,
    ExpansionConfig,
)


class ExpandDirection(Enum):
    """Direction for context expansion."""

    BEFORE = "before"
    AFTER = "after"
    BOTH = "both"


@dataclass
class ExpandContextFragment:
    """A context fragment in the expansion output.

    Attributes:
        id: Unique identifier of the fragment.
        text: The text content of the fragment.
        start_time: Start time in seconds (for audio/video).
        end_time: End time in seconds (for audio/video).
        token_count: Estimated token count for this fragment.
    """

    id: str
    text: str
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    token_count: int = 0


@dataclass
class ExpandToolOutput:
    """Output from the expand tool.

    Attributes:
        fragment_id: The ID of the original fragment.
        original_text: The original text content of the fragment.
        before_context: List of context fragments before the original.
        after_context: List of context fragments after the original.
        combined_text: All context and original text combined.
        total_tokens: Total estimated token count.
        at_document_start: Whether the expansion reached the document start.
        at_document_end: Whether the expansion reached the document end.
        source_id: The source document ID.
    """

    fragment_id: str
    original_text: str
    before_context: list[ExpandContextFragment]
    after_context: list[ExpandContextFragment]
    combined_text: str
    total_tokens: int
    at_document_start: bool
    at_document_end: bool
    source_id: str


class ExpandToolError(Exception):
    """Error raised by the expand tool."""

    def __init__(self, message: str, error_code: str) -> None:
        """Initialize the error.

        Args:
            message: Human-readable error message.
            error_code: Machine-readable error code.
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class ExpandTool:
    """MCP tool for context expansion around search result fragments.

    Provides context expansion capabilities over Voogle's indexed content
    with support for:
    - Directional expansion (before/after/both)
    - Token-limited expansion windows
    - Document boundary respect
    - Boundary indicators
    """

    name: str = "expand"
    description: str = (
        "Expand a search result fragment with surrounding context. "
        "Returns the original fragment plus neighboring context while "
        "respecting document boundaries and token limits."
    )

    def __init__(
        self,
        context_expander: Optional[ContextExpander] = None,
    ) -> None:
        """Initialize the expand tool.

        Args:
            context_expander: Optional ContextExpander instance for expansion.
                If None, creates a new expander with default configuration.
        """
        self._context_expander = context_expander

    @property
    def context_expander(self) -> ContextExpander:
        """Get or lazily initialize the context expander."""
        if self._context_expander is None:
            self._context_expander = ContextExpander()
        return self._context_expander

    @property
    def input_schema(self) -> dict[str, Any]:
        """Return the JSON schema for tool input parameters.

        Returns:
            JSON Schema dictionary describing the input format.
        """
        return {
            "type": "object",
            "properties": {
                "fragment_id": {
                    "type": "string",
                    "description": "The unique identifier of the fragment to expand",
                    "minLength": 1,
                },
                "source_id": {
                    "type": "string",
                    "description": "The source document ID for boundary detection",
                    "minLength": 1,
                },
                "direction": {
                    "type": "string",
                    "enum": ["before", "after", "both"],
                    "description": "Direction to expand: 'before', 'after', or 'both'",
                    "default": "both",
                },
                "tokens": {
                    "type": "integer",
                    "description": "Maximum tokens to include in expansion (applies to each direction)",
                    "minimum": 1,
                    "maximum": 2000,
                    "default": 500,
                },
                "max_fragments": {
                    "type": "integer",
                    "description": "Maximum number of fragments to include per direction",
                    "minimum": 1,
                    "maximum": 20,
                    "default": 5,
                },
            },
            "required": ["fragment_id", "source_id"],
        }

    def __call__(
        self,
        fragment_id: str,
        source_id: str,
        direction: str = "both",
        tokens: int = 500,
        max_fragments: int = 5,
    ) -> dict[str, Any]:
        """Expand a fragment with surrounding context.

        Args:
            fragment_id: The unique identifier of the fragment to expand.
            source_id: The source document ID for boundary detection.
            direction: Direction to expand ('before', 'after', or 'both').
            tokens: Maximum tokens to include in expansion per direction.
            max_fragments: Maximum number of fragments per direction.

        Returns:
            Dictionary containing original fragment, expanded context,
            combined text, and boundary indicators.

        Raises:
            ExpandToolError: If fragment_id is invalid or fragment not found.
            ValueError: If parameters are invalid.
        """
        # Validate inputs
        if not fragment_id or not fragment_id.strip():
            raise ExpandToolError(
                message="fragment_id cannot be empty",
                error_code="INVALID_FRAGMENT_ID",
            )
        if not source_id or not source_id.strip():
            raise ExpandToolError(
                message="source_id cannot be empty",
                error_code="INVALID_SOURCE_ID",
            )

        # Validate direction
        direction = direction.lower().strip()
        if direction not in ("before", "after", "both"):
            raise ValueError(
                f"direction must be 'before', 'after', or 'both', got '{direction}'"
            )

        # Validate tokens
        if tokens < 1 or tokens > 2000:
            raise ValueError(f"tokens must be between 1 and 2000, got {tokens}")

        # Validate max_fragments
        if max_fragments < 1 or max_fragments > 20:
            raise ValueError(
                f"max_fragments must be between 1 and 20, got {max_fragments}"
            )

        # Build expansion config based on direction
        config = ExpansionConfig(
            max_tokens_before=tokens if direction in ("before", "both") else 0,
            max_tokens_after=tokens if direction in ("after", "both") else 0,
            max_fragments_before=max_fragments if direction in ("before", "both") else 0,
            max_fragments_after=max_fragments if direction in ("after", "both") else 0,
            respect_boundaries=True,
        )

        # Execute expansion
        expanded = self.context_expander.expand(
            fragment_id=fragment_id.strip(),
            source_id=source_id.strip(),
            config=config,
        )

        if expanded is None:
            raise ExpandToolError(
                message=f"Fragment not found: {fragment_id}",
                error_code="FRAGMENT_NOT_FOUND",
            )

        # Build output
        before_context = [
            {
                "id": f.id,
                "text": f.text,
                "start_time": f.start_time,
                "end_time": f.end_time,
                "token_count": f.token_count,
            }
            for f in expanded.before_context
        ]

        after_context = [
            {
                "id": f.id,
                "text": f.text,
                "start_time": f.start_time,
                "end_time": f.end_time,
                "token_count": f.token_count,
            }
            for f in expanded.after_context
        ]

        # Get combined text
        combined_text = self.context_expander.get_full_context_text(expanded)
        total_tokens = self.context_expander.get_context_token_count(expanded)

        # Determine boundary indicators
        # At document start if we requested before context but got none/less than max
        at_document_start = (
            direction in ("before", "both")
            and len(expanded.before_context) < max_fragments
            and sum(f.token_count for f in expanded.before_context) < tokens
        )

        # At document end if we requested after context but got none/less than max
        at_document_end = (
            direction in ("after", "both")
            and len(expanded.after_context) < max_fragments
            and sum(f.token_count for f in expanded.after_context) < tokens
        )

        return {
            "fragment_id": expanded.id,
            "original_text": expanded.text,
            "before_context": before_context,
            "after_context": after_context,
            "combined_text": combined_text,
            "total_tokens": total_tokens,
            "at_document_start": at_document_start,
            "at_document_end": at_document_end,
            "source_id": expanded.source_id,
        }


# Module-level instance for convenient access
expand_tool = ExpandTool()
