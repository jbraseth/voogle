# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for job_manager module."""
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from voogle.job_manager import (
    DEFAULT_RETRY_DELAYS,
    MAX_RETRIES,
    JobInfo,
    JobStatus,
    clear_job_progress,
    get_job_progress,
    get_retry_config,
    set_job_progress,
)

pytestmark = pytest.mark.unit


class TestRetryConfig:
    """Tests for retry configuration."""

    @pytest.mark.description("Default retry config uses correct values")
    def test_default_config(self) -> None:
        retry = get_retry_config()
        assert retry.max == MAX_RETRIES
        assert retry.intervals == DEFAULT_RETRY_DELAYS

    @pytest.mark.description("Custom max retries is respected")
    def test_custom_max_retries(self) -> None:
        retry = get_retry_config(max_retries=5)
        assert retry.max == 5

    @pytest.mark.description("Custom delays are respected")
    def test_custom_delays(self) -> None:
        custom_delays = [10, 20, 30]
        retry = get_retry_config(delays=custom_delays)
        assert retry.intervals == custom_delays

    @pytest.mark.description("Default delays are 1min, 5min, 15min")
    def test_default_delay_values(self) -> None:
        assert DEFAULT_RETRY_DELAYS == [60, 300, 900]


class TestJobInfo:
    """Tests for JobInfo dataclass."""

    @pytest.mark.description("JobInfo stores all fields correctly")
    def test_job_info_fields(self) -> None:
        now = datetime.now(timezone.utc)
        info = JobInfo(
            job_id="test-123",
            status=JobStatus.STARTED,
            func_name="test_func",
            enqueued_at=now,
            started_at=now,
            ended_at=None,
            exc_info=None,
            retries_left=2,
            meta={"key": "value"},
        )
        assert info.job_id == "test-123"
        assert info.status == JobStatus.STARTED
        assert info.func_name == "test_func"
        assert info.enqueued_at == now
        assert info.started_at == now
        assert info.ended_at is None
        assert info.exc_info is None
        assert info.retries_left == 2
        assert info.meta == {"key": "value"}


class TestJobStatus:
    """Tests for JobStatus enum."""

    @pytest.mark.description("JobStatus has expected values")
    def test_status_values(self) -> None:
        assert JobStatus.QUEUED.value == "queued"
        assert JobStatus.STARTED.value == "started"
        assert JobStatus.FINISHED.value == "finished"
        assert JobStatus.FAILED.value == "failed"
        assert JobStatus.DEFERRED.value == "deferred"
        assert JobStatus.SCHEDULED.value == "scheduled"


class TestJobProgress:
    """Tests for job progress tracking."""

    @pytest.mark.description("set_job_progress stores progress in Redis")
    def test_set_progress(self) -> None:
        mock_redis = MagicMock()
        with patch("voogle.job_manager.get_redis_connection", return_value=mock_redis):
            set_job_progress("job-123", current=50, total=100, message="Halfway done")

        # Verify hset was called with correct key
        mock_redis.hset.assert_called_once()
        call_args = mock_redis.hset.call_args
        assert call_args.kwargs["mapping"]["current"] == 50
        assert call_args.kwargs["mapping"]["total"] == 100
        assert call_args.kwargs["mapping"]["message"] == "Halfway done"
        # Also verify expire was called (24 hour TTL)
        mock_redis.expire.assert_called_once()

    @pytest.mark.description("get_job_progress returns None when not found")
    def test_get_progress_not_found(self) -> None:
        mock_redis = MagicMock()
        mock_redis.hgetall.return_value = {}
        with patch("voogle.job_manager.get_redis_connection", return_value=mock_redis):
            result = get_job_progress("nonexistent-job")
        assert result is None

    @pytest.mark.description("get_job_progress returns progress dict when found")
    def test_get_progress_found(self) -> None:
        mock_redis = MagicMock()
        mock_redis.hgetall.return_value = {
            b"current": b"50",
            b"total": b"100",
            b"message": b"Halfway done",
            b"updated_at": b"2025-01-01T12:00:00+00:00",
        }
        with patch("voogle.job_manager.get_redis_connection", return_value=mock_redis):
            result = get_job_progress("job-123")

        assert result is not None
        assert result["current"] == 50
        assert result["total"] == 100
        assert result["message"] == "Halfway done"
        assert result["updated_at"] == "2025-01-01T12:00:00+00:00"

    @pytest.mark.description("clear_job_progress deletes progress from Redis")
    def test_clear_progress(self) -> None:
        mock_redis = MagicMock()
        with patch("voogle.job_manager.get_redis_connection", return_value=mock_redis):
            clear_job_progress("job-123")

        mock_redis.delete.assert_called_once()
        call_args = mock_redis.delete.call_args
        assert "voogle:job_progress:job-123" in call_args.args


class TestEnqueueWithRetry:
    """Tests for enqueue_with_retry function."""

    @pytest.mark.description("enqueue_with_retry sets default retry config")
    def test_enqueue_with_default_retry(self) -> None:
        mock_queue = MagicMock()
        mock_job = MagicMock()
        mock_job.id = "test-job-id"
        mock_queue.enqueue.return_value = mock_job

        with patch("voogle.job_manager.settings") as mock_settings:
            mock_settings.queue = mock_queue
            from voogle.job_manager import enqueue_with_retry

            def test_func() -> None:
                pass

            job = enqueue_with_retry(test_func, job_timeout="10m")

        assert job.id == "test-job-id"
        mock_queue.enqueue.assert_called_once()
        call_kwargs = mock_queue.enqueue.call_args.kwargs
        assert call_kwargs["job_timeout"] == "10m"
        assert call_kwargs["retry"].max == MAX_RETRIES

    @pytest.mark.description("enqueue_with_retry passes description to queue")
    def test_enqueue_with_description(self) -> None:
        mock_queue = MagicMock()
        mock_job = MagicMock()
        mock_job.id = "test-job-id"
        mock_queue.enqueue.return_value = mock_job

        with patch("voogle.job_manager.settings") as mock_settings:
            mock_settings.queue = mock_queue
            from voogle.job_manager import enqueue_with_retry

            def test_func() -> None:
                pass

            enqueue_with_retry(test_func, description="Test job description")

        call_kwargs = mock_queue.enqueue.call_args.kwargs
        assert call_kwargs["description"] == "Test job description"
