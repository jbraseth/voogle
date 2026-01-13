# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for pipeline job management module."""

from datetime import datetime

import pytest

from voogle.pipeline.jobs import (
    Checkpoint,
    InvalidTransitionError,
    Job,
    JobError,
    JobProgress,
    JobService,
    JobStatus,
    VALID_TRANSITIONS,
    get_job_service,
    reset_job_service,
)

pytestmark = pytest.mark.unit


class TestJobStatus:
    """Tests for JobStatus enum."""

    def test_all_statuses_exist(self) -> None:
        """All expected job statuses are defined."""
        assert JobStatus.PENDING.value == "pending"
        assert JobStatus.RUNNING.value == "running"
        assert JobStatus.COMPLETED.value == "completed"
        assert JobStatus.FAILED.value == "failed"
        assert JobStatus.CANCELLED.value == "cancelled"

    def test_status_count(self) -> None:
        """Correct number of statuses are defined."""
        assert len(JobStatus) == 5

    def test_is_terminal_for_non_terminal_statuses(self) -> None:
        """Non-terminal statuses return False."""
        assert JobStatus.PENDING.is_terminal() is False
        assert JobStatus.RUNNING.is_terminal() is False

    def test_is_terminal_for_terminal_statuses(self) -> None:
        """Terminal statuses return True."""
        assert JobStatus.COMPLETED.is_terminal() is True
        assert JobStatus.FAILED.is_terminal() is True
        assert JobStatus.CANCELLED.is_terminal() is True


class TestJobProgress:
    """Tests for JobProgress dataclass."""

    def test_create_default_progress(self) -> None:
        """Default progress can be created."""
        progress = JobProgress()
        assert progress.current == 0
        assert progress.total == 0
        assert progress.message == ""
        assert progress.stage == ""
        assert progress.metadata == {}

    def test_create_custom_progress(self) -> None:
        """Custom progress can be created."""
        progress = JobProgress(
            current=50,
            total=100,
            message="Processing items",
            stage="embedding",
            metadata={"batch_size": 32},
        )
        assert progress.current == 50
        assert progress.total == 100
        assert progress.message == "Processing items"
        assert progress.stage == "embedding"
        assert progress.metadata == {"batch_size": 32}

    def test_percentage_calculation(self) -> None:
        """Percentage is calculated correctly."""
        progress = JobProgress(current=25, total=100)
        assert progress.percentage == 25.0

    def test_percentage_with_zero_total(self) -> None:
        """Percentage returns 0 when total is 0."""
        progress = JobProgress(current=50, total=0)
        assert progress.percentage == 0.0

    def test_percentage_capped_at_100(self) -> None:
        """Percentage is capped at 100."""
        progress = JobProgress(current=150, total=100)
        assert progress.percentage == 100.0

    def test_to_dict(self) -> None:
        """Progress can be converted to dict."""
        progress = JobProgress(
            current=10, total=20, message="Test", stage="fetch", metadata={"key": "val"}
        )
        result = progress.to_dict()
        assert result["current"] == 10
        assert result["total"] == 20
        assert result["message"] == "Test"
        assert result["stage"] == "fetch"
        assert result["metadata"] == {"key": "val"}

    def test_from_dict(self) -> None:
        """Progress can be created from dict."""
        data = {
            "current": 10,
            "total": 20,
            "message": "Test",
            "stage": "fetch",
            "metadata": {"key": "val"},
        }
        progress = JobProgress.from_dict(data)
        assert progress.current == 10
        assert progress.total == 20
        assert progress.message == "Test"
        assert progress.stage == "fetch"
        assert progress.metadata == {"key": "val"}

    def test_from_dict_with_defaults(self) -> None:
        """Progress from_dict uses defaults for missing fields."""
        progress = JobProgress.from_dict({})
        assert progress.current == 0
        assert progress.total == 0
        assert progress.message == ""
        assert progress.stage == ""
        assert progress.metadata == {}


