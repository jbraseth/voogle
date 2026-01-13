# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for MCP ingest tool."""

from unittest.mock import MagicMock, patch

import pytest

from voogle.mcp.tools.ingest import (
    ChunkingStrategy,
    IngestSource,
    IngestTool,
    IngestToolInput,
    IngestToolOutput,
    SourceType,
    ingest_tool,
)
from voogle.pipeline.jobs import Job, JobService, JobStatus

pytestmark = pytest.mark.unit


class TestSourceType:
    """Tests for SourceType enum."""

    @pytest.mark.description("SourceType has URL, FILE, and BATCH values")
    def test_source_types(self) -> None:
        assert SourceType.URL.value == "url"
        assert SourceType.FILE.value == "file"
        assert SourceType.BATCH.value == "batch"

    @pytest.mark.description("SourceType can be created from string")
    def test_from_string(self) -> None:
        assert SourceType("url") == SourceType.URL
        assert SourceType("file") == SourceType.FILE
        assert SourceType("batch") == SourceType.BATCH


class TestChunkingStrategy:
    """Tests for ChunkingStrategy enum."""

    @pytest.mark.description("ChunkingStrategy has all expected values")
    def test_chunking_strategies(self) -> None:
        assert ChunkingStrategy.FIXED_SIZE.value == "fixed_size"
        assert ChunkingStrategy.SENTENCE.value == "sentence"
        assert ChunkingStrategy.PARAGRAPH.value == "paragraph"
        assert ChunkingStrategy.SEMANTIC.value == "semantic"

    @pytest.mark.description("ChunkingStrategy can be created from string")
    def test_from_string(self) -> None:
        assert ChunkingStrategy("fixed_size") == ChunkingStrategy.FIXED_SIZE
        assert ChunkingStrategy("sentence") == ChunkingStrategy.SENTENCE
        assert ChunkingStrategy("paragraph") == ChunkingStrategy.PARAGRAPH
        assert ChunkingStrategy("semantic") == ChunkingStrategy.SEMANTIC


class TestIngestSource:
    """Tests for IngestSource dataclass."""

    @pytest.mark.description("IngestSource with URL type")
    def test_url_source(self) -> None:
        source = IngestSource(
            type=SourceType.URL,
            value="https://example.com/audio.mp3",
        )
        assert source.type == SourceType.URL
        assert source.value == "https://example.com/audio.mp3"
        assert source.content_type is None

    @pytest.mark.description("IngestSource with FILE type and content_type")
    def test_file_source_with_content_type(self) -> None:
        source = IngestSource(
            type=SourceType.FILE,
            value="/path/to/file.pdf",
            content_type="document",
        )
        assert source.type == SourceType.FILE
        assert source.value == "/path/to/file.pdf"
        assert source.content_type == "document"

    @pytest.mark.description("IngestSource with BATCH type")
    def test_batch_source(self) -> None:
        urls = ["https://example.com/a.mp3", "https://example.com/b.mp3"]
        source = IngestSource(
            type=SourceType.BATCH,
            value=urls,
        )
        assert source.type == SourceType.BATCH
        assert source.value == urls
        assert len(source.value) == 2


class TestIngestToolInput:
    """Tests for IngestToolInput dataclass."""

    @pytest.mark.description("IngestToolInput with required fields only")
    def test_required_fields(self) -> None:
        source = IngestSource(type=SourceType.URL, value="https://example.com/a.mp3")
        input_data = IngestToolInput(
            corpus_id="test-corpus",
            source=source,
        )
        assert input_data.corpus_id == "test-corpus"
        assert input_data.source == source
        assert input_data.metadata == {}
        assert input_data.chunking_strategy == ChunkingStrategy.FIXED_SIZE

    @pytest.mark.description("IngestToolInput with all fields")
    def test_all_fields(self) -> None:
        source = IngestSource(type=SourceType.FILE, value="/path/to/file")
        input_data = IngestToolInput(
            corpus_id="my-corpus",
            source=source,
            metadata={"author": "Test", "tags": ["audio", "podcast"]},
            chunking_strategy=ChunkingStrategy.SEMANTIC,
        )
        assert input_data.corpus_id == "my-corpus"
        assert input_data.metadata == {"author": "Test", "tags": ["audio", "podcast"]}
        assert input_data.chunking_strategy == ChunkingStrategy.SEMANTIC


