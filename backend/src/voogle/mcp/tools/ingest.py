# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""MCP ingest tool for triggering content ingestion.

Provides the MCP tool for initiating content ingestion as long-running
background operations via JobService.
"""

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from voogle.pipeline.jobs import JobService, get_job_service


class SourceType(str, Enum):
    """Type of content source for ingestion.

    Attributes:
        URL: Single URL to fetch and process.
        FILE: Local file path to process.
        BATCH: Batch of multiple sources (URLs or files).
    """

    URL = "url"
    FILE = "file"
    BATCH = "batch"


class ChunkingStrategy(str, Enum):
    """Strategy for dividing content into fragments.

    Attributes:
        FIXED_SIZE: Fixed-size chunks (default ~40 words).
        SENTENCE: Split on sentence boundaries.
        PARAGRAPH: Split on paragraph boundaries.
        SEMANTIC: Use semantic boundaries (more compute-intensive).
    """

    FIXED_SIZE = "fixed_size"
    SENTENCE = "sentence"
    PARAGRAPH = "paragraph"
    SEMANTIC = "semantic"


@dataclass
class IngestSource:
    """Source specification for ingestion.

    Attributes:
        type: The source type (url, file, or batch).
        value: The source value - URL string, file path, or list of sources.
        content_type: Optional hint about content type (audio, video, document).
    """

    type: SourceType
    value: str | list[str]
    content_type: Optional[str] = None


@dataclass
class IngestToolInput:
    """Input schema for the MCP ingest tool.

    Attributes:
        corpus_id: ID of the corpus to ingest content into.
        source: Source specification with type and value.
        metadata: Optional metadata to attach to ingested content.
        chunking_strategy: Strategy for dividing content into fragments.
    """

    corpus_id: str
    source: IngestSource
    metadata: dict[str, Any] = field(default_factory=dict)
    chunking_strategy: ChunkingStrategy = ChunkingStrategy.FIXED_SIZE


@dataclass
class IngestToolOutput:
    """Output from the ingest tool.

    Attributes:
        job_id: Unique identifier for the ingestion job.
        status: Initial status of the job (always 'pending').
        message: Human-readable confirmation message.
    """

    job_id: str
    status: str
    message: str


class IngestTool:
    """MCP tool for triggering content ingestion.

    Initiates long-running ingestion operations that run in the background.
    Returns a job ID immediately that can be used to track progress.

    Supports:
    - Single URL ingestion
    - Local file ingestion
    - Batch ingestion of multiple sources
    - Configurable chunking strategies
    - Custom metadata attachment
    """

    name: str = "ingest"
    description: str = (
        "Trigger content ingestion into a corpus. "
        "Accepts URLs, file paths, or batch sources. "
        "Returns a job ID immediately for tracking the long-running operation. "
        "Use the job ID to monitor progress or cancel the ingestion."
    )

    def __init__(self, job_service: Optional[JobService] = None) -> None:
        """Initialize the ingest tool.

        Args:
            job_service: Optional JobService instance for job management.
                If None, uses the default service.
        """
        self._job_service = job_service

    @property
    def job_service(self) -> JobService:
        """Get or lazily initialize the job service."""
        if self._job_service is None:
            self._job_service = get_job_service()
        return self._job_service

    @property
    def input_schema(self) -> dict[str, Any]:
        """Return the JSON schema for tool input parameters.

        Returns:
            JSON Schema dictionary describing the input format.
        """
        return {
            "type": "object",
            "properties": {
                "corpus_id": {
                    "type": "string",
                    "description": "ID of the corpus to ingest content into",
                    "minLength": 1,
                },
                "source": {
                    "type": "object",
                    "description": "Source specification for content to ingest",
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": ["url", "file", "batch"],
                            "description": "Type of source (url, file, or batch)",
                        },
                        "value": {
                            "oneOf": [
                                {
                                    "type": "string",
                                    "description": "Single URL or file path",
                                },
                                {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Batch of URLs or file paths",
                                },
                            ],
                            "description": "Source value - URL, file path, or list for batch",
                        },
                        "content_type": {
                            "type": "string",
                            "description": "Optional content type hint (audio, video, document)",
                        },
                    },
                    "required": ["type", "value"],
                },
                "metadata": {
                    "type": "object",
                    "description": "Optional metadata to attach to ingested content",
                    "additionalProperties": True,
                },
                "chunking_strategy": {
                    "type": "string",
                    "enum": ["fixed_size", "sentence", "paragraph", "semantic"],
                    "description": "Strategy for dividing content into fragments",
                    "default": "fixed_size",
                },
            },
            "required": ["corpus_id", "source"],
        }

    def _generate_job_id(self) -> str:
        """Generate a unique job ID.

        Returns:
            A unique job ID string.
        """
        return f"ingest-{uuid.uuid4().hex[:12]}"

    def _validate_source(self, source: dict[str, Any]) -> IngestSource:
        """Validate and parse source specification.

        Args:
            source: Raw source dictionary from input.

        Returns:
            Validated IngestSource object.

        Raises:
            ValueError: If source specification is invalid.
        """
        if not source:
            raise ValueError("source cannot be empty")

        source_type_str = source.get("type")
        if not source_type_str:
            raise ValueError("source.type is required")

        try:
            source_type = SourceType(source_type_str)
        except ValueError:
            valid_types = [st.value for st in SourceType]
            raise ValueError(
                f"Invalid source type '{source_type_str}'. "
                f"Must be one of: {valid_types}"
            )

        value = source.get("value")
        if value is None:
            raise ValueError("source.value is required")

        # Validate value based on type
        if source_type == SourceType.BATCH:
            if not isinstance(value, list):
                raise ValueError("source.value must be a list for batch type")
            if len(value) == 0:
                raise ValueError("source.value cannot be empty for batch type")
        else:
            if not isinstance(value, str):
                raise ValueError(
                    f"source.value must be a string for {source_type.value} type"
                )

        return IngestSource(
            type=source_type,
            value=value,
            content_type=source.get("content_type"),
        )

    def _validate_chunking_strategy(
        self, strategy: Optional[str]
    ) -> ChunkingStrategy:
        """Validate and parse chunking strategy.

        Args:
            strategy: Raw strategy string from input.

        Returns:
            Validated ChunkingStrategy enum value.

        Raises:
            ValueError: If strategy is invalid.
        """
        if strategy is None:
            return ChunkingStrategy.FIXED_SIZE

        try:
            return ChunkingStrategy(strategy)
        except ValueError:
            valid_strategies = [cs.value for cs in ChunkingStrategy]
            raise ValueError(
                f"Invalid chunking strategy '{strategy}'. "
                f"Must be one of: {valid_strategies}"
            )

    def __call__(
        self,
        corpus_id: str,
        source: dict[str, Any],
        metadata: Optional[dict[str, Any]] = None,
        chunking_strategy: Optional[str] = None,
    ) -> dict[str, Any]:
        """Trigger content ingestion as a background job.

        Creates a new ingestion job and queues it for processing.
        Returns immediately with the job ID for tracking.

        Args:
            corpus_id: ID of the corpus to ingest content into.
            source: Source specification dict with type and value.
            metadata: Optional metadata to attach to ingested content.
            chunking_strategy: Strategy for chunking (fixed_size, sentence,
                paragraph, semantic). Defaults to fixed_size.

        Returns:
            Dictionary containing job_id, status, and confirmation message.

        Raises:
            ValueError: If inputs are invalid.
        """
        # Validate corpus_id
        if not corpus_id or not corpus_id.strip():
            raise ValueError("corpus_id cannot be empty")
        corpus_id = corpus_id.strip()

        # Validate and parse source
        validated_source = self._validate_source(source)

        # Validate chunking strategy
        validated_strategy = self._validate_chunking_strategy(chunking_strategy)

        # Generate job ID
        job_id = self._generate_job_id()

        # Prepare job metadata
        job_metadata = {
            "source_type": validated_source.type.value,
            "source_value": validated_source.value,
            "source_content_type": validated_source.content_type,
            "chunking_strategy": validated_strategy.value,
            "user_metadata": metadata or {},
        }

        # Create job via JobService
        job = self.job_service.create(
            job_id=job_id,
            corpus_id=corpus_id,
            **job_metadata,
        )

        # Build confirmation message
        source_desc = (
            f"{len(validated_source.value)} sources"
            if validated_source.type == SourceType.BATCH
            else f"1 {validated_source.type.value}"
        )
        message = (
            f"Ingestion job created for corpus '{corpus_id}'. "
            f"Processing {source_desc} with {validated_strategy.value} chunking."
        )

        return {
            "job_id": job_id,
            "status": job.status.value,
            "message": message,
        }


# Module-level instance for convenient access
ingest_tool = IngestTool()
