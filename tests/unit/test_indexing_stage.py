# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for IndexingStage."""

from collections.abc import AsyncIterator
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from voogle.pipeline.indexing import (
    EmbeddedFragment,
    IndexingConfig,
    IndexingResult,
    IndexingStage,
    generate_point_id,
)
from voogle.vector_schema import VectorName


class TestIndexingConfig:
    """Tests for IndexingConfig dataclass."""

    def test_create_default_config(self) -> None:
        """Default indexing config can be created."""
        config = IndexingConfig()
        assert config.collection_name == "vectordb"
        assert config.batch_size == 100
        assert config.enable_deduplication is True
        assert config.optimize_threshold == 10000
        assert config.vector_name == VectorName.TEXT_DENSE.value
        assert config.wait_for_upsert is True

    def test_create_custom_config(self) -> None:
        """Custom indexing config can be created."""
        config = IndexingConfig(
            collection_name="my_collection",
            batch_size=50,
            enable_deduplication=False,
            optimize_threshold=5000,
            vector_name=VectorName.IMAGE.value,
            wait_for_upsert=False,
        )
        assert config.collection_name == "my_collection"
        assert config.batch_size == 50
        assert config.enable_deduplication is False
        assert config.optimize_threshold == 5000
        assert config.vector_name == VectorName.IMAGE.value
        assert config.wait_for_upsert is False

    def test_empty_collection_name_raises(self) -> None:
        """Empty collection_name raises ValueError."""
        with pytest.raises(ValueError, match="collection_name cannot be empty"):
            IndexingConfig(collection_name="")

    def test_zero_batch_size_raises(self) -> None:
        """Zero batch_size raises ValueError."""
        with pytest.raises(ValueError, match="batch_size must be >= 1"):
            IndexingConfig(batch_size=0)

    def test_negative_batch_size_raises(self) -> None:
        """Negative batch_size raises ValueError."""
        with pytest.raises(ValueError, match="batch_size must be >= 1"):
            IndexingConfig(batch_size=-1)

    def test_zero_optimize_threshold_raises(self) -> None:
        """Zero optimize_threshold raises ValueError."""
        with pytest.raises(ValueError, match="optimize_threshold must be >= 1"):
            IndexingConfig(optimize_threshold=0)

    def test_config_is_frozen(self) -> None:
        """IndexingConfig is immutable."""
        config = IndexingConfig()
        with pytest.raises(AttributeError):
            config.batch_size = 200  # type: ignore[misc]


class TestEmbeddedFragment:
    """Tests for EmbeddedFragment dataclass."""

    def test_create_fragment_with_numpy_embedding(self) -> None:
        """Fragment can be created with numpy array embedding."""
        embedding = np.array([0.1, 0.2, 0.3])
        fragment = EmbeddedFragment(
            id="frag1",
            text="Hello world",
            embedding=embedding,
            source_id="source1",
        )
        assert fragment.id == "frag1"
        assert fragment.text == "Hello world"
        assert np.array_equal(fragment.embedding, embedding)
        assert fragment.source_id == "source1"
        assert fragment.source_type == "text"
        assert fragment.vector_name == VectorName.TEXT_DENSE.value

    def test_create_fragment_with_list_embedding(self) -> None:
        """Fragment can be created with list embedding."""
        embedding = [0.1, 0.2, 0.3]
        fragment = EmbeddedFragment(
            id="frag2",
            text="Test text",
            embedding=embedding,
            source_id="source2",
        )
        assert fragment.embedding == embedding

    def test_fragment_with_full_metadata(self) -> None:
        """Fragment can be created with all optional fields."""
        fragment = EmbeddedFragment(
            id="frag3",
            text="Full fragment",
            embedding=[0.1, 0.2],
            source_id="source3",
            source_type="audio",
            vector_name=VectorName.MULTIMODAL.value,
            location={"type": "timestamp", "start_time": 10.5, "end_time": 20.0},
            deep_link="https://example.com/audio?t=10",
            metadata={"episode": 123, "channel": 456},
        )
        assert fragment.source_type == "audio"
        assert fragment.vector_name == VectorName.MULTIMODAL.value
        assert fragment.location == {"type": "timestamp", "start_time": 10.5, "end_time": 20.0}
        assert fragment.deep_link == "https://example.com/audio?t=10"
        assert fragment.metadata == {"episode": 123, "channel": 456}

    def test_content_hash_is_deterministic(self) -> None:
        """Content hash is deterministic for same content."""
        fragment1 = EmbeddedFragment(
            id="frag1",
            text="Same text",
            embedding=[0.1, 0.2],
            source_id="source1",
            location={"type": "test"},
        )
        fragment2 = EmbeddedFragment(
            id="frag2",  # Different ID
            text="Same text",
            embedding=[0.3, 0.4],  # Different embedding
            source_id="source1",
            location={"type": "test"},
        )
        assert fragment1.content_hash == fragment2.content_hash

    def test_content_hash_differs_for_different_text(self) -> None:
        """Content hash differs for different text content."""
        fragment1 = EmbeddedFragment(
            id="frag1",
            text="Text A",
            embedding=[0.1],
            source_id="source1",
        )
        fragment2 = EmbeddedFragment(
            id="frag1",
            text="Text B",
            embedding=[0.1],
            source_id="source1",
        )
        assert fragment1.content_hash != fragment2.content_hash

    def test_content_hash_differs_for_different_source(self) -> None:
        """Content hash differs for different source_id."""
        fragment1 = EmbeddedFragment(
            id="frag1",
            text="Same text",
            embedding=[0.1],
            source_id="source1",
        )
        fragment2 = EmbeddedFragment(
            id="frag1",
            text="Same text",
            embedding=[0.1],
            source_id="source2",
        )
        assert fragment1.content_hash != fragment2.content_hash


