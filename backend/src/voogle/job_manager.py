# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Job management utilities for RQ worker reliability.

Provides retry configuration, dead letter queue handling, job progress tracking,
and utilities for monitoring and recovering failed jobs.
"""
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional

import redis
from rq import Queue, Retry
from rq.job import Job
from rq.registry import FailedJobRegistry, FinishedJobRegistry, StartedJobRegistry

from voogle import settings

logger = logging.getLogger(__name__)

# Retry intervals: 1 minute, 5 minutes, 15 minutes
DEFAULT_RETRY_DELAYS = [60, 300, 900]
MAX_RETRIES = 3


class JobStatus(str, Enum):
    """Job status values."""

    QUEUED = "queued"
    STARTED = "started"
    FINISHED = "finished"
    FAILED = "failed"
    DEFERRED = "deferred"
    SCHEDULED = "scheduled"


@dataclass
class JobInfo:
    """Information about a job for monitoring."""

    job_id: str
    status: JobStatus
    func_name: str
    enqueued_at: Optional[datetime]
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    exc_info: Optional[str]
    retries_left: int
    meta: dict[str, Any]


def get_retry_config(
    max_retries: int = MAX_RETRIES,
    delays: Optional[list[int]] = None,
) -> Retry:
    """Create RQ Retry configuration with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts.
        delays: List of delay intervals in seconds between retries.
            Defaults to [60, 300, 900] (1min, 5min, 15min).

    Returns:
        RQ Retry object configured with the specified parameters.
    """
    if delays is None:
        delays = DEFAULT_RETRY_DELAYS

    return Retry(max=max_retries, interval=delays)


def enqueue_with_retry(
    func: Callable[..., Any],
    *args: Any,
    job_timeout: str = "10m",
    retry_config: Optional[Retry] = None,
    description: Optional[str] = None,
    **kwargs: Any,
) -> Job:
    """Enqueue a job with automatic retry on failure.

    Args:
        func: The function to execute.
        *args: Positional arguments to pass to the function.
        job_timeout: Maximum time for job execution.
        retry_config: Custom retry configuration, or None for defaults.
        description: Optional human-readable job description.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        The enqueued Job object.
    """
    if retry_config is None:
        retry_config = get_retry_config()

    job = settings.queue.enqueue(
        func,
        *args,
        job_timeout=job_timeout,
        retry=retry_config,
        description=description,
        **kwargs,
    )

    logger.info(
        f"enqueued job {job.id} for {func.__name__} with "
        f"max_retries={retry_config.max}, timeout={job_timeout}"
    )
    return job


def get_redis_connection() -> redis.Redis:
    """Get the Redis connection used by the queue."""
    return redis.Redis(settings.settings.redis_host)


def get_queue() -> Queue:
    """Get the main job queue."""
    return settings.queue


def get_failed_job_registry() -> FailedJobRegistry:
    """Get the registry containing failed jobs (dead letter queue)."""
    return FailedJobRegistry(queue=get_queue())


def get_finished_job_registry() -> FinishedJobRegistry:
    """Get the registry containing finished jobs."""
    return FinishedJobRegistry(queue=get_queue())


def get_started_job_registry() -> StartedJobRegistry:
    """Get the registry containing currently running jobs."""
    return StartedJobRegistry(queue=get_queue())


def get_job_info(job_id: str) -> Optional[JobInfo]:
    """Get detailed information about a job.

    Args:
        job_id: The job ID to look up.

    Returns:
        JobInfo object if job exists, None otherwise.
    """
    try:
        job = Job.fetch(job_id, connection=get_redis_connection())
    except Exception:
        return None

    status_map = {
        "queued": JobStatus.QUEUED,
        "started": JobStatus.STARTED,
        "finished": JobStatus.FINISHED,
        "failed": JobStatus.FAILED,
        "deferred": JobStatus.DEFERRED,
        "scheduled": JobStatus.SCHEDULED,
    }

    return JobInfo(
        job_id=job.id,
        status=status_map.get(job.get_status(), JobStatus.QUEUED),
        func_name=job.func_name or "unknown",
        enqueued_at=job.enqueued_at,
        started_at=job.started_at,
        ended_at=job.ended_at,
        exc_info=job.exc_info,
        retries_left=getattr(job, "retries_left", None) or 0,
        meta=job.meta or {},
    )


def list_failed_jobs(limit: int = 100) -> list[JobInfo]:
    """List all jobs in the dead letter queue.

    Args:
        limit: Maximum number of jobs to return.

    Returns:
        List of JobInfo objects for failed jobs.
    """
    registry = get_failed_job_registry()
    failed_jobs = []

    for job_id in registry.get_job_ids()[:limit]:
        info = get_job_info(job_id)
        if info:
            failed_jobs.append(info)

    return failed_jobs


def list_active_jobs(limit: int = 100) -> list[JobInfo]:
    """List currently running jobs.

    Args:
        limit: Maximum number of jobs to return.

    Returns:
        List of JobInfo objects for active jobs.
    """
    registry = get_started_job_registry()
    active_jobs = []

    for job_id in registry.get_job_ids()[:limit]:
        info = get_job_info(job_id)
        if info:
            active_jobs.append(info)

    return active_jobs


def list_queued_jobs(limit: int = 100) -> list[JobInfo]:
    """List jobs waiting in the queue.

    Args:
        limit: Maximum number of jobs to return.

    Returns:
        List of JobInfo objects for queued jobs.
    """
    queue = get_queue()
    queued_jobs = []

    for job in queue.jobs[:limit]:
        info = get_job_info(job.id)
        if info:
            queued_jobs.append(info)

    return queued_jobs


def retry_failed_job(job_id: str) -> bool:
    """Move a failed job back to the queue for retry.

    Args:
        job_id: The job ID to retry.

    Returns:
        True if job was successfully requeued, False otherwise.
    """
    try:
        registry = get_failed_job_registry()
        job = Job.fetch(job_id, connection=get_redis_connection())

        # Re-enqueue with fresh retry config
        registry.remove(job)
        job.requeue()

        logger.info(f"requeued failed job {job_id}")
        return True
    except Exception:
        logger.error(f"failed to retry job {job_id}", exc_info=True)
        return False


def retry_all_failed_jobs() -> tuple[int, int]:
    """Retry all jobs in the dead letter queue.

    Returns:
        Tuple of (successful_count, failed_count).
    """
    registry = get_failed_job_registry()
    job_ids = registry.get_job_ids()

    success = 0
    failed = 0

    for job_id in job_ids:
        if retry_failed_job(job_id):
            success += 1
        else:
            failed += 1

    logger.info(f"retried {success} failed jobs, {failed} could not be retried")
    return success, failed


def delete_failed_job(job_id: str) -> bool:
    """Permanently delete a failed job.

    Args:
        job_id: The job ID to delete.

    Returns:
        True if job was deleted, False otherwise.
    """
    try:
        registry = get_failed_job_registry()
        job = Job.fetch(job_id, connection=get_redis_connection())
        registry.remove(job)
        job.delete()
        logger.info(f"deleted failed job {job_id}")
        return True
    except Exception:
        logger.error(f"failed to delete job {job_id}", exc_info=True)
        return False


def clear_failed_jobs() -> int:
    """Delete all jobs in the dead letter queue.

    Returns:
        Number of jobs deleted.
    """
    registry = get_failed_job_registry()
    job_ids = registry.get_job_ids()
    count = 0

    for job_id in job_ids:
        if delete_failed_job(job_id):
            count += 1

    logger.info(f"cleared {count} failed jobs")
    return count


def get_queue_stats() -> dict[str, int]:
    """Get statistics about the job queue.

    Returns:
        Dictionary with queue statistics.
    """
    queue = get_queue()
    return {
        "queued": len(queue),
        "started": len(get_started_job_registry()),
        "finished": len(get_finished_job_registry()),
        "failed": len(get_failed_job_registry()),
    }


# Progress tracking utilities
PROGRESS_KEY_PREFIX = "voogle:job_progress:"


def set_job_progress(job_id: str, current: int, total: int, message: str = "") -> None:
    """Update progress for a running job.

    Args:
        job_id: The job ID.
        current: Current progress value.
        total: Total expected value.
        message: Optional progress message.
    """
    conn = get_redis_connection()
    key = f"{PROGRESS_KEY_PREFIX}{job_id}"
    conn.hset(
        key,
        mapping={
            "current": current,
            "total": total,
            "message": message,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    # Expire progress data after 24 hours
    conn.expire(key, 86400)


def get_job_progress(job_id: str) -> Optional[dict[str, Any]]:
    """Get progress for a job.

    Args:
        job_id: The job ID.

    Returns:
        Progress dictionary or None if not found.
    """
    conn = get_redis_connection()
    key = f"{PROGRESS_KEY_PREFIX}{job_id}"
    data: dict[bytes, bytes] = conn.hgetall(key)  # type: ignore[assignment]

    if not data:
        return None

    # Redis returns bytes, decode them
    return {
        "current": int(data.get(b"current", b"0")),
        "total": int(data.get(b"total", b"0")),
        "message": data.get(b"message", b"").decode(),
        "updated_at": data.get(b"updated_at", b"").decode(),
    }


def clear_job_progress(job_id: str) -> None:
    """Clear progress data for a job.

    Args:
        job_id: The job ID.
    """
    conn = get_redis_connection()
    key = f"{PROGRESS_KEY_PREFIX}{job_id}"
    conn.delete(key)