class TestIngestToolOutput:
    """Tests for IngestToolOutput dataclass."""

    @pytest.mark.description("IngestToolOutput structure")
    def test_output_structure(self) -> None:
        output = IngestToolOutput(
            job_id="ingest-abc123",
            status="pending",
            message="Ingestion job created",
        )
        assert output.job_id == "ingest-abc123"
        assert output.status == "pending"
        assert output.message == "Ingestion job created"


class TestIngestToolBasic:
    """Basic tests for IngestTool."""

    @pytest.mark.description("ingest_tool has correct name and description")
    def test_tool_metadata(self) -> None:
        tool = IngestTool()
        assert tool.name == "ingest"
        assert "ingest" in tool.description.lower()
        assert "job" in tool.description.lower()

    @pytest.mark.description("ingest_tool has valid input schema")
    def test_input_schema(self) -> None:
        tool = IngestTool()
        schema = tool.input_schema
        assert schema["type"] == "object"
        assert "corpus_id" in schema["properties"]
        assert "source" in schema["properties"]
        assert "metadata" in schema["properties"]
        assert "chunking_strategy" in schema["properties"]
        assert "corpus_id" in schema["required"]
        assert "source" in schema["required"]

    @pytest.mark.description("ingest_tool input_schema has correct types")
    def test_input_schema_types(self) -> None:
        schema = ingest_tool.input_schema
        assert schema["properties"]["corpus_id"]["type"] == "string"
        assert schema["properties"]["source"]["type"] == "object"
        assert schema["properties"]["metadata"]["type"] == "object"
        assert schema["properties"]["chunking_strategy"]["type"] == "string"

    @pytest.mark.description("ingest_tool input_schema source has required fields")
    def test_input_schema_source(self) -> None:
        schema = ingest_tool.input_schema
        source_props = schema["properties"]["source"]
        assert "type" in source_props["properties"]
        assert "value" in source_props["properties"]
        assert source_props["required"] == ["type", "value"]

    @pytest.mark.description("ingest_tool input_schema has chunking strategy enum")
    def test_input_schema_chunking_enum(self) -> None:
        schema = ingest_tool.input_schema
        chunking_prop = schema["properties"]["chunking_strategy"]
        assert chunking_prop["enum"] == ["fixed_size", "sentence", "paragraph", "semantic"]

    @pytest.mark.description("module-level ingest_tool is IngestTool instance")
    def test_module_level_instance(self) -> None:
        assert isinstance(ingest_tool, IngestTool)