class TestCheckpoint:
    """Tests for Checkpoint dataclass."""

    def test_create_checkpoint(self) -> None:
        """Checkpoint can be created."""
        checkpoint = Checkpoint(
            stage="chunking", position=42, data={"items_remaining": 10}
        )
        assert checkpoint.stage == "chunking"
        assert checkpoint.position == 42
        assert checkpoint.data == {"items_remaining": 10}
        assert isinstance(checkpoint.created_at, datetime)

    def test_to_dict(self) -> None:
        """Checkpoint can be converted to dict."""
        checkpoint = Checkpoint(stage="fetch", position=10, data={"url": "test.com"})
        result = checkpoint.to_dict()
        assert result["stage"] == "fetch"
        assert result["position"] == 10
        assert result["data"] == {"url": "test.com"}
        assert "created_at" in result

    def test_from_dict(self) -> None:
        """Checkpoint can be created from dict."""
        data = {
            "stage": "embed",
            "position": 5,
            "data": {"model": "sbert"},
            "created_at": "2025-01-01T12:00:00",
        }
        checkpoint = Checkpoint.from_dict(data)
        assert checkpoint.stage == "embed"
        assert checkpoint.position == 5
        assert checkpoint.data == {"model": "sbert"}
        assert checkpoint.created_at == datetime(2025, 1, 1, 12, 0, 0)


class TestJob:
    """Tests for Job dataclass."""

    def test_create_minimal_job(self) -> None:
        """Job can be created with minimal fields."""
        job = Job(id="test-1", corpus_id="corpus-1")
        assert job.id == "test-1"
        assert job.corpus_id == "corpus-1"
        assert job.status == JobStatus.PENDING
        assert isinstance(job.progress, JobProgress)
        assert isinstance(job.created_at, datetime)
        assert job.started_at is None
        assert job.completed_at is None
        assert job.error is None
        assert job.error_details is None
        assert job.checkpoint is None
        assert job.metadata == {}

    def test_create_full_job(self) -> None:
        """Job can be created with all fields."""
        progress = JobProgress(current=50, total=100)
        checkpoint = Checkpoint(stage="fetch", position=10, data={})
        job = Job(
            id="test-2",
            corpus_id="corpus-2",
            status=JobStatus.RUNNING,
            progress=progress,
            started_at=datetime.now(),
            error="Test error",
            error_details="Stack trace",
            checkpoint=checkpoint,
            metadata={"source": "test"},
        )
        assert job.id == "test-2"
        assert job.status == JobStatus.RUNNING
        assert job.progress.current == 50
        assert job.checkpoint is not None
        assert job.metadata == {"source": "test"}

    def test_empty_id_raises(self) -> None:
        """Empty id raises ValueError."""
        with pytest.raises(ValueError, match="id cannot be empty"):
            Job(id="", corpus_id="corpus-1")

    def test_empty_corpus_id_raises(self) -> None:
        """Empty corpus_id raises ValueError."""
        with pytest.raises(ValueError, match="corpus_id cannot be empty"):
            Job(id="test-1", corpus_id="")

    def test_repr(self) -> None:
        """Job has a useful repr."""
        job = Job(id="test-1", corpus_id="c1", status=JobStatus.RUNNING)
        result = repr(job)
        assert "test-1" in result
        assert "c1" in result
        assert "running" in result

    def test_can_transition_to_valid(self) -> None:
        """can_transition_to returns True for valid transitions."""
        job = Job(id="test", corpus_id="c1")
        assert job.can_transition_to(JobStatus.RUNNING) is True
        assert job.can_transition_to(JobStatus.CANCELLED) is True

    def test_can_transition_to_invalid(self) -> None:
        """can_transition_to returns False for invalid transitions."""
        job = Job(id="test", corpus_id="c1")
        assert job.can_transition_to(JobStatus.COMPLETED) is False
        assert job.can_transition_to(JobStatus.FAILED) is False

    def test_transition_to_running(self) -> None:
        """Transition to RUNNING sets started_at."""
        job = Job(id="test", corpus_id="c1")
        job.transition_to(JobStatus.RUNNING)
        assert job.status == JobStatus.RUNNING
        assert job.started_at is not None

    def test_transition_to_completed(self) -> None:
        """Transition to COMPLETED sets completed_at."""
        job = Job(id="test", corpus_id="c1")
        job.transition_to(JobStatus.RUNNING)
        job.transition_to(JobStatus.COMPLETED)
        assert job.status == JobStatus.COMPLETED
        assert job.completed_at is not None

    def test_transition_to_invalid_raises(self) -> None:
        """Invalid transition raises InvalidTransitionError."""
        job = Job(id="test", corpus_id="c1")
        with pytest.raises(InvalidTransitionError) as exc_info:
            job.transition_to(JobStatus.COMPLETED)
        assert exc_info.value.current == JobStatus.PENDING
        assert exc_info.value.target == JobStatus.COMPLETED

    def test_to_dict(self) -> None:
        """Job can be converted to dict."""
        job = Job(id="test", corpus_id="c1", metadata={"key": "val"})
        result = job.to_dict()
        assert result["id"] == "test"
        assert result["corpus_id"] == "c1"
        assert result["status"] == "pending"
        assert result["metadata"] == {"key": "val"}
        assert "created_at" in result
        assert "progress" in result

    def test_from_dict(self) -> None:
        """Job can be created from dict."""
        data = {
            "id": "test-1",
            "corpus_id": "c1",
            "status": "running",
            "created_at": "2025-01-01T10:00:00",
            "started_at": "2025-01-01T10:01:00",
            "progress": {"current": 10, "total": 100},
            "metadata": {"source": "test"},
        }
        job = Job.from_dict(data)
        assert job.id == "test-1"
        assert job.corpus_id == "c1"
        assert job.status == JobStatus.RUNNING
        assert job.progress.current == 10
        assert job.metadata == {"source": "test"}


