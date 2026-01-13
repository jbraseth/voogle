# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for pipeline architecture."""

from collections.abc import AsyncIterator
from typing import Any

import pytest

from voogle.pipeline import (
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


class TestRetryStrategy:
    """Tests for RetryStrategy enum."""

    def test_all_strategies_exist(self) -> None:
        """All expected retry strategies are defined."""
        assert RetryStrategy.NONE.value == "none"
        assert RetryStrategy.FIXED.value == "fixed"
        assert RetryStrategy.EXPONENTIAL.value == "exponential"

    def test_strategy_count(self) -> None:
        """Correct number of strategies are defined."""
        assert len(RetryStrategy) == 3


class TestStageStatus:
    """Tests for StageStatus enum."""

    def test_all_statuses_exist(self) -> None:
        """All expected stage statuses are defined."""
        assert StageStatus.PENDING.value == "pending"
        assert StageStatus.RUNNING.value == "running"
        assert StageStatus.COMPLETED.value == "completed"
        assert StageStatus.FAILED.value == "failed"
        assert StageStatus.CANCELLED.value == "cancelled"

    def test_status_count(self) -> None:
        """Correct number of statuses are defined."""
        assert len(StageStatus) == 5


class TestRetryConfig:
    """Tests for RetryConfig dataclass."""

    def test_create_default_config(self) -> None:
        """Default retry config can be created."""
        config = RetryConfig()
        assert config.strategy == RetryStrategy.EXPONENTIAL
        assert config.max_retries == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 60.0
        assert config.jitter is True

    def test_create_custom_config(self) -> None:
        """Custom retry config can be created."""
        config = RetryConfig(
            strategy=RetryStrategy.FIXED,
            max_retries=5,
            base_delay=2.0,
            max_delay=30.0,
            jitter=False,
        )
        assert config.strategy == RetryStrategy.FIXED
        assert config.max_retries == 5
        assert config.base_delay == 2.0
        assert config.max_delay == 30.0
        assert config.jitter is False

    def test_negative_max_retries_raises(self) -> None:
        """Negative max_retries raises ValueError."""
        with pytest.raises(ValueError, match="max_retries must be >= 0"):
            RetryConfig(max_retries=-1)

    def test_negative_base_delay_raises(self) -> None:
        """Negative base_delay raises ValueError."""
        with pytest.raises(ValueError, match="base_delay must be >= 0"):
            RetryConfig(base_delay=-1.0)

    def test_max_delay_less_than_base_raises(self) -> None:
        """max_delay < base_delay raises ValueError."""
        with pytest.raises(ValueError, match="max_delay must be >= base_delay"):
            RetryConfig(base_delay=10.0, max_delay=5.0)

    def test_get_delay_none_strategy(self) -> None:
        """NONE strategy returns zero delay."""
        config = RetryConfig(strategy=RetryStrategy.NONE)
        assert config.get_delay(0) == 0.0
        assert config.get_delay(5) == 0.0

    def test_get_delay_fixed_strategy(self) -> None:
        """FIXED strategy returns base_delay (with optional jitter)."""
        config = RetryConfig(strategy=RetryStrategy.FIXED, base_delay=2.0, jitter=False)
        assert config.get_delay(0) == 2.0
        assert config.get_delay(1) == 2.0
        assert config.get_delay(5) == 2.0

    def test_get_delay_exponential_strategy(self) -> None:
        """EXPONENTIAL strategy returns increasing delays."""
        config = RetryConfig(
            strategy=RetryStrategy.EXPONENTIAL,
            base_delay=1.0,
            max_delay=60.0,
            jitter=False,
        )
        assert config.get_delay(0) == 1.0
        assert config.get_delay(1) == 2.0
        assert config.get_delay(2) == 4.0
        assert config.get_delay(3) == 8.0

    def test_get_delay_respects_max_delay(self) -> None:
        """Exponential delay is capped at max_delay."""
        config = RetryConfig(
            strategy=RetryStrategy.EXPONENTIAL,
            base_delay=1.0,
            max_delay=5.0,
            jitter=False,
        )
        assert config.get_delay(10) == 5.0

    def test_config_is_frozen(self) -> None:
        """RetryConfig is immutable."""
        config = RetryConfig()
        with pytest.raises(AttributeError):
            config.max_retries = 10  # type: ignore[misc]


class TestPipelineConfig:
    """Tests for PipelineConfig dataclass."""

    def test_create_default_config(self) -> None:
        """Default pipeline config can be created."""
        config = PipelineConfig()
        assert config.max_concurrency == 4
        assert config.stage_timeout == 300.0
        assert config.pipeline_timeout is None
        assert config.buffer_size == 100
        assert config.fail_fast is False
        assert isinstance(config.retry_config, RetryConfig)

    def test_create_custom_config(self) -> None:
        """Custom pipeline config can be created."""
        retry = RetryConfig(max_retries=5)
        config = PipelineConfig(
            max_concurrency=8,
            stage_timeout=60.0,
            pipeline_timeout=3600.0,
            retry_config=retry,
            buffer_size=50,
            fail_fast=True,
        )
        assert config.max_concurrency == 8
        assert config.stage_timeout == 60.0
        assert config.pipeline_timeout == 3600.0
        assert config.retry_config.max_retries == 5
        assert config.buffer_size == 50
        assert config.fail_fast is True

    def test_zero_max_concurrency_raises(self) -> None:
        """Zero max_concurrency raises ValueError."""
        with pytest.raises(ValueError, match="max_concurrency must be >= 1"):
            PipelineConfig(max_concurrency=0)

    def test_negative_max_concurrency_raises(self) -> None:
        """Negative max_concurrency raises ValueError."""
        with pytest.raises(ValueError, match="max_concurrency must be >= 1"):
            PipelineConfig(max_concurrency=-1)

    def test_zero_stage_timeout_raises(self) -> None:
        """Zero stage_timeout raises ValueError."""
        with pytest.raises(ValueError, match="stage_timeout must be > 0"):
            PipelineConfig(stage_timeout=0.0)

    def test_negative_stage_timeout_raises(self) -> None:
        """Negative stage_timeout raises ValueError."""
        with pytest.raises(ValueError, match="stage_timeout must be > 0"):
            PipelineConfig(stage_timeout=-1.0)

    def test_none_stage_timeout_allowed(self) -> None:
        """None stage_timeout is allowed."""
        config = PipelineConfig(stage_timeout=None)
        assert config.stage_timeout is None

    def test_zero_pipeline_timeout_raises(self) -> None:
        """Zero pipeline_timeout raises ValueError."""
        with pytest.raises(ValueError, match="pipeline_timeout must be > 0"):
            PipelineConfig(pipeline_timeout=0.0)

    def test_zero_buffer_size_raises(self) -> None:
        """Zero buffer_size raises ValueError."""
        with pytest.raises(ValueError, match="buffer_size must be >= 1"):
            PipelineConfig(buffer_size=0)


class TestStageProgress:
    """Tests for StageProgress dataclass."""

    def test_create_default_progress(self) -> None:
        """Default stage progress can be created."""
        progress = StageProgress(stage_name="test")
        assert progress.stage_name == "test"
        assert progress.status == StageStatus.PENDING
        assert progress.items_processed == 0
        assert progress.items_failed == 0
        assert progress.items_total is None
        assert progress.started_at is None
        assert progress.completed_at is None
        assert progress.errors == []

    def test_items_attempted_property(self) -> None:
        """items_attempted returns sum of processed and failed."""
        progress = StageProgress(
            stage_name="test",
            items_processed=10,
            items_failed=2,
        )
        assert progress.items_attempted == 12

    def test_success_rate_property(self) -> None:
        """success_rate returns correct percentage."""
        progress = StageProgress(
            stage_name="test",
            items_processed=80,
            items_failed=20,
        )
        assert progress.success_rate == 80.0

    def test_success_rate_zero_attempts(self) -> None:
        """success_rate returns 0 when no items attempted."""
        progress = StageProgress(stage_name="test")
        assert progress.success_rate == 0.0

    def test_is_complete_for_pending(self) -> None:
        """is_complete returns False for PENDING status."""
        progress = StageProgress(stage_name="test", status=StageStatus.PENDING)
        assert progress.is_complete is False

    def test_is_complete_for_running(self) -> None:
        """is_complete returns False for RUNNING status."""
        progress = StageProgress(stage_name="test", status=StageStatus.RUNNING)
        assert progress.is_complete is False

    def test_is_complete_for_completed(self) -> None:
        """is_complete returns True for COMPLETED status."""
        progress = StageProgress(stage_name="test", status=StageStatus.COMPLETED)
        assert progress.is_complete is True

    def test_is_complete_for_failed(self) -> None:
        """is_complete returns True for FAILED status."""
        progress = StageProgress(stage_name="test", status=StageStatus.FAILED)
        assert progress.is_complete is True

    def test_is_complete_for_cancelled(self) -> None:
        """is_complete returns True for CANCELLED status."""
        progress = StageProgress(stage_name="test", status=StageStatus.CANCELLED)
        assert progress.is_complete is True


class TestPipelineProgress:
    """Tests for PipelineProgress dataclass."""

    def test_create_default_progress(self) -> None:
        """Default pipeline progress can be created."""
        progress = PipelineProgress()
        assert progress.stages == {}
        assert progress.started_at is None
        assert progress.completed_at is None

    def test_is_complete_empty_stages(self) -> None:
        """is_complete returns False for empty stages."""
        progress = PipelineProgress()
        assert progress.is_complete is False

    def test_is_complete_all_completed(self) -> None:
        """is_complete returns True when all stages complete."""
        progress = PipelineProgress(
            stages={
                "stage1": StageProgress(stage_name="stage1", status=StageStatus.COMPLETED),
                "stage2": StageProgress(stage_name="stage2", status=StageStatus.COMPLETED),
            }
        )
        assert progress.is_complete is True

    def test_is_complete_some_running(self) -> None:
        """is_complete returns False when some stages running."""
        progress = PipelineProgress(
            stages={
                "stage1": StageProgress(stage_name="stage1", status=StageStatus.COMPLETED),
                "stage2": StageProgress(stage_name="stage2", status=StageStatus.RUNNING),
            }
        )
        assert progress.is_complete is False

    def test_total_processed(self) -> None:
        """total_processed sums across all stages."""
        progress = PipelineProgress(
            stages={
                "stage1": StageProgress(stage_name="stage1", items_processed=10),
                "stage2": StageProgress(stage_name="stage2", items_processed=5),
            }
        )
        assert progress.total_processed == 15

    def test_total_failed(self) -> None:
        """total_failed sums across all stages."""
        progress = PipelineProgress(
            stages={
                "stage1": StageProgress(stage_name="stage1", items_failed=2),
                "stage2": StageProgress(stage_name="stage2", items_failed=3),
            }
        )
        assert progress.total_failed == 5


class TestStageError:
    """Tests for StageError exception."""

    def test_create_basic_error(self) -> None:
        """Basic stage error can be created."""
        error = StageError("fetch", "Connection failed")
        assert error.stage_name == "fetch"
        assert "fetch" in str(error)
        assert "Connection failed" in str(error)
        assert error.item is None
        assert error.cause is None

    def test_create_error_with_item(self) -> None:
        """Stage error with item can be created."""
        error = StageError("process", "Invalid format", item={"id": 123})
        assert error.item == {"id": 123}

    def test_create_error_with_cause(self) -> None:
        """Stage error with cause can be created."""
        cause = ValueError("bad value")
        error = StageError("embed", "Embedding failed", cause=cause)
        assert error.cause is cause


class TestPipelineError:
    """Tests for PipelineError exception."""

    def test_create_basic_error(self) -> None:
        """Basic pipeline error can be created."""
        error = PipelineError("Pipeline failed")
        assert "Pipeline failed" in str(error)
        assert error.stage_errors == []

    def test_create_error_with_stage_errors(self) -> None:
        """Pipeline error with stage errors can be created."""
        stage_errors = [
            StageError("fetch", "Network error"),
            StageError("process", "Parse error"),
        ]
        error = PipelineError("Multiple failures", stage_errors=stage_errors)
        assert len(error.stage_errors) == 2


class MockPassthroughStage(Stage[Any, Any]):
    """Mock stage that passes items through unchanged."""

    def __init__(self, name: str = "passthrough"):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    async def process(self, items: AsyncIterator[Any]) -> AsyncIterator[Any]:
        async for item in items:
            yield item


class MockTransformStage(Stage[int, int]):
    """Mock stage that doubles input values."""

    @property
    def name(self) -> str:
        return "transform"

    async def process(self, items: AsyncIterator[int]) -> AsyncIterator[int]:
        async for item in items:
            yield item * 2


class MockFailingStage(Stage[Any, Any]):
    """Mock stage that fails after processing some items."""

    def __init__(self, fail_after: int = 2):
        self._fail_after = fail_after
        self._count = 0

    @property
    def name(self) -> str:
        return "failing"

    async def process(self, items: AsyncIterator[Any]) -> AsyncIterator[Any]:
        async for item in items:
            self._count += 1
            if self._count > self._fail_after:
                raise ValueError(f"Intentional failure after {self._fail_after} items")
            yield item


class TestStage:
    """Tests for Stage ABC."""

    def test_abstract_methods_defined(self) -> None:
        """Stage has expected abstract methods."""
        abstract_methods = Stage.__abstractmethods__
        assert "name" in abstract_methods
        assert "process" in abstract_methods

    @pytest.mark.asyncio
    async def test_concrete_implementation_works(self) -> None:
        """Concrete stage implementation can be used."""
        stage = MockPassthroughStage()
        assert stage.name == "passthrough"

        async def items() -> AsyncIterator[int]:
            for i in [1, 2, 3]:
                yield i

        results = []
        async for result in stage.process(items()):
            results.append(result)

        assert results == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_setup_default_does_nothing(self) -> None:
        """Default setup() does nothing."""
        stage = MockPassthroughStage()
        await stage.setup()  # Should not raise

    @pytest.mark.asyncio
    async def test_teardown_default_does_nothing(self) -> None:
        """Default teardown() does nothing."""
        stage = MockPassthroughStage()
        await stage.teardown()  # Should not raise

    @pytest.mark.asyncio
    async def test_on_error_default_reraises(self) -> None:
        """Default on_error() re-raises the exception."""
        stage = MockPassthroughStage()
        error = ValueError("test error")
        with pytest.raises(ValueError, match="test error"):
            await stage.on_error("item", error)


class TestPipeline:
    """Tests for Pipeline class."""

    def test_create_pipeline(self) -> None:
        """Pipeline can be created with stages."""
        stages = [MockPassthroughStage("stage1"), MockPassthroughStage("stage2")]
        pipeline = Pipeline(stages)
        assert len(pipeline.stages) == 2
        assert isinstance(pipeline.config, PipelineConfig)

    def test_create_pipeline_with_config(self) -> None:
        """Pipeline can be created with custom config."""
        config = PipelineConfig(max_concurrency=8)
        pipeline = Pipeline([MockPassthroughStage()], config)
        assert pipeline.config.max_concurrency == 8

    def test_empty_stages_raises(self) -> None:
        """Empty stages list raises ValueError."""
        with pytest.raises(ValueError, match="at least one stage"):
            Pipeline([])

    @pytest.mark.asyncio
    async def test_execute_single_stage(self) -> None:
        """Pipeline with single stage executes correctly."""
        pipeline = Pipeline([MockPassthroughStage()])

        async def items() -> AsyncIterator[int]:
            for i in [1, 2, 3]:
                yield i

        results = []
        async for result in pipeline.execute(items()):
            results.append(result)

        assert results == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_execute_multiple_stages(self) -> None:
        """Pipeline with multiple stages chains correctly."""
        pipeline = Pipeline([MockTransformStage(), MockTransformStage()])

        async def items() -> AsyncIterator[int]:
            for i in [1, 2, 3]:
                yield i

        results = []
        async for result in pipeline.execute(items()):
            results.append(result)

        # Each stage doubles, so 1->2->4, 2->4->8, 3->6->12
        assert results == [4, 8, 12]

    @pytest.mark.asyncio
    async def test_execute_tracks_progress(self) -> None:
        """Pipeline tracks progress during execution."""
        pipeline = Pipeline([MockPassthroughStage("fetch")])

        async def items() -> AsyncIterator[int]:
            for i in [1, 2, 3]:
                yield i

        results = []
        async for result in pipeline.execute(items()):
            results.append(result)

        progress = pipeline.progress
        assert progress.started_at is not None
        assert progress.completed_at is not None
        assert "fetch" in progress.stages
        assert progress.stages["fetch"].items_processed == 3

    @pytest.mark.asyncio
    async def test_execute_with_fail_fast(self) -> None:
        """Pipeline with fail_fast stops on first error."""
        config = PipelineConfig(fail_fast=True, retry_config=RetryConfig(max_retries=0))
        pipeline = Pipeline([MockFailingStage(fail_after=2)], config)

        async def items() -> AsyncIterator[int]:
            for i in range(10):
                yield i

        results = []
        with pytest.raises(PipelineError):
            async for result in pipeline.execute(items()):
                results.append(result)

        # Should have processed 2 items before failing
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_execute_without_fail_fast_continues(self) -> None:
        """Pipeline without fail_fast continues on errors."""
        config = PipelineConfig(fail_fast=False, retry_config=RetryConfig(max_retries=0))
        pipeline = Pipeline([MockFailingStage(fail_after=2)], config)

        async def items() -> AsyncIterator[int]:
            for i in range(5):
                yield i

        results = []
        async for result in pipeline.execute(items()):
            results.append(result)

        # Should have processed 2 items, rest failed
        assert len(results) == 2
        assert pipeline.progress.stages["failing"].items_failed > 0

    @pytest.mark.asyncio
    async def test_cancel_pipeline(self) -> None:
        """Pipeline can be cancelled."""
        pipeline = Pipeline([MockPassthroughStage()])

        async def items() -> AsyncIterator[int]:
            for i in range(1000):
                yield i

        results = []
        async for result in pipeline.execute(items()):
            results.append(result)
            if len(results) >= 5:
                await pipeline.cancel()
                break

        assert len(results) == 5
