# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for voogle-episodes CLI commands.

Tests for CLI argument parsing and command execution paths.
"""
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytestmark = pytest.mark.unit


class TestCheckMetadataCommand:
    """Tests for --check-metadata CLI command."""

    @pytest.mark.description("--check-metadata calls check_embedding_metadata task")
    async def test_check_metadata_calls_task(self) -> None:
        """Verify --check-metadata invokes the correct task function."""
        with patch("voogle.cli.episodes.tasks") as mock_tasks:
            mock_tasks.check_embedding_metadata = AsyncMock(return_value=0)

            # Simulate CLI execution
            test_args = ["episodes", "--check-metadata"]
            with patch.object(sys, "argv", test_args):
                from voogle.cli.episodes import _main

                await _main()

            mock_tasks.check_embedding_metadata.assert_called_once()

    @pytest.mark.description("--check-metadata logs warning when metadata missing")
    async def test_check_metadata_logs_warning_when_missing(self) -> None:
        """Verify warning is logged when fragments are missing metadata."""
        with patch("voogle.cli.episodes.tasks") as mock_tasks:
            mock_tasks.check_embedding_metadata = AsyncMock(return_value=42)

            with patch("voogle.cli.episodes.logger") as mock_logger:
                test_args = ["episodes", "--check-metadata"]
                with patch.object(sys, "argv", test_args):
                    from voogle.cli.episodes import _main

                    await _main()

                # Should log warning with count
                mock_logger.warning.assert_called()
                call_args = str(mock_logger.warning.call_args)
                assert "42" in call_args

    @pytest.mark.description("--check-metadata logs info when all metadata present")
    async def test_check_metadata_logs_info_when_complete(self) -> None:
        """Verify info is logged when all fragments have metadata."""
        with patch("voogle.cli.episodes.tasks") as mock_tasks:
            mock_tasks.check_embedding_metadata = AsyncMock(return_value=0)

            with patch("voogle.cli.episodes.logger") as mock_logger:
                test_args = ["episodes", "--check-metadata"]
                with patch.object(sys, "argv", test_args):
                    from voogle.cli.episodes import _main

                    await _main()

                # Should log info about all metadata present
                mock_logger.info.assert_called()


class TestRebuildEmbeddingsCommand:
    """Tests for --rebuild-embeddings CLI command."""

    @pytest.mark.description("--rebuild-embeddings requires --reindex-channel")
    async def test_rebuild_embeddings_requires_channel(self) -> None:
        """Verify --rebuild-embeddings fails without --reindex-channel."""
        test_args = ["episodes", "--rebuild-embeddings"]

        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit):
                from voogle.cli.episodes import _main

                await _main()

    @pytest.mark.description("--rebuild-embeddings with channel calls rebuild task")
    async def test_rebuild_embeddings_with_channel(self) -> None:
        """Verify --rebuild-embeddings with valid channel calls the task."""
        mock_channel = MagicMock()
        mock_channel.pk = "test-channel-id"

        with patch("voogle.cli.episodes.tasks") as mock_tasks:
            mock_tasks.rebuild_channel_embeddings = AsyncMock(return_value=10)

            with patch("voogle.cli.episodes.models") as mock_models:
                mock_models.Channel.objects.get = AsyncMock(return_value=mock_channel)

                with patch("voogle.cli.episodes.embedding") as mock_embedding:
                    mock_provider = MagicMock()
                    mock_provider.provider_name = "local"
                    mock_provider.model_name = "test-model"
                    mock_embedding.get_embeddings_provider.return_value = mock_provider

                    test_args = [
                        "episodes",
                        "--rebuild-embeddings",
                        "--reindex-channel",
                        "test-channel-id",
                    ]
                    with patch.object(sys, "argv", test_args):
                        from voogle.cli.episodes import _main

                        await _main()

                    mock_tasks.rebuild_channel_embeddings.assert_called_once()

    @pytest.mark.description("--rebuild-embeddings with --provider uses explicit provider")
    async def test_rebuild_embeddings_with_provider_override(self) -> None:
        """Verify --provider flag overrides default provider."""
        mock_channel = MagicMock()
        mock_channel.pk = "test-channel-id"

        with patch("voogle.cli.episodes.tasks") as mock_tasks:
            mock_tasks.rebuild_channel_embeddings = AsyncMock(return_value=5)

            with patch("voogle.cli.episodes.models") as mock_models:
                mock_models.Channel.objects.get = AsyncMock(return_value=mock_channel)

                with patch("voogle.cli.episodes.embedding") as mock_embedding:
                    mock_provider = MagicMock()
                    mock_provider.provider_name = "openai"
                    mock_provider.model_name = "text-embedding-3-small"
                    mock_embedding.get_embeddings_provider_by_name.return_value = mock_provider

                    test_args = [
                        "episodes",
                        "--rebuild-embeddings",
                        "--reindex-channel",
                        "test-channel-id",
                        "--provider",
                        "openai",
                    ]
                    with patch.object(sys, "argv", test_args):
                        from voogle.cli.episodes import _main

                        await _main()

                    # Should use get_embeddings_provider_by_name, not get_embeddings_provider
                    mock_embedding.get_embeddings_provider_by_name.assert_called_once_with(
                        "openai"
                    )
                    mock_embedding.get_embeddings_provider.assert_not_called()


class TestUpdateCommand:
    """Tests for --update CLI command."""

    @pytest.mark.description("--update calls update_channels and add_default_channels")
    async def test_update_calls_correct_functions(self) -> None:
        """Verify --update invokes the correct task functions."""
        with patch("voogle.cli.episodes.collection") as mock_collection:
            mock_collection.add_default_channels = AsyncMock()

            with patch("voogle.cli.episodes.tasks") as mock_tasks:
                mock_tasks.update_channels = AsyncMock(return_value=5)

                test_args = ["episodes", "--update"]
                with patch.object(sys, "argv", test_args):
                    from voogle.cli.episodes import _main

                    await _main()

                mock_collection.add_default_channels.assert_called_once()
                mock_tasks.update_channels.assert_called_once()


class TestStoreCommand:
    """Tests for --store CLI command."""

    @pytest.mark.description("--store calls store_episodes_embeddings")
    async def test_store_calls_task(self) -> None:
        """Verify --store invokes store_episodes_embeddings."""
        with patch("voogle.cli.episodes.tasks") as mock_tasks:
            mock_tasks.store_episodes_embeddings = AsyncMock()

            test_args = ["episodes", "--store"]
            with patch.object(sys, "argv", test_args):
                from voogle.cli.episodes import _main

                await _main()

            mock_tasks.store_episodes_embeddings.assert_called_once()


class TestTranscribeCommand:
    """Tests for --transcribe-days CLI command."""

    @pytest.mark.description("--transcribe-days with positive value calls transcribe_episodes")
    async def test_transcribe_days_positive(self) -> None:
        """Verify --transcribe-days with positive value works."""
        with patch("voogle.cli.episodes.tasks") as mock_tasks:
            mock_tasks.transcribe_episodes = AsyncMock(return_value=10)

            test_args = ["episodes", "--transcribe-days", "7"]
            with patch.object(sys, "argv", test_args):
                from voogle.cli.episodes import _main

                await _main()

            mock_tasks.transcribe_episodes.assert_called_once_with(7)

    @pytest.mark.description("--transcribe-days with zero or negative does nothing")
    async def test_transcribe_days_zero_or_negative(self) -> None:
        """Verify --transcribe-days with 0 or negative doesn't call task."""
        with patch("voogle.cli.episodes.tasks") as mock_tasks:
            mock_tasks.transcribe_episodes = AsyncMock(return_value=0)

            # Default is -1, which should not trigger transcription
            test_args = ["episodes"]
            with patch.object(sys, "argv", test_args):
                from voogle.cli.episodes import _main

                await _main()

            mock_tasks.transcribe_episodes.assert_not_called()
