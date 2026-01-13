# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Modular ingestion pipeline architecture for content processing.

This module provides the core pipeline infrastructure for orchestrating
source fetching, content extraction, chunking, embedding, and indexing.
Pipelines are built from composable stages that can be configured,
monitored, and scaled independently.

Usage:
    from voogle.pipeline import Pipeline, Stage, PipelineConfig

    class FetchStage(Stage):
        async def process(self, items):
            for item in items:
                yield await self.fetch(item)

    config = PipelineConfig(max_concurrency=4)
    pipeline = Pipeline([FetchStage(), ChunkStage(), EmbedStage()], config)

    async for result in pipeline.execute(sources):
        print(f"Processed: {result}")
"""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Generic, TypeVar

logger = logging.getLogger(__name__)

# Type variables for stage input/output types
InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class StageStatus(Enum):
    """Status of a pipeline stage execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RetryStrategy(Enum):
    """Strategy for retrying failed stage operations."""

    NONE = "none"
    FIXED = "fixed"
    EXPONENTIAL = "exponential"


@dataclass(frozen=True)
class RetryConfig:
    """Configuration for retry behavior.

    Attributes:
        strategy: The retry strategy to use.
        max_retries: Maximum number of retry attempts.
        base_delay: Base delay in seconds between retries.
        max_delay: Maximum delay in seconds for exponential backoff.
        jitter: Whether to add random jitter to delays.
    """

    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    jitter: bool = True

    def __post_init__(self) -> None:
        """Validate retry configuration."""
        if self.max_retries < 0:
            raise ValueError(f"max_retries must be >= 0, got {self.max_retries}")
        if self.base_delay < 0:
            raise ValueError(f"base_delay must be >= 0, got {self.base_delay}")
        if self.max_delay < self.base_delay:
            raise ValueError(
                f"max_delay must be >= base_delay, got max_delay={self.max_delay}, "
                f"base_delay={self.base_delay}"
            )

    def get_delay(self, attempt: int) -> float:
        """Calculate the delay for a given retry attempt.

        Args:
            attempt: The retry attempt number (0-indexed).

        Returns:
            The delay in seconds before the next retry.
        """
        import random

        if self.strategy == RetryStrategy.NONE:
            return 0.0
        elif self.strategy == RetryStrategy.FIXED:
            delay = self.base_delay
        else:  # EXPONENTIAL
            delay = min(self.base_delay * (2**attempt), self.max_delay)

        if self.jitter:
            delay = delay * (0.5 + random.random())

        return delay


@dataclass(frozen=True)
class PipelineConfig:
    """Configuration for pipeline execution.

    Attributes:
        max_concurrency: Maximum number of concurrent items to process.
        stage_timeout: Timeout in seconds for each stage operation.
        pipeline_timeout: Timeout in seconds for the entire pipeline.
        retry_config: Configuration for retry behavior.
        buffer_size: Size of the buffer between stages.
        fail_fast: Whether to stop the pipeline on first error.
    """

    max_concurrency: int = 4
    stage_timeout: float | None = 300.0
    pipeline_timeout: float | None = None
    retry_config: RetryConfig = field(default_factory=RetryConfig)
    buffer_size: int = 100
    fail_fast: bool = False

    def __post_init__(self) -> None:
        """Validate pipeline configuration."""
        if self.max_concurrency < 1:
            raise ValueError(f"max_concurrency must be >= 1, got {self.max_concurrency}")
        if self.stage_timeout is not None and self.stage_timeout <= 0:
            raise ValueError(f"stage_timeout must be > 0, got {self.stage_timeout}")
        if self.pipeline_timeout is not None and self.pipeline_timeout <= 0:
            raise ValueError(f"pipeline_timeout must be > 0, got {self.pipeline_timeout}")
        if self.buffer_size < 1:
            raise ValueError(f"buffer_size must be >= 1, got {self.buffer_size}")


@dataclass
class StageProgress:
    """Progress tracking for a pipeline stage.

    Attributes:
        stage_name: Name of the stage being tracked.
        status: Current status of the stage.
        items_processed: Number of items successfully processed.
        items_failed: Number of items that failed processing.
        items_total: Total number of items to process (if known).
        started_at: Timestamp when the stage started.
        completed_at: Timestamp when the stage completed.
        errors: List of error messages from failed items.
    """

    stage_name: str
    status: StageStatus = StageStatus.PENDING
    items_processed: int = 0
    items_failed: int = 0
    items_total: int | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    errors: list[str] = field(default_factory=list)

    @property
    def items_attempted(self) -> int:
        """Total number of items attempted (processed + failed)."""
        return self.items_processed + self.items_failed

    @property
    def success_rate(self) -> float:
        """Calculate the success rate as a percentage."""
        if self.items_attempted == 0:
            return 0.0
        return (self.items_processed / self.items_attempted) * 100.0

    @property
    def is_complete(self) -> bool:
        """Check if the stage has finished execution."""
        return self.status in (
            StageStatus.COMPLETED,
            StageStatus.FAILED,
            StageStatus.CANCELLED,
        )


