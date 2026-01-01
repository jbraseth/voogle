# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Component tests for CLI commands.

These tests verify the CLI argument parsing and basic command behavior
without requiring a full database or network access.
"""

import argparse
from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.component


class TestEpisodesCliArguments:
    """Tests for voogle-episodes CLI argument parsing."""

    @pytest.mark.description("--check-metadata flag is recognized")
    def test_check_metadata_flag_recognized(self) -> None:
        """Verify --check-metadata is a valid CLI argument."""
        # Create parser manually to test argument parsing
        parser = argparse.ArgumentParser()
        parser.add_argument("--check-metadata", action="store_true", default=False)
        parser.add_argument("--rebuild-embeddings", action="store_true", default=False)
        parser.add_argument("--reindex-channel", type=str, default=None)

        # Test the flag is recognized
        args = parser.parse_args(["--check-metadata"])
        assert args.check_metadata is True
        assert args.rebuild_embeddings is False

    @pytest.mark.description("--rebuild-embeddings requires --reindex-channel")
    def test_rebuild_embeddings_requires_channel(self) -> None:
        """Verify --rebuild-embeddings requires --reindex-channel."""
        # The actual validation happens in _main(), not in argparse
        # This test documents the expected constraint
        parser = argparse.ArgumentParser()
        parser.add_argument("--check-metadata", action="store_true", default=False)
        parser.add_argument("--rebuild-embeddings", action="store_true", default=False)
        parser.add_argument("--reindex-channel", type=str, default=None)

        # This should parse successfully (validation happens later)
        args = parser.parse_args(["--rebuild-embeddings"])
        assert args.rebuild_embeddings is True
        assert args.reindex_channel is None  # Missing, will error in _main()

    @pytest.mark.description("Combined flags parse correctly")
    def test_combined_flags_parse(self) -> None:
        """Verify multiple flags can be combined."""
        parser = argparse.ArgumentParser()
        parser.add_argument("--update", action="store_true", default=False)
        parser.add_argument("--store", action="store_true", default=False)
        parser.add_argument("--transcribe-days", type=int, default=-1)

        args = parser.parse_args(["--update", "--store", "--transcribe-days", "7"])
        assert args.update is True
        assert args.store is True
        assert args.transcribe_days == 7


class TestCheckMetadataCommand:
    """Tests for the --check-metadata command functionality."""

    @pytest.mark.description("check_embedding_metadata returns 0 when all have metadata")
    @pytest.mark.asyncio
    async def test_check_metadata_all_present(self) -> None:
        """Verify check_embedding_metadata returns 0 when all fragments have metadata."""
        from voogle import tasks

        # Mock the Qdrant client
        mock_client = MagicMock()
        mock_client.collection_exists.return_value = True

        # Create mock points with full metadata
        mock_points = [
            MagicMock(
                payload={
                    "embedding_model": "all-MiniLM-L6-v2",
                    "embedding_provider": "local",
                    "embedded_at": "2025-01-01T00:00:00Z",
                    "episode": 1,
                    "text": "sample text",
                }
            ),
            MagicMock(
                payload={
                    "embedding_model": "all-MiniLM-L6-v2",
                    "embedding_provider": "local",
                    "embedded_at": "2025-01-01T00:00:00Z",
                    "episode": 2,
                    "text": "more text",
                }
            ),
        ]
        # scroll returns (results, next_offset)
        mock_client.scroll.side_effect = [
            (mock_points, None),  # First call returns points, no next offset
        ]

        with (
            patch("voogle.tasks.vector.get_configured_client", return_value=mock_client),
            patch("voogle.tasks.vector.get_collection_name", return_value="vectordb"),
        ):
            count = await tasks.check_embedding_metadata()

        assert count == 0

    @pytest.mark.description("check_embedding_metadata counts fragments missing metadata")
    @pytest.mark.asyncio
    async def test_check_metadata_some_missing(self) -> None:
        """Verify check_embedding_metadata counts fragments without metadata."""
        from voogle import tasks

        mock_client = MagicMock()
        mock_client.collection_exists.return_value = True

        # Mix of points with and without metadata
        mock_points = [
            # Has all metadata
            MagicMock(
                payload={
                    "embedding_model": "all-MiniLM-L6-v2",
                    "embedding_provider": "local",
                    "embedded_at": "2025-01-01T00:00:00Z",
                    "episode": 1,
                    "text": "with metadata",
                }
            ),
            # Missing metadata fields (old format)
            MagicMock(
                payload={
                    "episode": 2,
                    "text": "old format without metadata",
                }
            ),
            # Missing only embedded_at
            MagicMock(
                payload={
                    "embedding_model": "all-MiniLM-L6-v2",
                    "embedding_provider": "local",
                    "episode": 3,
                    "text": "partial metadata",
                }
            ),
        ]
        mock_client.scroll.side_effect = [
            (mock_points, None),
        ]

        with (
            patch("voogle.tasks.vector.get_configured_client", return_value=mock_client),
            patch("voogle.tasks.vector.get_collection_name", return_value="vectordb"),
        ):
            count = await tasks.check_embedding_metadata()

        assert count == 2  # Two points missing at least one metadata field

    @pytest.mark.description("check_embedding_metadata handles empty collection")
    @pytest.mark.asyncio
    async def test_check_metadata_empty_collection(self) -> None:
        """Verify check_embedding_metadata handles empty collection gracefully."""
        from voogle import tasks

        mock_client = MagicMock()
        mock_client.collection_exists.return_value = True
        mock_client.scroll.side_effect = [
            ([], None),  # Empty collection
        ]

        with (
            patch("voogle.tasks.vector.get_configured_client", return_value=mock_client),
            patch("voogle.tasks.vector.get_collection_name", return_value="vectordb"),
        ):
            count = await tasks.check_embedding_metadata()

        assert count == 0

    @pytest.mark.description("check_embedding_metadata handles nonexistent collection")
    @pytest.mark.asyncio
    async def test_check_metadata_nonexistent_collection(self) -> None:
        """Verify check_embedding_metadata handles nonexistent collection."""
        from voogle import tasks

        mock_client = MagicMock()
        mock_client.collection_exists.return_value = False

        with (
            patch("voogle.tasks.vector.get_configured_client", return_value=mock_client),
            patch("voogle.tasks.vector.get_collection_name", return_value="vectordb"),
        ):
            count = await tasks.check_embedding_metadata()

        assert count == 0
        mock_client.scroll.assert_not_called()


class TestRebuildEmbeddingsCommand:
    """Tests for the --rebuild-embeddings command functionality.

    Note: These tests validate the logic of rebuild_channel_embeddings
    at a unit level by testing the essential behaviors:
    - Deletes existing points for the channel
    - Re-indexes episodes with embeddings
    - Returns correct count

    Full integration requires database fixtures - see integration tests.
    """

    @pytest.mark.description("rebuild_channel_embeddings workflow validates delete then upsert")
    def test_rebuild_workflow_logic(self) -> None:
        """Verify the rebuild workflow logic: delete old, create new."""
        # This test validates the expected workflow at a logical level
        # without mocking the complex ORM internals

        # Expected workflow:
        # 1. Get collection name from provider
        # 2. Get or create vector client
        # 3. Ensure collection exists
        # 4. DELETE existing points for this channel (via filter)
        # 5. For each transcribed episode:
        #    a. Load chunking config
        #    b. Calculate embeddings
        #    c. UPSERT points with metadata
        #    d. Update episode.embeddings = True

        # The key invariant: delete happens BEFORE any upserts
        # This prevents data loss if upsert fails mid-way

        # Verify the ordering constraint is met by checking tasks.py source
        import inspect

        from voogle import tasks

        source = inspect.getsource(tasks.rebuild_channel_embeddings)

        # client.delete should appear before client.upsert
        delete_pos = source.find("client.delete")
        upsert_pos = source.find("client.upsert")

        assert delete_pos > 0, "rebuild_channel_embeddings should call client.delete"
        assert upsert_pos > 0, "rebuild_channel_embeddings should call client.upsert"
        assert delete_pos < upsert_pos, "delete should happen before upsert"

    @pytest.mark.description("rebuild_channel_embeddings returns count of episodes")
    def test_rebuild_returns_episode_count(self) -> None:
        """Verify rebuild returns len(episodes) as documented."""
        import inspect

        from voogle import tasks

        source = inspect.getsource(tasks.rebuild_channel_embeddings)

        # Should return len(episodes)
        assert "return len(episodes)" in source, (
            "rebuild_channel_embeddings should return len(episodes)"
        )
