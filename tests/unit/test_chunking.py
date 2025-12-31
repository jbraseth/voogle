# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for chunking configuration."""
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from voogle.chunking import (
    DEFAULT_CONFIG,
    ChunkingConfig,
    _get_config_path,
    load_chunking_config,
)

pytestmark = pytest.mark.unit


class TestChunkingConfig:
    """Tests for ChunkingConfig dataclass."""

    @pytest.mark.description("Default config values are correct")
    def test_default_values(self) -> None:
        config = ChunkingConfig()
        assert config.chunk_size_words == 40
        assert config.chunk_overlap_words == 0
        assert config.min_chunk_length_words == 10

    @pytest.mark.description("Custom values are accepted")
    def test_custom_values(self) -> None:
        config = ChunkingConfig(
            chunk_size_words=60,
            chunk_overlap_words=15,
            min_chunk_length_words=5,
        )
        assert config.chunk_size_words == 60
        assert config.chunk_overlap_words == 15
        assert config.min_chunk_length_words == 5

    @pytest.mark.description("Invalid chunk_size_words raises ValueError")
    def test_invalid_chunk_size(self) -> None:
        with pytest.raises(ValueError, match="chunk_size_words must be >= 1"):
            ChunkingConfig(chunk_size_words=0)
        with pytest.raises(ValueError, match="chunk_size_words must be >= 1"):
            ChunkingConfig(chunk_size_words=-1)

    @pytest.mark.description("Negative chunk_overlap_words raises ValueError")
    def test_negative_overlap(self) -> None:
        with pytest.raises(ValueError, match="chunk_overlap_words must be >= 0"):
            ChunkingConfig(chunk_overlap_words=-1)

    @pytest.mark.description("Overlap >= chunk_size raises ValueError")
    def test_overlap_too_large(self) -> None:
        with pytest.raises(ValueError, match="chunk_overlap_words .* must be < chunk_size_words"):
            ChunkingConfig(chunk_size_words=40, chunk_overlap_words=40)
        with pytest.raises(ValueError, match="chunk_overlap_words .* must be < chunk_size_words"):
            ChunkingConfig(chunk_size_words=40, chunk_overlap_words=50)

    @pytest.mark.description("Invalid min_chunk_length_words raises ValueError")
    def test_invalid_min_length(self) -> None:
        with pytest.raises(ValueError, match="min_chunk_length_words must be >= 1"):
            ChunkingConfig(min_chunk_length_words=0)

    @pytest.mark.description("Config is immutable (frozen dataclass)")
    def test_immutable(self) -> None:
        config = ChunkingConfig()
        with pytest.raises(Exception):  # FrozenInstanceError
            config.chunk_size_words = 100  # type: ignore[misc]


class TestLoadChunkingConfig:
    """Tests for load_chunking_config function."""

    @pytest.mark.description("Returns default when config file doesn't exist")
    def test_missing_file_returns_default(self) -> None:
        with patch.object(Path, "exists", return_value=False):
            config = load_chunking_config()
        assert config == DEFAULT_CONFIG

    @pytest.mark.description("Returns default when file is empty")
    def test_empty_file_returns_default(self) -> None:
        with patch.object(Path, "exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="")):
                config = load_chunking_config()
        assert config == DEFAULT_CONFIG

    @pytest.mark.description("Loads default section from config file")
    def test_loads_default_section(self) -> None:
        yaml_content = """
default:
  chunk_size_words: 50
  chunk_overlap_words: 10
  min_chunk_length_words: 8
"""
        with patch.object(Path, "exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=yaml_content)):
                config = load_chunking_config()
        assert config.chunk_size_words == 50
        assert config.chunk_overlap_words == 10
        assert config.min_chunk_length_words == 8

    @pytest.mark.description("Loads channel-specific config with defaults merged")
    def test_loads_channel_config(self) -> None:
        yaml_content = """
default:
  chunk_size_words: 40
  chunk_overlap_words: 0
  min_chunk_length_words: 10

channels:
  channel_abc:
    chunk_size_words: 60
    chunk_overlap_words: 15
"""
        with patch.object(Path, "exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=yaml_content)):
                config = load_chunking_config("channel_abc")
        assert config.chunk_size_words == 60
        assert config.chunk_overlap_words == 15
        assert config.min_chunk_length_words == 10  # Inherited from default

    @pytest.mark.description("Unknown channel falls back to default")
    def test_unknown_channel_uses_default(self) -> None:
        yaml_content = """
default:
  chunk_size_words: 40
  chunk_overlap_words: 0
  min_chunk_length_words: 10
"""
        with patch.object(Path, "exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=yaml_content)):
                config = load_chunking_config("unknown_channel")
        assert config.chunk_size_words == 40

    @pytest.mark.description("None channel_id uses default config")
    def test_none_channel_uses_default(self) -> None:
        yaml_content = """
default:
  chunk_size_words: 45

channels:
  channel_abc:
    chunk_size_words: 60
"""
        with patch.object(Path, "exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=yaml_content)):
                config = load_chunking_config(None)
        assert config.chunk_size_words == 45


class TestConfigPath:
    """Tests for config path resolution."""

    @pytest.mark.description("Config path points to config/chunking.yaml")
    def test_config_path_location(self) -> None:
        path = _get_config_path()
        assert path.name == "chunking.yaml"
        assert path.parent.name == "config"
