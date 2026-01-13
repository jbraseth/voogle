# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for MCP get_ingestion_status tool."""

from unittest.mock import MagicMock

import pytest

from voogle.mcp.tools.ingest import (
    GetIngestionStatusTool,
    IngestionStatusInput,
    IngestionStatusOutput,
    get_ingestion_status_tool,
)
from voogle.pipeline.jobs import Job, JobProgress, JobService, JobStatus

pytestmark = pytest.mark.unit


class TestIngestionStatusInput:
    """Tests for IngestionStatusInput dataclass."""

    @pytest.mark.description("IngestionStatusInput with job_id")
    def test_input_structure(self) -> None:
        input_data = IngestionStatusInput(job_id="ingest-abc123")
        assert input_data.job_id == "ingest-abc123"


class TestIngestionStatusOutput:
    """Tests for IngestionStatusOutput dataclass."""

    @pytest.mark.description("IngestionStatusOutput structure")
    def test_output_structure(self) -> None:
        output = IngestionStatusOutput(
            job_id="ingest-abc123",
            status="running",
            progress_percentage=50.0,
            documents_processed=5,
            total_documents=10,
            errors=[],
            message="Ingestion in progress.",
        )
        assert output.job_id == "ingest-abc123"
        assert output.status == "running"
        assert output.progress_percentage == 50.0
        assert output.documents_processed == 5
        assert output.total_documents == 10
        assert output.errors == []
        assert output.message == "Ingestion in progress."

    @pytest.mark.description("IngestionStatusOutput with errors")
    def test_output_with_errors(self) -> None:
        output = IngestionStatusOutput(
            job_id="ingest-abc123",
            status="failed",
            progress_percentage=25.0,
            documents_processed=2,
            total_documents=8,
            errors=["Connection timeout", "Invalid format"],
            message="Ingestion failed.",
        )
        assert output.status == "failed"
        assert len(output.errors) == 2
        assert "Connection timeout" in output.errors


class TestGetIngestionStatusToolBasic:
    """Basic tests for GetIngestionStatusTool."""

    @pytest.mark.description("get_ingestion_status_tool has correct name and description")
    def test_tool_metadata(self) -> None:
        tool = GetIngestionStatusTool()
        assert tool.name == "get_ingestion_status"
        assert "status" in tool.description.lower()
        assert "progress" in tool.description.lower()

    @pytest.mark.description("get_ingestion_status_tool has valid input schema")
    def test_input_schema(self) -> None:
        tool = GetIngestionStatusTool()
        schema = tool.input_schema
        assert schema["type"] == "object"
        assert "job_id" in schema["properties"]
        assert "job_id" in schema["required"]

    @pytest.mark.description("get_ingestion_status_tool input_schema job_id is string")
    def test_input_schema_job_id_type(self) -> None:
        schema = get_ingestion_status_tool.input_schema
        assert schema["properties"]["job_id"]["type"] == "string"
        assert schema["properties"]["job_id"]["minLength"] == 1

    @pytest.mark.description("module-level get_ingestion_status_tool is GetIngestionStatusTool instance")
    def test_module_level_instance(self) -> None:
        assert isinstance(get_ingestion_status_tool, GetIngestionStatusTool)


class TestGetIngestionStatusToolValidation:
    """Tests for GetIngestionStatusTool input validation."""

    @pytest.fixture
    def mock_job_service(self) -> MagicMock:
        """Create a mock JobService."""
        return MagicMock(spec=JobService)

    @pytest.mark.description("get_ingestion_status_tool raises ValueError for empty job_id")
    def test_empty_job_id(self, mock_job_service: MagicMock) -> None:
        tool = GetIngestionStatusTool(job_service=mock_job_service)
        with pytest.raises(ValueError, match="job_id cannot be empty"):
            tool(job_id="")

    @pytest.mark.description("get_ingestion_status_tool raises ValueError for whitespace job_id")
    def test_whitespace_job_id(self, mock_job_service: MagicMock) -> None:
        tool = GetIngestionStatusTool(job_service=mock_job_service)
        with pytest.raises(ValueError, match="job_id cannot be empty"):
            tool(job_id="   ")