class TestGeneratePointId:
    """Tests for generate_point_id function."""

    def test_generates_valid_uuid(self) -> None:
        """Generated point ID is a valid UUID string."""
        content_hash = "a" * 64  # Valid SHA256 hash
        point_id = generate_point_id(content_hash)
        # Should be a valid UUID format
        parts = point_id.split("-")
        assert len(parts) == 5
        assert len(parts[0]) == 8
        assert len(parts[1]) == 4
        assert len(parts[2]) == 4
        assert len(parts[3]) == 4
        assert len(parts[4]) == 12

    def test_same_hash_produces_same_id(self) -> None:
        """Same content hash produces same point ID."""
        content_hash = "abc123" + "0" * 58
        id1 = generate_point_id(content_hash)
        id2 = generate_point_id(content_hash)
        assert id1 == id2

    def test_different_hash_produces_different_id(self) -> None:
        """Different content hashes produce different point IDs."""
        hash1 = "a" * 64
        hash2 = "b" * 64
        id1 = generate_point_id(hash1)
        id2 = generate_point_id(hash2)
        assert id1 != id2


class TestIndexingStage:
    """Tests for IndexingStage class."""

    def test_create_stage_default(self) -> None:
        """Stage can be created with defaults."""
        stage = IndexingStage()
        assert stage.name == "indexing"
        assert stage.client is None
        assert isinstance(stage.config, IndexingConfig)
        assert stage.points_indexed == 0

    def test_create_stage_with_config(self) -> None:
        """Stage can be created with custom config."""
        config = IndexingConfig(batch_size=50)
        stage = IndexingStage(config=config)
        assert stage.config.batch_size == 50

    def test_create_stage_with_client(self) -> None:
        """Stage can be created with Qdrant client."""
        mock_client = MagicMock()
        stage = IndexingStage(client=mock_client)
        assert stage.client is mock_client

    def test_client_can_be_set(self) -> None:
        """Qdrant client can be set after creation."""
        stage = IndexingStage()
        mock_client = MagicMock()
        stage.client = mock_client
        assert stage.client is mock_client

    def test_str_representation(self) -> None:
        """Stage has readable string representation."""
        stage = IndexingStage(config=IndexingConfig(collection_name="test", batch_size=50))
        result = str(stage)
        assert "IndexingStage" in result
        assert "test" in result
        assert "50" in result

    def test_repr_representation(self) -> None:
        """Stage has detailed repr representation."""
        stage = IndexingStage()
        result = repr(stage)
        assert "IndexingStage" in result
        assert "points_indexed=0" in result

    @pytest.mark.asyncio
    async def test_setup_without_client_logs_warning(self) -> None:
        """Setup without client logs warning and doesn't fail."""
        stage = IndexingStage()
        await stage.setup()  # Should not raise

    @pytest.mark.asyncio
    async def test_setup_creates_collection_if_needed(self) -> None:
        """Setup creates collection if it doesn't exist."""
        mock_client = MagicMock()
        mock_client.collection_exists.return_value = False

        stage = IndexingStage(client=mock_client)
        await stage.setup()

        mock_client.collection_exists.assert_called_once_with("vectordb")
        mock_client.create_collection.assert_called_once()

    @pytest.mark.asyncio
    async def test_setup_skips_creation_if_exists(self) -> None:
        """Setup skips collection creation if it exists."""
        mock_client = MagicMock()
        mock_client.collection_exists.return_value = True

        stage = IndexingStage(client=mock_client)
        await stage.setup()

        mock_client.collection_exists.assert_called_once()
        mock_client.create_collection.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_without_client_raises(self) -> None:
        """Processing without client raises StageError."""
        from voogle.pipeline import StageError

        stage = IndexingStage()

        async def empty_items() -> AsyncIterator[EmbeddedFragment]:
            yield EmbeddedFragment(
                id="test",
                text="test",
                embedding=[0.1],
                source_id="src",
            )

        with pytest.raises(StageError, match="No Qdrant client configured"):
            async for _ in stage.process(empty_items()):
                pass

    @pytest.mark.asyncio
    async def test_process_batches_fragments(self) -> None:
        """Process batches fragments according to batch_size."""
        mock_client = MagicMock()
        config = IndexingConfig(batch_size=2)
        stage = IndexingStage(client=mock_client, config=config)

        async def items() -> AsyncIterator[EmbeddedFragment]:
            for i in range(5):
                yield EmbeddedFragment(
                    id=f"frag{i}",
                    text=f"Text {i}",
                    embedding=np.array([0.1 * i, 0.2 * i]),
                    source_id="source1",
                )

        results = []
        async for result in stage.process(items()):
            results.append(result)

        # 5 fragments with batch_size=2 should produce 2 batches (2+2)
        # Remaining 1 is flushed in teardown
        assert len(results) == 2
        assert results[0].batch_size == 2
        assert results[1].batch_size == 2

    @pytest.mark.asyncio
    async def test_process_deduplicates_by_content_hash(self) -> None:
        """Process skips duplicate fragments by content hash."""
        mock_client = MagicMock()
        config = IndexingConfig(batch_size=10, enable_deduplication=True)
        stage = IndexingStage(client=mock_client, config=config)

        async def items() -> AsyncIterator[EmbeddedFragment]:
            # First two have same text+source, so same content hash
            yield EmbeddedFragment(
                id="frag1",
                text="Same text",
                embedding=[0.1],
                source_id="source1",
            )
            yield EmbeddedFragment(
                id="frag2",
                text="Same text",  # Duplicate!
                embedding=[0.2],
                source_id="source1",
            )
            yield EmbeddedFragment(
                id="frag3",
                text="Different text",
                embedding=[0.3],
                source_id="source1",
            )

        results = []
        async for result in stage.process(items()):
            results.append(result)

        # No results yet (batch_size=10, only 2 unique items)
        assert len(results) == 0

        # Teardown flushes remaining
        await stage.teardown()
        # After deduplication, should have indexed 2 unique fragments
        assert stage.points_indexed == 2

    @pytest.mark.asyncio
    async def test_process_without_deduplication(self) -> None:
        """Process doesn't deduplicate when disabled."""
        mock_client = MagicMock()
        config = IndexingConfig(batch_size=10, enable_deduplication=False)
        stage = IndexingStage(client=mock_client, config=config)

        async def items() -> AsyncIterator[EmbeddedFragment]:
            yield EmbeddedFragment(
                id="frag1",
                text="Same text",
                embedding=[0.1],
                source_id="source1",
            )
            yield EmbeddedFragment(
                id="frag2",
                text="Same text",  # Would be duplicate, but dedup is off
                embedding=[0.2],
                source_id="source1",
            )

        async for _ in stage.process(items()):
            pass

        await stage.teardown()
        # Without deduplication, both fragments should be indexed
        assert stage.points_indexed == 2

    @pytest.mark.asyncio
    async def test_teardown_flushes_remaining_batch(self) -> None:
        """Teardown flushes any remaining items in batch."""
        mock_client = MagicMock()
        config = IndexingConfig(batch_size=10)  # Large batch
        stage = IndexingStage(client=mock_client, config=config)

        async def items() -> AsyncIterator[EmbeddedFragment]:
            for i in range(3):
                yield EmbeddedFragment(
                    id=f"frag{i}",
                    text=f"Text {i}",
                    embedding=[0.1],
                    source_id="source1",
                )

        async for _ in stage.process(items()):
            pass

        # Not yet indexed (batch not full)
        assert stage.points_indexed == 0

        # Teardown should flush
        await stage.teardown()
        assert stage.points_indexed == 3

    @pytest.mark.asyncio
    async def test_teardown_triggers_optimization(self) -> None:
        """Teardown triggers optimization when threshold reached."""
        mock_client = MagicMock()
        config = IndexingConfig(batch_size=5, optimize_threshold=3)
        stage = IndexingStage(client=mock_client, config=config)

        async def items() -> AsyncIterator[EmbeddedFragment]:
            for i in range(5):
                yield EmbeddedFragment(
                    id=f"frag{i}",
                    text=f"Text {i}",
                    embedding=[0.1],
                    source_id="source1",
                )

        async for _ in stage.process(items()):
            pass

        await stage.teardown()

        # Should have triggered optimization
        mock_client.update_collection.assert_called_once()

    @pytest.mark.asyncio
    async def test_build_payload_includes_required_fields(self) -> None:
        """Payload includes all required fields."""
        stage = IndexingStage()
        fragment = EmbeddedFragment(
            id="frag1",
            text="Hello world",
            embedding=[0.1],
            source_id="source1",
            source_type="audio",
        )

        payload = stage._build_payload(fragment)

        assert payload["fragment_id"] == "frag1"
        assert payload["text"] == "Hello world"
        assert payload["source_id"] == "source1"
        assert payload["source_type"] == "audio"
        assert "content_hash" in payload
        assert "indexed_at" in payload

    @pytest.mark.asyncio
    async def test_build_payload_includes_location(self) -> None:
        """Payload includes flattened location fields."""
        stage = IndexingStage()
        fragment = EmbeddedFragment(
            id="frag1",
            text="Test",
            embedding=[0.1],
            source_id="source1",
            location={"type": "timestamp", "start_time": 10.5, "end_time": 20.0},
        )

        payload = stage._build_payload(fragment)

        assert payload["location_type"] == "timestamp"
        assert payload["start_time"] == 10.5
        assert payload["end_time"] == 20.0

    @pytest.mark.asyncio
    async def test_build_payload_includes_metadata(self) -> None:
        """Payload includes additional metadata."""
        stage = IndexingStage()
        fragment = EmbeddedFragment(
            id="frag1",
            text="Test",
            embedding=[0.1],
            source_id="source1",
            metadata={"episode": 123, "channel": 456},
        )

        payload = stage._build_payload(fragment)

        assert payload["episode"] == 123
        assert payload["channel"] == 456


class TestIndexingResult:
    """Tests for IndexingResult dataclass."""

    def test_create_result(self) -> None:
        """IndexingResult can be created with all fields."""
        result = IndexingResult(
            point_ids=["id1", "id2"],
            deduplicated_count=1,
            batch_size=3,
            collection_name="test_collection",
        )
        assert result.point_ids == ["id1", "id2"]
        assert result.deduplicated_count == 1
        assert result.batch_size == 3
        assert result.collection_name == "test_collection"

    def test_empty_result(self) -> None:
        """Empty IndexingResult can be created."""
        result = IndexingResult(
            point_ids=[],
            deduplicated_count=0,
            batch_size=0,
            collection_name="empty",
        )
        assert len(result.point_ids) == 0
        assert result.batch_size == 0