class TestIngestToolValidation:
    """Tests for IngestTool input validation."""

    @pytest.fixture
    def mock_job_service(self) -> MagicMock:
        """Create a mock JobService."""
        mock_service = MagicMock(spec=JobService)
        mock_job = MagicMock(spec=Job)
        mock_job.status = JobStatus.PENDING
        mock_service.create.return_value = mock_job
        return mock_service

    @pytest.mark.description("ingest_tool raises ValueError for empty corpus_id")
    def test_empty_corpus_id(self, mock_job_service: MagicMock) -> None:
        tool = IngestTool(job_service=mock_job_service)
        with pytest.raises(ValueError, match="corpus_id cannot be empty"):
            tool(
                corpus_id="",
                source={"type": "url", "value": "https://example.com/a.mp3"},
            )

    @pytest.mark.description("ingest_tool raises ValueError for whitespace corpus_id")
    def test_whitespace_corpus_id(self, mock_job_service: MagicMock) -> None:
        tool = IngestTool(job_service=mock_job_service)
        with pytest.raises(ValueError, match="corpus_id cannot be empty"):
            tool(
                corpus_id="   ",
                source={"type": "url", "value": "https://example.com/a.mp3"},
            )

    @pytest.mark.description("ingest_tool raises ValueError for empty source")
    def test_empty_source(self, mock_job_service: MagicMock) -> None:
        tool = IngestTool(job_service=mock_job_service)
        with pytest.raises(ValueError, match="source cannot be empty"):
            tool(corpus_id="test-corpus", source={})

    @pytest.mark.description("ingest_tool raises ValueError for missing source type")
    def test_missing_source_type(self, mock_job_service: MagicMock) -> None:
        tool = IngestTool(job_service=mock_job_service)
        with pytest.raises(ValueError, match="source.type is required"):
            tool(
                corpus_id="test-corpus",
                source={"value": "https://example.com/a.mp3"},
            )

    @pytest.mark.description("ingest_tool raises ValueError for invalid source type")
    def test_invalid_source_type(self, mock_job_service: MagicMock) -> None:
        tool = IngestTool(job_service=mock_job_service)
        with pytest.raises(ValueError, match="Invalid source type"):
            tool(
                corpus_id="test-corpus",
                source={"type": "invalid", "value": "something"},
            )

    @pytest.mark.description("ingest_tool raises ValueError for missing source value")
    def test_missing_source_value(self, mock_job_service: MagicMock) -> None:
        tool = IngestTool(job_service=mock_job_service)
        with pytest.raises(ValueError, match="source.value is required"):
            tool(
                corpus_id="test-corpus",
                source={"type": "url"},
            )

    @pytest.mark.description("ingest_tool raises ValueError for batch with non-list value")
    def test_batch_non_list_value(self, mock_job_service: MagicMock) -> None:
        tool = IngestTool(job_service=mock_job_service)
        with pytest.raises(ValueError, match="must be a list for batch type"):
            tool(
                corpus_id="test-corpus",
                source={"type": "batch", "value": "single-url"},
            )

    @pytest.mark.description("ingest_tool raises ValueError for batch with empty list")
    def test_batch_empty_list(self, mock_job_service: MagicMock) -> None:
        tool = IngestTool(job_service=mock_job_service)
        with pytest.raises(ValueError, match="cannot be empty for batch type"):
            tool(
                corpus_id="test-corpus",
                source={"type": "batch", "value": []},
            )

    @pytest.mark.description("ingest_tool raises ValueError for url with non-string value")
    def test_url_non_string_value(self, mock_job_service: MagicMock) -> None:
        tool = IngestTool(job_service=mock_job_service)
        with pytest.raises(ValueError, match="must be a string for url type"):
            tool(
                corpus_id="test-corpus",
                source={"type": "url", "value": ["list", "of", "urls"]},
            )

    @pytest.mark.description("ingest_tool raises ValueError for invalid chunking strategy")
    def test_invalid_chunking_strategy(self, mock_job_service: MagicMock) -> None:
        tool = IngestTool(job_service=mock_job_service)
        with pytest.raises(ValueError, match="Invalid chunking strategy"):
            tool(
                corpus_id="test-corpus",
                source={"type": "url", "value": "https://example.com/a.mp3"},
                chunking_strategy="invalid_strategy",
            )