class TestGetIngestionStatusToolExecution:
    """Tests for GetIngestionStatusTool execution with mocked JobService."""

    @pytest.fixture
    def mock_job_service(self) -> MagicMock:
        """Create a mock JobService."""
        return MagicMock(spec=JobService)

    @pytest.fixture
    def pending_job(self) -> Job:
        """Create a pending job."""
        return Job(
            id="ingest-abc123",
            corpus_id="test-corpus",
            status=JobStatus.PENDING,
            progress=JobProgress(current=0, total=10),
        )

    @pytest.fixture
    def running_job(self) -> Job:
        """Create a running job with progress."""
        return Job(
            id="ingest-def456",
            corpus_id="test-corpus",
            status=JobStatus.RUNNING,
            progress=JobProgress(current=5, total=10, stage="embedding"),
        )

    @pytest.fixture
    def completed_job(self) -> Job:
        """Create a completed job."""
        return Job(
            id="ingest-ghi789",
            corpus_id="test-corpus",
            status=JobStatus.COMPLETED,
            progress=JobProgress(current=10, total=10),
        )

    @pytest.fixture
    def failed_job(self) -> Job:
        """Create a failed job."""
        job = Job(
            id="ingest-jkl012",
            corpus_id="test-corpus",
            status=JobStatus.FAILED,
            progress=JobProgress(current=3, total=10),
            error="Connection timeout",
        )
        return job

    @pytest.fixture
    def cancelled_job(self) -> Job:
        """Create a cancelled job."""
        return Job(
            id="ingest-mno345",
            corpus_id="test-corpus",
            status=JobStatus.CANCELLED,
            progress=JobProgress(current=2, total=10),
        )

    @pytest.mark.description("get_ingestion_status_tool returns not_found for unknown job")
    def test_job_not_found(self, mock_job_service: MagicMock) -> None:
        mock_job_service.get.return_value = None
        tool = GetIngestionStatusTool(job_service=mock_job_service)
        result = tool(job_id="ingest-unknown")

        assert result["job_id"] == "ingest-unknown"
        assert result["status"] == "not_found"
        assert result["progress_percentage"] == 0.0
        assert result["documents_processed"] == 0
        assert result["total_documents"] == 0
        assert len(result["errors"]) == 1
        assert "not found" in result["errors"][0]

    @pytest.mark.description("get_ingestion_status_tool returns pending status")
    def test_pending_status(
        self, mock_job_service: MagicMock, pending_job: Job
    ) -> None:
        mock_job_service.get.return_value = pending_job
        tool = GetIngestionStatusTool(job_service=mock_job_service)
        result = tool(job_id="ingest-abc123")

        assert result["job_id"] == "ingest-abc123"
        assert result["status"] == "pending"
        assert result["progress_percentage"] == 0.0
        assert result["documents_processed"] == 0
        assert result["total_documents"] == 10
        assert result["errors"] == []
        assert "queued" in result["message"].lower()

    @pytest.mark.description("get_ingestion_status_tool returns running status with progress")
    def test_running_status(
        self, mock_job_service: MagicMock, running_job: Job
    ) -> None:
        mock_job_service.get.return_value = running_job
        tool = GetIngestionStatusTool(job_service=mock_job_service)
        result = tool(job_id="ingest-def456")

        assert result["job_id"] == "ingest-def456"
        assert result["status"] == "running"
        assert result["progress_percentage"] == 50.0
        assert result["documents_processed"] == 5
        assert result["total_documents"] == 10
        assert result["errors"] == []
        assert "in progress" in result["message"].lower()
        assert "embedding" in result["message"].lower()

    @pytest.mark.description("get_ingestion_status_tool returns completed status")
    def test_completed_status(
        self, mock_job_service: MagicMock, completed_job: Job
    ) -> None:
        mock_job_service.get.return_value = completed_job
        tool = GetIngestionStatusTool(job_service=mock_job_service)
        result = tool(job_id="ingest-ghi789")

        assert result["job_id"] == "ingest-ghi789"
        assert result["status"] == "completed"
        assert result["progress_percentage"] == 100.0
        assert result["documents_processed"] == 10
        assert result["total_documents"] == 10
        assert result["errors"] == []
        assert "completed" in result["message"].lower()

    @pytest.mark.description("get_ingestion_status_tool returns failed status with error")
    def test_failed_status(
        self, mock_job_service: MagicMock, failed_job: Job
    ) -> None:
        mock_job_service.get.return_value = failed_job
        tool = GetIngestionStatusTool(job_service=mock_job_service)
        result = tool(job_id="ingest-jkl012")

        assert result["job_id"] == "ingest-jkl012"
        assert result["status"] == "failed"
        assert result["progress_percentage"] == 30.0
        assert result["documents_processed"] == 3
        assert result["total_documents"] == 10
        assert len(result["errors"]) == 1
        assert "Connection timeout" in result["errors"][0]
        assert "failed" in result["message"].lower()

    @pytest.mark.description("get_ingestion_status_tool returns cancelled status")
    def test_cancelled_status(
        self, mock_job_service: MagicMock, cancelled_job: Job
    ) -> None:
        mock_job_service.get.return_value = cancelled_job
        tool = GetIngestionStatusTool(job_service=mock_job_service)
        result = tool(job_id="ingest-mno345")

        assert result["job_id"] == "ingest-mno345"
        assert result["status"] == "cancelled"
        assert result["documents_processed"] == 2
        assert result["total_documents"] == 10
        assert result["errors"] == []
        assert "cancelled" in result["message"].lower()

    @pytest.mark.description("get_ingestion_status_tool strips whitespace from job_id")
    def test_job_id_stripped(self, mock_job_service: MagicMock, pending_job: Job) -> None:
        mock_job_service.get.return_value = pending_job
        tool = GetIngestionStatusTool(job_service=mock_job_service)
        result = tool(job_id="  ingest-abc123  ")

        mock_job_service.get.assert_called_once_with("ingest-abc123")
        assert result["job_id"] == "ingest-abc123"


