# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Job management for tracking, persisting, and recovering long-running ingestion jobs.

This module provides:
- Job: Entity representing an ingestion job with status, progress, and error tracking
- JobStatus: Enum for job lifecycle states
- JobService: CRUD operations, status transitions, checkpointing, and cancellation
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    """Status values for ingestion jobs.

    Lifecycle: PENDING -> RUNNING -> COMPLETED
                              |-> FAILED
                              |-> CANCELLED
    """

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

    def is_terminal(self) -> bool:
        """Check if this status is a terminal state."""
        return self in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED)


# Valid status transitions
VALID_TRANSITIONS: dict[JobStatus, set[JobStatus]] = {
    JobStatus.PENDING: {JobStatus.RUNNING, JobStatus.CANCELLED},
    JobStatus.RUNNING: {JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED},
    JobStatus.COMPLETED: set(),  # Terminal state
    JobStatus.FAILED: {JobStatus.PENDING},  # Can retry
    JobStatus.CANCELLED: {JobStatus.PENDING},  # Can restart
}


class JobError(Exception):
    """Exception raised for job-related errors."""

    pass


class InvalidTransitionError(JobError):
    """Exception raised when an invalid status transition is attempted."""

    def __init__(self, current: JobStatus, target: JobStatus):
        self.current = current
        self.target = target
        super().__init__(
            f"Invalid transition from {current.value} to {target.value}. "
            f"Valid transitions: {[s.value for s in VALID_TRANSITIONS[current]]}"
        )


@dataclass
class JobProgress:
    """Progress tracking for a job.

    Attributes:
        current: Number of items processed.
        total: Total number of items to process.
        message: Human-readable progress message.
        stage: Current stage name (e.g., 'fetching', 'chunking', 'embedding').
        metadata: Additional stage-specific progress data.
    """

    current: int = 0
    total: int = 0
    message: str = ""
    stage: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def percentage(self) -> float:
        """Calculate progress as a percentage."""
        if self.total <= 0:
            return 0.0
        return min(100.0, (self.current / self.total) * 100.0)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "current": self.current,
            "total": self.total,
            "message": self.message,
            "stage": self.stage,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> JobProgress:
        """Create from dictionary."""
        return cls(
            current=data.get("current", 0),
            total=data.get("total", 0),
            message=data.get("message", ""),
            stage=data.get("stage", ""),
            metadata=data.get("metadata", {}),
        )


@dataclass
class Checkpoint:
    """Checkpoint data for job recovery.

    Stores the state needed to resume a job from a specific point.

    Attributes:
        stage: Stage name where the checkpoint was created.
        position: Position within the stage (e.g., item index).
        data: Stage-specific state data for resumption.
        created_at: When the checkpoint was created.
    """

    stage: str
    position: int
    data: dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "stage": self.stage,
            "position": self.position,
            "data": self.data,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Checkpoint:
        """Create from dictionary."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.now()

        return cls(
            stage=data.get("stage", ""),
            position=data.get("position", 0),
            data=data.get("data", {}),
            created_at=created_at,
        )


@dataclass
class Job:
    """Represents an ingestion job for processing content.

    Jobs track the lifecycle of content ingestion from source fetching
    through chunking, embedding, and indexing.

    Attributes:
        id: Unique identifier for this job.
        corpus_id: ID of the corpus being populated.
        status: Current job status.
        progress: Current progress information.
        created_at: When the job was created.
        started_at: When the job started running.
        completed_at: When the job finished (success, failure, or cancellation).
        error: Error message if the job failed.
        error_details: Detailed error information (stack trace, etc.).
        checkpoint: Last checkpoint for resumption.
        metadata: Additional job metadata.
    """

    id: str
    corpus_id: str
    status: JobStatus = JobStatus.PENDING
    progress: JobProgress = field(default_factory=JobProgress)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None
    error_details: str | None = None
    checkpoint: Checkpoint | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate job data after initialization."""
        if not self.id:
            raise ValueError("id cannot be empty")
        if not self.corpus_id:
            raise ValueError("corpus_id cannot be empty")

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"Job(id={self.id!r}, corpus_id={self.corpus_id!r}, "
            f"status={self.status.value!r})"
        )

    def can_transition_to(self, target: JobStatus) -> bool:
        """Check if transition to target status is valid."""
        return target in VALID_TRANSITIONS[self.status]

    def transition_to(self, target: JobStatus) -> None:
        """Transition to a new status.

        Args:
            target: The target status.

        Raises:
            InvalidTransitionError: If the transition is not allowed.
        """
        if not self.can_transition_to(target):
            raise InvalidTransitionError(self.status, target)

        self.status = target

        # Update timestamps based on new status
        if target == JobStatus.RUNNING:
            self.started_at = datetime.now()
        elif target.is_terminal():
            self.completed_at = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "corpus_id": self.corpus_id,
            "status": self.status.value,
            "progress": self.progress.to_dict(),
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
            "error_details": self.error_details,
            "checkpoint": self.checkpoint.to_dict() if self.checkpoint else None,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Job:
        """Create from dictionary."""
        # Parse datetime fields
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.now()

        started_at = data.get("started_at")
        if isinstance(started_at, str):
            started_at = datetime.fromisoformat(started_at)

        completed_at = data.get("completed_at")
        if isinstance(completed_at, str):
            completed_at = datetime.fromisoformat(completed_at)

        # Parse nested objects
        progress_data = data.get("progress", {})
        progress = JobProgress.from_dict(progress_data) if progress_data else JobProgress()

        checkpoint_data = data.get("checkpoint")
        checkpoint = Checkpoint.from_dict(checkpoint_data) if checkpoint_data else None

        return cls(
            id=data["id"],
            corpus_id=data["corpus_id"],
            status=JobStatus(data.get("status", "pending")),
            progress=progress,
            created_at=created_at,
            started_at=started_at,
            completed_at=completed_at,
            error=data.get("error"),
            error_details=data.get("error_details"),
            checkpoint=checkpoint,
            metadata=data.get("metadata", {}),
        )


