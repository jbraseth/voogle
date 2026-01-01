# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for LocalFeed dataclass validation."""

from pathlib import Path

import pytest
from voogle.sources import ConfigurationError, LocalFeed

pytestmark = pytest.mark.unit


class TestLocalFeedValidation:
    """Test LocalFeed boundary validation (fail loud principle)."""

    @pytest.mark.description("LocalFeed accepts valid configuration")
    def test_valid_local_feed(self, tmp_path: Path) -> None:
        """Valid LocalFeed with all required fields."""
        # Create a valid XML file
        feed_path = tmp_path / "test.xml"
        feed_path.write_text('<?xml version="1.0"?><rss></rss>')

        feed = LocalFeed(
            path=feed_path.absolute(),
            source_id="youtube",
            channel_url="local://youtube/PLtest123",
        )

        assert feed.path == feed_path.absolute()
        assert feed.source_id == "youtube"
        assert feed.channel_url == "local://youtube/PLtest123"
        assert feed.exists() is True

    @pytest.mark.description("LocalFeed rejects relative paths")
    def test_rejects_relative_path(self, tmp_path: Path) -> None:
        """Relative paths should fail at boundary."""
        with pytest.raises(ConfigurationError, match="must be absolute"):
            LocalFeed(
                path=Path("relative/path/feed.xml"),
                source_id="youtube",
                channel_url="local://youtube/test",
            )

    @pytest.mark.description("LocalFeed rejects non-XML files")
    def test_rejects_non_xml_extension(self, tmp_path: Path) -> None:
        """Non-XML extensions should fail."""
        json_path = tmp_path / "feed.json"
        json_path.write_text("{}")

        with pytest.raises(ConfigurationError, match="must be XML"):
            LocalFeed(
                path=json_path.absolute(),
                source_id="youtube",
                channel_url="local://youtube/test",
            )

    @pytest.mark.description("LocalFeed rejects non-local URL schemes")
    def test_rejects_http_url(self, tmp_path: Path) -> None:
        """HTTP URLs should fail - must use local:// scheme."""
        feed_path = tmp_path / "feed.xml"
        feed_path.write_text('<?xml version="1.0"?><rss></rss>')

        with pytest.raises(ConfigurationError, match="local://"):
            LocalFeed(
                path=feed_path.absolute(),
                source_id="youtube",
                channel_url="https://example.com/feed",
            )

    @pytest.mark.description("LocalFeed rejects empty source_id")
    def test_rejects_empty_source_id(self, tmp_path: Path) -> None:
        """Empty source_id should fail."""
        feed_path = tmp_path / "feed.xml"
        feed_path.write_text('<?xml version="1.0"?><rss></rss>')

        with pytest.raises(ConfigurationError, match="source_id cannot be empty"):
            LocalFeed(
                path=feed_path.absolute(),
                source_id="",
                channel_url="local://youtube/test",
            )

    @pytest.mark.description("LocalFeed exists() returns False for missing file")
    def test_exists_false_for_missing_file(self, tmp_path: Path) -> None:
        """exists() should return False if file doesn't exist."""
        # Create path but don't create the file
        feed_path = tmp_path / "nonexistent.xml"

        feed = LocalFeed(
            path=feed_path.absolute(),
            source_id="youtube",
            channel_url="local://youtube/test",
        )

        assert feed.exists() is False

    @pytest.mark.description("LocalFeed is immutable (frozen dataclass)")
    def test_immutable(self, tmp_path: Path) -> None:
        """LocalFeed should be immutable after creation."""
        feed_path = tmp_path / "feed.xml"
        feed_path.write_text('<?xml version="1.0"?><rss></rss>')

        feed = LocalFeed(
            path=feed_path.absolute(),
            source_id="youtube",
            channel_url="local://youtube/test",
        )

        with pytest.raises(Exception):  # FrozenInstanceError
            feed.source_id = "changed"  # type: ignore


class TestLocalFeedEdgeCases:
    """Edge case tests for LocalFeed."""

    @pytest.mark.description("LocalFeed handles Unicode in channel_url")
    def test_unicode_channel_url(self, tmp_path: Path) -> None:
        """Channel URL with Unicode characters should work."""
        feed_path = tmp_path / "feed.xml"
        feed_path.write_text('<?xml version="1.0"?><rss></rss>')

        feed = LocalFeed(
            path=feed_path.absolute(),
            source_id="youtube",
            channel_url="local://youtube/playlist-日本語",
        )

        assert "日本語" in feed.channel_url

    @pytest.mark.description("LocalFeed handles spaces in path")
    def test_path_with_spaces(self, tmp_path: Path) -> None:
        """Paths with spaces should work."""
        spaced_dir = tmp_path / "path with spaces"
        spaced_dir.mkdir()
        feed_path = spaced_dir / "feed.xml"
        feed_path.write_text('<?xml version="1.0"?><rss></rss>')

        feed = LocalFeed(
            path=feed_path.absolute(),
            source_id="youtube",
            channel_url="local://youtube/test",
        )

        assert feed.exists() is True