class TestIngestToolExecution:
    """Tests for IngestTool execution with mocked JobService."""

    @pytest.fixture
    def mock_job_service(self) -> MagicMock:
        """Create a mock JobService."""
        mock_service = MagicMock(spec=JobService)
        mock_job = MagicMock(spec=Job)
        mock_job.status = JobStatus.PENDING
        mock_service.create.return_value = mock_job
        return mock_service

    @pytest.mark.description("ingest_tool returns expected output structure")
    def test_output_structure(self, mock_job_service: MagicMock) -> None:
        tool = IngestTool(job_service=mock_job_service)
        result = tool(
            corpus_id="test-corpus",
            source={"type": "url", "value": "https://example.com/audio.mp3"},
        )

        assert "job_id" in result
        assert "status" in result
        assert "message" in result

    @pytest.mark.description("ingest_tool returns job_id starting with ingest-")
    def test_job_id_format(self, mock_job_service: MagicMock) -> None:
        tool = IngestTool(job_service=mock_job_service)
        result = tool(
            corpus_id="test-corpus",
            source={"type": "url", "value": "https://example.com/audio.mp3"},
        )

        assert result["job_id"].startswith("ingest-")
        assert len(result["job_id"]) == 19  # "ingest-" + 12 hex chars

    @pytest.mark.description("ingest_tool returns pending status")
    def test_pending_status(self, mock_job_service: MagicMock) -> None:
        tool = IngestTool(job_service=mock_job_service)
        result = tool(
            corpus_id="test-corpus",
            source={"type": "url", "value": "https://example.com/audio.mp3"},
        )

        assert result["status"] == "pending"

    @pytest.mark.description("ingest_tool creates job via JobService")
    def test_creates_job(self, mock_job_service: MagicMock) -> None:
        tool = IngestTool(job_service=mock_job_service)
        result = tool(
            corpus_id="test-corpus",
            source={"type": "url", "value": "https://example.com/audio.mp3"},
        )

        mock_job_service.create.assert_called_once()
        call_kwargs = mock_job_service.create.call_args.kwargs
        assert call_kwargs["corpus_id"] == "test-corpus"
        assert call_kwargs["source_type"] == "url"
        assert call_kwargs["source_value"] == "https://example.com/audio.mp3"

    @pytest.mark.description("ingest_tool passes chunking_strategy to job")
    def test_chunking_strategy_passed(self, mock_job_service: MagicMock) -> None:
        tool = IngestTool(job_service=mock_job_service)
        tool(
            corpus_id="test-corpus",
            source={"type": "url", "value": "https://example.com/audio.mp3"},
            chunking_strategy="semantic",
        )

        call_kwargs = mock_job_service.create.call_args.kwargs
        assert call_kwargs["chunking_strategy"] == "semantic"

    @pytest.mark.description("ingest_tool uses default chunking_strategy when not provided")
    def test_default_chunking_strategy(self, mock_job_service: MagicMock) -> None:
        tool = IngestTool(job_service=mock_job_service)
        tool(
            corpus_id="test-corpus",
            source={"type": "url", "value": "https://example.com/audio.mp3"},
        )

        call_kwargs = mock_job_service.create.call_args.kwargs
        assert call_kwargs["chunking_strategy"] == "fixed_size"

    @pytest.mark.description("ingest_tool passes metadata to job")
    def test_metadata_passed(self, mock_job_service: MagicMock) -> None:
        tool = IngestTool(job_service=mock_job_service)
        metadata = {"author": "Test Author", "tags": ["podcast", "tech"]}
        tool(
            corpus_id="test-corpus",
            source={"type": "url", "value": "https://example.com/audio.mp3"},
            metadata=metadata,
        )

        call_kwargs = mock_job_service.create.call_args.kwargs
        assert call_kwargs["user_metadata"] == metadata

    @pytest.mark.description("ingest_tool passes content_type from source")
    def test_content_type_passed(self, mock_job_service: MagicMock) -> None:
        tool = IngestTool(job_service=mock_job_service)
        tool(
            corpus_id="test-corpus",
            source={
                "type": "file",
                "value": "/path/to/file.mp3",
                "content_type": "audio",
            },
        )

        call_kwargs = mock_job_service.create.call_args.kwargs
        assert call_kwargs["source_content_type"] == "audio"

    @pytest.mark.description("ingest_tool strips whitespace from corpus_id")
    def test_corpus_id_stripped(self, mock_job_service: MagicMock) -> None:
        tool = IngestTool(job_service=mock_job_service)
        tool(
            corpus_id="  test-corpus  ",
            source={"type": "url", "value": "https://example.com/audio.mp3"},
        )

        call_kwargs = mock_job_service.create.call_args.kwargs
        assert call_kwargs["corpus_id"] == "test-corpus"

    @pytest.mark.description("ingest_tool message includes corpus_id")
    def test_message_includes_corpus(self, mock_job_service: MagicMock) -> None:
        tool = IngestTool(job_service=mock_job_service)
        result = tool(
            corpus_id="my-podcast-corpus",
            source={"type": "url", "value": "https://example.com/audio.mp3"},
        )

        assert "my-podcast-corpus" in result["message"]

    @pytest.mark.description("ingest_tool message includes chunking strategy")
    def test_message_includes_chunking(self, mock_job_service: MagicMock) -> None:
        tool = IngestTool(job_service=mock_job_service)
        result = tool(
            corpus_id="test-corpus",
            source={"type": "url", "value": "https://example.com/audio.mp3"},
            chunking_strategy="sentence",
        )

        assert "sentence" in result["message"]