@dataclass
class PipelineProgress:
    """Progress tracking for an entire pipeline execution.

    Attributes:
        stages: Progress for each stage in the pipeline.
        started_at: Timestamp when the pipeline started.
        completed_at: Timestamp when the pipeline completed.
    """

    stages: dict[str, StageProgress] = field(default_factory=dict)
    started_at: datetime | None = None
    completed_at: datetime | None = None

    @property
    def is_complete(self) -> bool:
        """Check if all stages have finished execution."""
        if not self.stages:
            return False
        return all(stage.is_complete for stage in self.stages.values())

    @property
    def total_processed(self) -> int:
        """Total items processed across all stages."""
        return sum(stage.items_processed for stage in self.stages.values())

    @property
    def total_failed(self) -> int:
        """Total items failed across all stages."""
        return sum(stage.items_failed for stage in self.stages.values())


class StageError(Exception):
    """Exception raised when a stage fails to process an item."""

    def __init__(
        self, stage_name: str, message: str, item: Any = None, cause: Exception | None = None
    ):
        self.stage_name = stage_name
        self.item = item
        self.cause = cause
        super().__init__(f"Stage '{stage_name}': {message}")


class PipelineError(Exception):
    """Exception raised when a pipeline fails."""

    def __init__(self, message: str, stage_errors: list[StageError] | None = None):
        self.stage_errors = stage_errors or []
        super().__init__(message)


class Stage(ABC, Generic[InputT, OutputT]):
    """Abstract base class for pipeline stages.

    Stages are the building blocks of pipelines. Each stage receives items
    from the previous stage (or the initial input), processes them, and
    yields results to the next stage.

    Subclasses must implement:
        - name: Property returning the stage name
        - process: Method that processes items and yields results

    Example:
        class FetchStage(Stage[str, bytes]):
            @property
            def name(self) -> str:
                return "fetch"

            async def process(self, items: AsyncIterator[str]) -> AsyncIterator[bytes]:
                async for url in items:
                    yield await self.fetch(url)
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this stage.

        The name is used for logging, progress tracking, and error reporting.
        """
        ...

    @abstractmethod
    async def process(self, items: AsyncIterator[InputT]) -> AsyncIterator[OutputT]:
        """Process items from the previous stage.

        Args:
            items: Async iterator of items to process.

        Yields:
            Processed items for the next stage.

        Raises:
            StageError: If processing fails for an item.
        """
        # Required yield to make this an async generator
        if False:  # pragma: no cover
            yield  # type: ignore

    async def setup(self) -> None:
        """Initialize resources before processing begins.

        Override this method to perform setup operations like opening
        connections, loading models, or allocating resources.
        """
        pass

    async def teardown(self) -> None:
        """Clean up resources after processing completes.

        Override this method to clean up resources allocated in setup(),
        such as closing connections or releasing memory.
        """
        pass

    async def on_error(self, item: InputT, error: Exception) -> OutputT | None:
        """Handle an error during item processing.

        Override this method to provide custom error handling, such as
        returning a fallback value or logging additional context.

        Args:
            item: The item that caused the error.
            error: The exception that was raised.

        Returns:
            A fallback value to yield, or None to skip this item.

        Raises:
            Exception: Re-raise if the error should propagate.
        """
        raise error