class JobService:
    """Service for managing ingestion jobs.

    Provides CRUD operations, status transitions, checkpointing,
    and cancellation support. Uses an in-memory store by default,
    but can be extended for persistent storage.
    """

    def __init__(self) -> None:
        """Initialize the job service."""
        self._jobs: dict[str, Job] = {}

    def create(self, job_id: str, corpus_id: str, **metadata: Any) -> Job:
        """Create a new job.

        Args:
            job_id: Unique identifier for the job.
            corpus_id: ID of the corpus being populated.
            **metadata: Additional metadata for the job.

        Returns:
            The created Job.

        Raises:
            JobError: If a job with this ID already exists.
        """
        if job_id in self._jobs:
            raise JobError(f"Job with id '{job_id}' already exists")

        job = Job(id=job_id, corpus_id=corpus_id, metadata=dict(metadata))
        self._jobs[job_id] = job
        logger.info(f"Created job {job_id} for corpus {corpus_id}")
        return job

    def get(self, job_id: str) -> Job | None:
        """Get a job by ID.

        Args:
            job_id: The job ID to look up.

        Returns:
            The Job if found, None otherwise.
        """
        return self._jobs.get(job_id)

    def get_or_raise(self, job_id: str) -> Job:
        """Get a job by ID, raising if not found.

        Args:
            job_id: The job ID to look up.

        Returns:
            The Job.

        Raises:
            JobError: If the job is not found.
        """
        job = self.get(job_id)
        if job is None:
            raise JobError(f"Job with id '{job_id}' not found")
        return job

    def list(
        self,
        corpus_id: str | None = None,
        status: JobStatus | None = None,
        limit: int = 100,
    ) -> list[Job]:
        """List jobs with optional filtering.

        Args:
            corpus_id: Filter by corpus ID.
            status: Filter by status.
            limit: Maximum number of jobs to return.

        Returns:
            List of matching jobs, ordered by creation time (newest first).
        """
        jobs = list(self._jobs.values())

        if corpus_id is not None:
            jobs = [j for j in jobs if j.corpus_id == corpus_id]

        if status is not None:
            jobs = [j for j in jobs if j.status == status]

        # Sort by creation time, newest first
        jobs.sort(key=lambda j: j.created_at, reverse=True)

        return jobs[:limit]

    def update(self, job: Job) -> Job:
        """Update a job in storage.

        Args:
            job: The job to update.

        Returns:
            The updated job.

        Raises:
            JobError: If the job doesn't exist.
        """
        if job.id not in self._jobs:
            raise JobError(f"Job with id '{job.id}' not found")

        self._jobs[job.id] = job
        return job

    def delete(self, job_id: str) -> bool:
        """Delete a job.

        Args:
            job_id: The job ID to delete.

        Returns:
            True if deleted, False if not found.
        """
        if job_id in self._jobs:
            del self._jobs[job_id]
            logger.info(f"Deleted job {job_id}")
            return True
        return False

    def start(self, job_id: str) -> Job:
        """Start a job.

        Args:
            job_id: The job ID to start.

        Returns:
            The updated job.

        Raises:
            JobError: If the job is not found or cannot be started.
        """
        job = self.get_or_raise(job_id)
        job.transition_to(JobStatus.RUNNING)
        logger.info(f"Started job {job_id}")
        return self.update(job)

    def complete(self, job_id: str) -> Job:
        """Mark a job as completed.

        Args:
            job_id: The job ID to complete.

        Returns:
            The updated job.

        Raises:
            JobError: If the job is not found or cannot be completed.
        """
        job = self.get_or_raise(job_id)
        job.transition_to(JobStatus.COMPLETED)
        logger.info(f"Completed job {job_id}")
        return self.update(job)

    def fail(self, job_id: str, error: str, details: str | None = None) -> Job:
        """Mark a job as failed.

        Args:
            job_id: The job ID to fail.
            error: Error message.
            details: Detailed error information.

        Returns:
            The updated job.

        Raises:
            JobError: If the job is not found or cannot be failed.
        """
        job = self.get_or_raise(job_id)
        job.transition_to(JobStatus.FAILED)
        job.error = error
        job.error_details = details
        logger.error(f"Failed job {job_id}: {error}")
        return self.update(job)

    def cancel(self, job_id: str) -> Job:
        """Cancel a job.

        Args:
            job_id: The job ID to cancel.

        Returns:
            The updated job.

        Raises:
            JobError: If the job is not found or cannot be cancelled.
        """
        job = self.get_or_raise(job_id)
        job.transition_to(JobStatus.CANCELLED)
        logger.info(f"Cancelled job {job_id}")
        return self.update(job)

    def retry(self, job_id: str) -> Job:
        """Retry a failed or cancelled job.

        Args:
            job_id: The job ID to retry.

        Returns:
            The updated job.

        Raises:
            JobError: If the job is not found or cannot be retried.
        """
        job = self.get_or_raise(job_id)
        job.transition_to(JobStatus.PENDING)
        job.error = None
        job.error_details = None
        job.started_at = None
        job.completed_at = None
        logger.info(f"Retrying job {job_id}")
        return self.update(job)

    def update_progress(
        self,
        job_id: str,
        current: int,
        total: int,
        message: str = "",
        stage: str = "",
        **metadata: Any,
    ) -> Job:
        """Update job progress.

        Args:
            job_id: The job ID to update.
            current: Number of items processed.
            total: Total number of items.
            message: Progress message.
            stage: Current stage name.
            **metadata: Additional progress metadata.

        Returns:
            The updated job.

        Raises:
            JobError: If the job is not found.
        """
        job = self.get_or_raise(job_id)
        job.progress = JobProgress(
            current=current,
            total=total,
            message=message,
            stage=stage,
            metadata=dict(metadata),
        )
        return self.update(job)

    def checkpoint(
        self,
        job_id: str,
        stage: str,
        position: int,
        **data: Any,
    ) -> Job:
        """Create a checkpoint for job recovery.

        Args:
            job_id: The job ID to checkpoint.
            stage: Current stage name.
            position: Position within the stage.
            **data: Additional checkpoint data.

        Returns:
            The updated job.

        Raises:
            JobError: If the job is not found.
        """
        job = self.get_or_raise(job_id)
        job.checkpoint = Checkpoint(
            stage=stage,
            position=position,
            data=dict(data),
        )
        logger.debug(f"Checkpoint created for job {job_id} at {stage}:{position}")
        return self.update(job)

    def get_active_jobs(self) -> list[Job]:
        """Get all currently running jobs.

        Returns:
            List of running jobs.
        """
        return self.list(status=JobStatus.RUNNING, limit=1000)

    def get_pending_jobs(self) -> list[Job]:
        """Get all pending jobs.

        Returns:
            List of pending jobs.
        """
        return self.list(status=JobStatus.PENDING, limit=1000)

    def get_failed_jobs(self) -> list[Job]:
        """Get all failed jobs.

        Returns:
            List of failed jobs.
        """
        return self.list(status=JobStatus.FAILED, limit=1000)

    def get_jobs_for_corpus(self, corpus_id: str) -> list[Job]:
        """Get all jobs for a specific corpus.

        Args:
            corpus_id: The corpus ID to filter by.

        Returns:
            List of jobs for the corpus.
        """
        return self.list(corpus_id=corpus_id, limit=1000)

    def export_to_json(self) -> str:
        """Export all jobs to JSON string.

        Returns:
            JSON string of all jobs.
        """
        jobs_data = [job.to_dict() for job in self._jobs.values()]
        return json.dumps(jobs_data, indent=2)

    def import_from_json(self, json_str: str) -> int:
        """Import jobs from JSON string.

        Args:
            json_str: JSON string containing job data.

        Returns:
            Number of jobs imported.
        """
        jobs_data = json.loads(json_str)
        count = 0
        for data in jobs_data:
            job = Job.from_dict(data)
            self._jobs[job.id] = job
            count += 1
        logger.info(f"Imported {count} jobs")
        return count


# Module-level service instance for convenience
_default_service: JobService | None = None


def get_job_service() -> JobService:
    """Get the default job service instance.

    Returns:
        The default JobService.
    """
    global _default_service
    if _default_service is None:
        _default_service = JobService()
    return _default_service


def reset_job_service() -> None:
    """Reset the default job service instance.

    Useful for testing.
    """
    global _default_service
    _default_service = None