class TestGetIngestionStatusToolServiceInit:
    """Tests for GetIngestionStatusTool service initialization."""

    @pytest.mark.description("get_ingestion_status_tool initializes with custom job service")
    def test_custom_job_service(self) -> None:
        mock_service = MagicMock(spec=JobService)
        tool = GetIngestionStatusTool(job_service=mock_service)
        assert tool._job_service == mock_service

    @pytest.mark.description("get_ingestion_status_tool lazily initializes job service")
    def test_lazy_service_init(self) -> None:
        tool = GetIngestionStatusTool()
        assert tool._job_service is None

    @pytest.mark.description("get_ingestion_status_tool job_service property returns service")
    def test_job_service_property(self) -> None:
        tool = GetIngestionStatusTool()
        # Access property triggers lazy init
        service = tool.job_service
        assert service is not None
        assert tool._job_service is not None


class TestModuleLevelGetIngestionStatusTool:
    """Tests for the module-level get_ingestion_status_tool instance."""

    @pytest.mark.description("get_ingestion_status_tool is a GetIngestionStatusTool instance")
    def test_is_get_ingestion_status_tool_instance(self) -> None:
        assert isinstance(get_ingestion_status_tool, GetIngestionStatusTool)

    @pytest.mark.description("get_ingestion_status_tool has expected name")
    def test_has_expected_name(self) -> None:
        assert get_ingestion_status_tool.name == "get_ingestion_status"

    @pytest.mark.description("get_ingestion_status_tool input_schema is accessible")
    def test_input_schema_accessible(self) -> None:
        schema = get_ingestion_status_tool.input_schema
        assert schema is not None
        assert "properties" in schema
        assert "job_id" in schema["properties"]