class TestIngestToolBatch:
    """Tests for IngestTool batch ingestion."""

    @pytest.fixture
    def mock_job_service(self) -> MagicMock:
        """Create a mock JobService."""
        mock_service = MagicMock(spec=JobService)
        mock_job = MagicMock(spec=Job)
        mock_job.status = JobStatus.PENDING
        mock_service.create.return_value = mock_job
        return mock_service

    @pytest.mark.description("ingest_tool accepts batch source type")
    def test_batch_source(self, mock_job_service: MagicMock) -> None:
        tool = IngestTool(job_service=mock_job_service)
        urls = [
            "https://example.com/a.mp3",
            "https://example.com/b.mp3",
            "https://example.com/c.mp3",
        ]
        result = tool(
            corpus_id="test-corpus",
            source={"type": "batch", "value": urls},
        )

        assert result["status"] == "pending"
        call_kwargs = mock_job_service.create.call_args.kwargs
        assert call_kwargs["source_type"] == "batch"
        assert call_kwargs["source_value"] == urls

    @pytest.mark.description("ingest_tool message reflects batch count")
    def test_batch_message_count(self, mock_job_service: MagicMock) -> None:
        tool = IngestTool(job_service=mock_job_service)
        urls = ["https://example.com/a.mp3", "https://example.com/b.mp3"]
        result = tool(
            corpus_id="test-corpus",
            source={"type": "batch", "value": urls},
        )

        assert "2 sources" in result["message"]


class TestIngestToolFileSource:
    """Tests for IngestTool file source type."""

    @pytest.fixture
    def mock_job_service(self) -> MagicMock:
        """Create a mock JobService."""
        mock_service = MagicMock(spec=JobService)
        mock_job = MagicMock(spec=Job)
        mock_job.status = JobStatus.PENDING
        mock_service.create.return_value = mock_job
        return mock_service

    @pytest.mark.description("ingest_tool accepts file source type")
    def test_file_source(self, mock_job_service: MagicMock) -> None:
        tool = IngestTool(job_service=mock_job_service)
        result = tool(
            corpus_id="test-corpus",
            source={"type": "file", "value": "/path/to/document.pdf"},
        )

        assert result["status"] == "pending"
        call_kwargs = mock_job_service.create.call_args.kwargs
        assert call_kwargs["source_type"] == "file"
        assert call_kwargs["source_value"] == "/path/to/document.pdf"

    @pytest.mark.description("ingest_tool message reflects file source")
    def test_file_message(self, mock_job_service: MagicMock) -> None:
        tool = IngestTool(job_service=mock_job_service)
        result = tool(
            corpus_id="test-corpus",
            source={"type": "file", "value": "/path/to/document.pdf"},
        )

        assert "1 file" in result["message"]


class TestIngestToolServiceInit:
    """Tests for IngestTool service initialization."""

    @pytest.mark.description("ingest_tool initializes with custom job service")
    def test_custom_job_service(self) -> None:
        mock_service = MagicMock(spec=JobService)
        tool = IngestTool(job_service=mock_service)
        assert tool._job_service == mock_service

    @pytest.mark.description("ingest_tool lazily initializes job service")
    def test_lazy_service_init(self) -> None:
        tool = IngestTool()
        assert tool._job_service is None

    @pytest.mark.description("ingest_tool job_service property returns service")
    def test_job_service_property(self) -> None:
        tool = IngestTool()
        # Access property triggers lazy init
        service = tool.job_service
        assert service is not None
        assert tool._job_service is not None


class TestModuleLevelIngestTool:
    """Tests for the module-level ingest_tool instance."""

    @pytest.mark.description("ingest_tool is an IngestTool instance")
    def test_is_ingest_tool_instance(self) -> None:
        assert isinstance(ingest_tool, IngestTool)

    @pytest.mark.description("ingest_tool has expected name")
    def test_has_expected_name(self) -> None:
        assert ingest_tool.name == "ingest"

    @pytest.mark.description("ingest_tool input_schema is accessible")
    def test_input_schema_accessible(self) -> None:
        schema = ingest_tool.input_schema
        assert schema is not None
        assert "properties" in schema
        assert "corpus_id" in schema["properties"]
        assert "source" in schema["properties"]
