# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Modular ingestion pipeline architecture.

This module provides the core infrastructure for building content processing
pipelines. Pipelines orchestrate source fetching, content extraction,
chunking, embedding, and indexing through composable stages.

Exports:
    Pipeline: Main pipeline orchestrator class.
    Stage: Abstract base class for pipeline stages.
    PipelineConfig: Configuration for pipeline execution.
    RetryConfig: Configuration for retry behavior.
    RetryStrategy: Enum for retry strategies (none, fixed, exponential).
    StageStatus: Enum for stage execution status.
    StageProgress: Progress tracking for individual stages.
    PipelineProgress: Progress tracking for entire pipeline.
    StageError: Exception for stage processing failures.
    PipelineError: Exception for pipeline-level failures.

Example:
    from voogle.pipeline import Pipeline, Stage, PipelineConfig

    class FetchStage(Stage[str, dict]):
        @property
        def name(self) -> str:
            return "fetch"

        async def process(self, items):
            async for url in items:
                yield await fetch_data(url)

    config = PipelineConfig(max_concurrency=4)
    pipeline = Pipeline([FetchStage()], config)

    async for result in pipeline.execute(urls):
        print(result)
"""

from voogle.pipeline.base import (
    Pipeline,
    PipelineConfig,
    PipelineError,
    PipelineProgress,
    RetryConfig,
    RetryStrategy,
    Stage,
    StageError,
    StageProgress,
    StageStatus,
)
from voogle.pipeline.chunking import (
    Chunk,
    ChunkableContent,
    ChunkConfig,
    ChunkingStage,
    ChunkStrategy,
)

__all__ = [
    "Chunk",
    "ChunkableContent",
    "ChunkConfig",
    "ChunkingStage",
    "ChunkStrategy",
    "Pipeline",
    "PipelineConfig",
    "PipelineError",
    "PipelineProgress",
    "RetryConfig",
    "RetryStrategy",
    "Stage",
    "StageError",
    "StageProgress",
    "StageStatus",
]