class TestValidTransitions:
    """Tests for VALID_TRANSITIONS map."""

    def test_pending_transitions(self) -> None:
        """PENDING can transition to RUNNING or CANCELLED."""
        assert VALID_TRANSITIONS[JobStatus.PENDING] == {
            JobStatus.RUNNING,
            JobStatus.CANCELLED,
        }

    def test_running_transitions(self) -> None:
        """RUNNING can transition to COMPLETED, FAILED, or CANCELLED."""
        assert VALID_TRANSITIONS[JobStatus.RUNNING] == {
            JobStatus.COMPLETED,
            JobStatus.FAILED,
            JobStatus.CANCELLED,
        }

    def test_completed_transitions(self) -> None:
        """COMPLETED is terminal and has no transitions."""
        assert VALID_TRANSITIONS[JobStatus.COMPLETED] == set()

    def test_failed_transitions(self) -> None:
        """FAILED can transition back to PENDING for retry."""
        assert VALID_TRANSITIONS[JobStatus.FAILED] == {JobStatus.PENDING}

    def test_cancelled_transitions(self) -> None:
        """CANCELLED can transition back to PENDING for restart."""
        assert VALID_TRANSITIONS[JobStatus.CANCELLED] == {JobStatus.PENDING}


class TestJobService:
    """Tests for JobService class."""

    @pytest.fixture
    def service(self) -> JobService:
        """Create a fresh JobService for each test."""
        return JobService()

    def test_create_job(self, service: JobService) -> None:
        """create() creates and stores a job."""
        job = service.create("job-1", "corpus-1")
        assert job.id == "job-1"
        assert job.corpus_id == "corpus-1"
        assert job.status == JobStatus.PENDING

    def test_create_job_with_metadata(self, service: JobService) -> None:
        """create() accepts metadata kwargs."""
        job = service.create("job-1", "corpus-1", source="test", batch=10)
        assert job.metadata == {"source": "test", "batch": 10}

    def test_create_duplicate_raises(self, service: JobService) -> None:
        """create() raises JobError for duplicate ID."""
        service.create("job-1", "corpus-1")
        with pytest.raises(JobError, match="already exists"):
            service.create("job-1", "corpus-2")

    def test_get_existing_job(self, service: JobService) -> None:
        """get() returns existing job."""
        service.create("job-1", "corpus-1")
        job = service.get("job-1")
        assert job is not None
        assert job.id == "job-1"

    def test_get_nonexistent_job(self, service: JobService) -> None:
        """get() returns None for nonexistent job."""
        job = service.get("nonexistent")
        assert job is None

    def test_get_or_raise_existing(self, service: JobService) -> None:
        """get_or_raise() returns existing job."""
        service.create("job-1", "corpus-1")
        job = service.get_or_raise("job-1")
        assert job.id == "job-1"

    def test_get_or_raise_nonexistent(self, service: JobService) -> None:
        """get_or_raise() raises JobError for nonexistent job."""
        with pytest.raises(JobError, match="not found"):
            service.get_or_raise("nonexistent")

    def test_list_all_jobs(self, service: JobService) -> None:
        """list() returns all jobs."""
        service.create("job-1", "corpus-1")
        service.create("job-2", "corpus-1")
        jobs = service.list()
        assert len(jobs) == 2

    def test_list_by_corpus(self, service: JobService) -> None:
        """list() can filter by corpus_id."""
        service.create("job-1", "corpus-1")
        service.create("job-2", "corpus-2")
        jobs = service.list(corpus_id="corpus-1")
        assert len(jobs) == 1
        assert jobs[0].corpus_id == "corpus-1"

    def test_list_by_status(self, service: JobService) -> None:
        """list() can filter by status."""
        service.create("job-1", "corpus-1")
        job2 = service.create("job-2", "corpus-1")
        service.start(job2.id)
        jobs = service.list(status=JobStatus.RUNNING)
        assert len(jobs) == 1
        assert jobs[0].id == "job-2"

    def test_list_respects_limit(self, service: JobService) -> None:
        """list() respects limit parameter."""
        for i in range(10):
            service.create(f"job-{i}", "corpus-1")
        jobs = service.list(limit=5)
        assert len(jobs) == 5

    def test_update_job(self, service: JobService) -> None:
        """update() saves changes to job."""
        job = service.create("job-1", "corpus-1")
        job.metadata["updated"] = True
        service.update(job)
        retrieved = service.get("job-1")
        assert retrieved is not None
        assert retrieved.metadata["updated"] is True

    def test_update_nonexistent_raises(self, service: JobService) -> None:
        """update() raises JobError for nonexistent job."""
        job = Job(id="nonexistent", corpus_id="c1")
        with pytest.raises(JobError, match="not found"):
            service.update(job)

    def test_delete_existing_job(self, service: JobService) -> None:
        """delete() removes existing job."""
        service.create("job-1", "corpus-1")
        result = service.delete("job-1")
        assert result is True
        assert service.get("job-1") is None

    def test_delete_nonexistent_job(self, service: JobService) -> None:
        """delete() returns False for nonexistent job."""
        result = service.delete("nonexistent")
        assert result is False

    def test_start_job(self, service: JobService) -> None:
        """start() transitions job to RUNNING."""
        service.create("job-1", "corpus-1")
        job = service.start("job-1")
        assert job.status == JobStatus.RUNNING
        assert job.started_at is not None

    def test_complete_job(self, service: JobService) -> None:
        """complete() transitions job to COMPLETED."""
        service.create("job-1", "corpus-1")
        service.start("job-1")
        job = service.complete("job-1")
        assert job.status == JobStatus.COMPLETED
        assert job.completed_at is not None

    def test_fail_job(self, service: JobService) -> None:
        """fail() transitions job to FAILED with error info."""
        service.create("job-1", "corpus-1")
        service.start("job-1")
        job = service.fail("job-1", "Something went wrong", "Stack trace here")
        assert job.status == JobStatus.FAILED
        assert job.error == "Something went wrong"
        assert job.error_details == "Stack trace here"

    def test_cancel_job(self, service: JobService) -> None:
        """cancel() transitions job to CANCELLED."""
        service.create("job-1", "corpus-1")
        service.start("job-1")
        job = service.cancel("job-1")
        assert job.status == JobStatus.CANCELLED
        assert job.completed_at is not None

    def test_retry_failed_job(self, service: JobService) -> None:
        """retry() resets failed job to PENDING."""
        service.create("job-1", "corpus-1")
        service.start("job-1")
        service.fail("job-1", "Error")
        job = service.retry("job-1")
        assert job.status == JobStatus.PENDING
        assert job.error is None
        assert job.error_details is None
        assert job.started_at is None
        assert job.completed_at is None

    def test_update_progress(self, service: JobService) -> None:
        """update_progress() updates job progress."""
        service.create("job-1", "corpus-1")
        service.start("job-1")
        job = service.update_progress(
            "job-1",
            current=50,
            total=100,
            message="Half done",
            stage="embedding",
            batch_size=32,
        )
        assert job.progress.current == 50
        assert job.progress.total == 100
        assert job.progress.message == "Half done"
        assert job.progress.stage == "embedding"
        assert job.progress.metadata == {"batch_size": 32}

    def test_checkpoint(self, service: JobService) -> None:
        """checkpoint() creates a checkpoint."""
        service.create("job-1", "corpus-1")
        service.start("job-1")
        job = service.checkpoint(
            "job-1", stage="chunking", position=42, items_remaining=58
        )
        assert job.checkpoint is not None
        assert job.checkpoint.stage == "chunking"
        assert job.checkpoint.position == 42
        assert job.checkpoint.data == {"items_remaining": 58}

    def test_get_active_jobs(self, service: JobService) -> None:
        """get_active_jobs() returns running jobs."""
        service.create("job-1", "corpus-1")
        service.create("job-2", "corpus-1")
        service.start("job-1")
        active = service.get_active_jobs()
        assert len(active) == 1
        assert active[0].id == "job-1"

    def test_get_pending_jobs(self, service: JobService) -> None:
        """get_pending_jobs() returns pending jobs."""
        service.create("job-1", "corpus-1")
        service.create("job-2", "corpus-1")
        service.start("job-2")
        pending = service.get_pending_jobs()
        assert len(pending) == 1
        assert pending[0].id == "job-1"

    def test_get_failed_jobs(self, service: JobService) -> None:
        """get_failed_jobs() returns failed jobs."""
        service.create("job-1", "corpus-1")
        service.create("job-2", "corpus-1")
        service.start("job-1")
        service.fail("job-1", "Error")
        failed = service.get_failed_jobs()
        assert len(failed) == 1
        assert failed[0].id == "job-1"

    def test_get_jobs_for_corpus(self, service: JobService) -> None:
        """get_jobs_for_corpus() returns jobs for specific corpus."""
        service.create("job-1", "corpus-1")
        service.create("job-2", "corpus-2")
        service.create("job-3", "corpus-1")
        jobs = service.get_jobs_for_corpus("corpus-1")
        assert len(jobs) == 2
        assert all(j.corpus_id == "corpus-1" for j in jobs)

    def test_export_import_json(self, service: JobService) -> None:
        """Jobs can be exported and imported via JSON."""
        service.create("job-1", "corpus-1", source="test")
        service.create("job-2", "corpus-2")
        service.start("job-1")

        json_str = service.export_to_json()

        # Create new service and import
        new_service = JobService()
        count = new_service.import_from_json(json_str)

        assert count == 2
        job1 = new_service.get("job-1")
        assert job1 is not None
        assert job1.status == JobStatus.RUNNING
        assert job1.metadata == {"source": "test"}


class TestDefaultJobService:
    """Tests for module-level job service singleton."""

    def teardown_method(self) -> None:
        """Reset the singleton after each test."""
        reset_job_service()

    def test_get_job_service_returns_singleton(self) -> None:
        """get_job_service() returns same instance."""
        service1 = get_job_service()
        service2 = get_job_service()
        assert service1 is service2

    def test_reset_job_service(self) -> None:
        """reset_job_service() creates new instance."""
        service1 = get_job_service()
        service1.create("job-1", "corpus-1")
        reset_job_service()
        service2 = get_job_service()
        assert service2.get("job-1") is None


class TestInvalidTransitionError:
    """Tests for InvalidTransitionError exception."""

    def test_error_message(self) -> None:
        """Error message contains useful information."""
        error = InvalidTransitionError(JobStatus.PENDING, JobStatus.COMPLETED)
        assert "pending" in str(error)
        assert "completed" in str(error)
        assert "Invalid transition" in str(error)

    def test_error_attributes(self) -> None:
        """Error has current and target attributes."""
        error = InvalidTransitionError(JobStatus.RUNNING, JobStatus.PENDING)
        assert error.current == JobStatus.RUNNING
        assert error.target == JobStatus.PENDING