class Pipeline:
    """Orchestrates execution of a sequence of stages.

    Pipelines connect stages together, managing data flow, concurrency,
    error handling, and progress tracking.

    Example:
        config = PipelineConfig(max_concurrency=4)
        pipeline = Pipeline([FetchStage(), ProcessStage()], config)

        async for result in pipeline.execute(items):
            print(result)
    """

    def __init__(
        self,
        stages: list[Stage[Any, Any]],
        config: PipelineConfig | None = None,
    ):
        """Initialize the pipeline.

        Args:
            stages: List of stages to execute in order.
            config: Pipeline configuration. Uses defaults if not provided.

        Raises:
            ValueError: If stages list is empty.
        """
        if not stages:
            raise ValueError("Pipeline must have at least one stage")

        self._stages = stages
        self._config = config or PipelineConfig()
        self._progress = PipelineProgress()
        self._cancelled = False
        self._semaphore: asyncio.Semaphore | None = None

    @property
    def stages(self) -> list[Stage[Any, Any]]:
        """Return the list of stages in this pipeline."""
        return self._stages

    @property
    def config(self) -> PipelineConfig:
        """Return the pipeline configuration."""
        return self._config

    @property
    def progress(self) -> PipelineProgress:
        """Return the current progress of the pipeline."""
        return self._progress

    async def execute(self, items: AsyncIterator[Any]) -> AsyncIterator[Any]:
        """Execute the pipeline on the given items.

        Args:
            items: Async iterator of items to process.

        Yields:
            Processed items from the final stage.

        Raises:
            PipelineError: If the pipeline fails and fail_fast is enabled.
        """
        self._cancelled = False
        self._progress = PipelineProgress(started_at=datetime.now())
        self._semaphore = asyncio.Semaphore(self._config.max_concurrency)

        # Initialize progress for all stages
        for stage in self._stages:
            self._progress.stages[stage.name] = StageProgress(stage_name=stage.name)

        try:
            # Setup all stages
            await self._setup_stages()

            # Chain stages together
            current_items = items
            for stage in self._stages:
                current_items = self._execute_stage(stage, current_items)

            # Yield final results
            async for result in current_items:
                yield result

        finally:
            # Teardown all stages
            await self._teardown_stages()
            self._progress.completed_at = datetime.now()

    async def cancel(self) -> None:
        """Cancel the pipeline execution.

        This sets a flag that stages should check to stop processing.
        """
        self._cancelled = True

    async def _setup_stages(self) -> None:
        """Setup all stages in the pipeline."""
        for stage in self._stages:
            try:
                await stage.setup()
            except Exception as e:
                logger.error(f"Failed to setup stage '{stage.name}': {e}")
                raise PipelineError(
                    f"Failed to setup stage '{stage.name}'",
                    stage_errors=[StageError(stage.name, str(e), cause=e)],
                )

    async def _teardown_stages(self) -> None:
        """Teardown all stages in the pipeline."""
        for stage in self._stages:
            try:
                await stage.teardown()
            except Exception as e:
                logger.warning(f"Failed to teardown stage '{stage.name}': {e}")

    async def _execute_stage(
        self, stage: Stage[Any, Any], items: AsyncIterator[Any]
    ) -> AsyncIterator[Any]:
        """Execute a single stage with error handling and progress tracking."""
        progress = self._progress.stages[stage.name]
        progress.status = StageStatus.RUNNING
        progress.started_at = datetime.now()

        try:
            async for result in self._process_with_retry(stage, items):
                if self._cancelled:
                    progress.status = StageStatus.CANCELLED
                    break
                progress.items_processed += 1
                yield result

            if not self._cancelled:
                progress.status = StageStatus.COMPLETED

        except Exception as e:
            progress.status = StageStatus.FAILED
            progress.errors.append(str(e))
            if self._config.fail_fast:
                raise PipelineError(
                    f"Pipeline failed at stage '{stage.name}'",
                    stage_errors=[StageError(stage.name, str(e), cause=e)],
                )
            logger.error(f"Stage '{stage.name}' failed: {e}")

        finally:
            progress.completed_at = datetime.now()

    async def _process_with_retry(
        self, stage: Stage[Any, Any], items: AsyncIterator[Any]
    ) -> AsyncIterator[Any]:
        """Process items through a stage with retry logic."""
        retry_config = self._config.retry_config
        progress = self._progress.stages[stage.name]

        async for item in items:
            if self._cancelled:
                break

            result = None
            last_error: Exception | None = None

            for attempt in range(retry_config.max_retries + 1):
                try:
                    async with self._semaphore:  # type: ignore
                        # Create a single-item iterator for processing
                        async def single_item() -> AsyncIterator[Any]:
                            yield item

                        async for output in stage.process(single_item()):
                            result = output
                            break  # Only take first result

                    break  # Success, exit retry loop

                except Exception as e:
                    last_error = e
                    if attempt < retry_config.max_retries:
                        delay = retry_config.get_delay(attempt)
                        logger.warning(
                            f"Stage '{stage.name}' failed on attempt {attempt + 1}, "
                            f"retrying in {delay:.1f}s: {e}"
                        )
                        await asyncio.sleep(delay)
                    else:
                        # Max retries exceeded, try error handler
                        try:
                            result = await stage.on_error(item, e)
                        except Exception:
                            progress.items_failed += 1
                            progress.errors.append(str(e))
                            if self._config.fail_fast:
                                raise StageError(
                                    stage.name, str(e), item=item, cause=e
                                )
                            continue

            if result is not None:
                yield result
