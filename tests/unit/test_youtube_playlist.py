# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for YouTube playlist source adapter.

Tests are organized by function:
- Data types (PlannedEpisode, DownloadResult, DownloadStatus)
- scan() - playlist scanning without download
- sync_media() - audio file downloading with skip/retry logic
- emit_rss() - RSS feed generation
"""

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch
import xml.etree.ElementTree as ET

import pytest

# Skip all tests in this module if yt-dlp is not installed
# (CI image may not have it until PR is merged)
pytest.importorskip("yt_dlp", reason="yt-dlp not installed")

from voogle.sources.youtube_playlist import (
    DownloadResult,
    DownloadStatus,
    PlannedEpisode,
    YouTubePlaylistError,
    _make_filename,
    _parse_upload_date,
    emit_rss,
    scan,
    sync_media,
)

pytestmark = pytest.mark.unit


# =============================================================================
# Helper Function Tests
# =============================================================================


class TestMakeFilename:
    @pytest.mark.description("_make_filename generates correct pattern with video ID")
    def test_basic_filename(self) -> None:
        result = _make_filename("My Video Title", "dQw4w9WgXcQ")
        assert result == "My Video Title [dQw4w9WgXcQ].mp3"

    @pytest.mark.description("_make_filename handles special characters in title")
    def test_special_characters_in_title(self) -> None:
        result = _make_filename("Video: Part 1 - (Full)", "abc123")
        assert result == "Video: Part 1 - (Full) [abc123].mp3"

    @pytest.mark.description("_make_filename handles YouTube IDs with brackets/hyphens")
    def test_youtube_id_with_special_chars(self) -> None:
        # YouTube IDs can contain hyphens and underscores
        result = _make_filename("Test", "-_Ab12Cd34Ef")
        assert result == "Test [-_Ab12Cd34Ef].mp3"

    @pytest.mark.description("_make_filename preserves brackets in video ID for glob escaping")
    def test_brackets_in_filename_need_glob_escaping(self) -> None:
        # This test documents that filenames with [id] pattern need glob escaping
        # when searching for files (e.g., glob.glob needs [[] escaping)
        filename = _make_filename("Example", "abc123")
        assert "[" in filename and "]" in filename
        # The actual glob escaping happens at file search time, not filename generation


class TestParseUploadDate:
    @pytest.mark.description("_parse_upload_date parses YYYYMMDD format")
    def test_valid_date(self) -> None:
        result = _parse_upload_date("20240115")
        assert result == datetime(2024, 1, 15, tzinfo=timezone.utc)

    @pytest.mark.description("_parse_upload_date returns None for None input")
    def test_none_input(self) -> None:
        result = _parse_upload_date(None)
        assert result is None

    @pytest.mark.description("_parse_upload_date returns None for invalid format")
    def test_invalid_format(self) -> None:
        result = _parse_upload_date("2024-01-15")  # Wrong format
        assert result is None

    @pytest.mark.description("_parse_upload_date returns None for empty string")
    def test_empty_string(self) -> None:
        result = _parse_upload_date("")
        assert result is None


# =============================================================================
# Data Type Tests
# =============================================================================


class TestDownloadStatus:
    @pytest.mark.description("DownloadStatus enum has expected values")
    def test_status_values(self) -> None:
        assert DownloadStatus.SUCCESS.value == "success"
        assert DownloadStatus.FAILED.value == "failed"
        assert DownloadStatus.SKIPPED.value == "skipped"


class TestPlannedEpisode:
    @pytest.mark.description("PlannedEpisode can be created with all fields")
    def test_create_with_all_fields(self) -> None:
        ep = PlannedEpisode(
            video_id="abc123",
            title="Test Video",
            description="A test video description",
            duration_seconds=300,
            upload_date=datetime(2024, 1, 15, tzinfo=timezone.utc),
            playlist_title="Test Playlist",
            playlist_index=1,
            expected_filename="Test Video [abc123].mp3",
        )
        assert ep.video_id == "abc123"
        assert ep.title == "Test Video"
        assert ep.duration_seconds == 300
        assert ep.playlist_index == 1

    @pytest.mark.description("PlannedEpisode handles None for optional fields")
    def test_create_with_optional_none(self) -> None:
        ep = PlannedEpisode(
            video_id="xyz789",
            title="Another Video",
            description="",
            duration_seconds=None,
            upload_date=None,
            playlist_title="Playlist",
            playlist_index=None,
            expected_filename="Another Video [xyz789].mp3",
        )
        assert ep.duration_seconds is None
        assert ep.upload_date is None
        assert ep.playlist_index is None


class TestDownloadResult:
    @pytest.mark.description("DownloadResult represents successful download")
    def test_success_result(self) -> None:
        result = DownloadResult(
            video_id="abc123",
            status=DownloadStatus.SUCCESS,
            filepath=Path("/tmp/video.mp3"),
            error=None,
        )
        assert result.status == DownloadStatus.SUCCESS
        assert result.filepath is not None
        assert result.error is None

    @pytest.mark.description("DownloadResult represents failed download")
    def test_failed_result(self) -> None:
        result = DownloadResult(
            video_id="abc123",
            status=DownloadStatus.FAILED,
            filepath=None,
            error="HTTP 403: Forbidden",
        )
        assert result.status == DownloadStatus.FAILED
        assert result.filepath is None
        assert result.error == "HTTP 403: Forbidden"

    @pytest.mark.description("DownloadResult represents skipped download")
    def test_skipped_result(self) -> None:
        result = DownloadResult(
            video_id="abc123",
            status=DownloadStatus.SKIPPED,
            filepath=Path("/tmp/existing.mp3"),
            error=None,
        )
        assert result.status == DownloadStatus.SKIPPED
        assert result.filepath is not None


# =============================================================================
# scan() Tests
# =============================================================================


class TestScan:
    @pytest.mark.description("scan() returns list of PlannedEpisode from playlist")
    def test_scan_returns_episodes(self) -> None:
        mock_info = {
            "title": "Test Playlist",
            "entries": [
                {
                    "id": "video1",
                    "title": "First Video",
                    "description": "Description 1",
                    "duration": 120,
                    "upload_date": "20240115",
                    "playlist_index": 1,
                },
                {
                    "id": "video2",
                    "title": "Second Video",
                    "description": "Description 2",
                    "duration": 180,
                    "upload_date": "20240116",
                    "playlist_index": 2,
                },
            ],
        }

        with patch("voogle.sources.youtube_playlist.YoutubeDL") as mock_ydl_class:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = mock_info
            mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
            mock_ydl.__exit__ = MagicMock(return_value=False)
            mock_ydl_class.return_value = mock_ydl

            episodes = scan("https://www.youtube.com/playlist?list=PLtest")

        assert len(episodes) == 2
        assert episodes[0].video_id == "video1"
        assert episodes[0].title == "First Video"
        assert episodes[0].playlist_title == "Test Playlist"
        assert episodes[1].video_id == "video2"
        assert episodes[1].playlist_index == 2

    @pytest.mark.description("scan() handles empty playlist")
    def test_scan_empty_playlist(self) -> None:
        mock_info = {
            "title": "Empty Playlist",
            "entries": [],
        }

        with patch("voogle.sources.youtube_playlist.YoutubeDL") as mock_ydl_class:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = mock_info
            mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
            mock_ydl.__exit__ = MagicMock(return_value=False)
            mock_ydl_class.return_value = mock_ydl

            episodes = scan("https://www.youtube.com/playlist?list=PLempty")

        assert episodes == []

    @pytest.mark.description("scan() raises YouTubePlaylistError on failure")
    def test_scan_raises_on_error(self) -> None:
        with patch("voogle.sources.youtube_playlist.YoutubeDL") as mock_ydl_class:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.side_effect = Exception("Network error")
            mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
            mock_ydl.__exit__ = MagicMock(return_value=False)
            mock_ydl_class.return_value = mock_ydl

            with pytest.raises(YouTubePlaylistError) as exc_info:
                scan("https://invalid-url")

            assert "Network error" in str(exc_info.value)

    @pytest.mark.description("scan() handles missing optional fields gracefully")
    def test_scan_missing_fields(self) -> None:
        mock_info = {
            "title": "Sparse Playlist",
            "entries": [
                {
                    "id": "video1",
                    "title": "Minimal Video",
                    # No description, duration, upload_date, playlist_index
                },
            ],
        }

        with patch("voogle.sources.youtube_playlist.YoutubeDL") as mock_ydl_class:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = mock_info
            mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
            mock_ydl.__exit__ = MagicMock(return_value=False)
            mock_ydl_class.return_value = mock_ydl

            episodes = scan("https://www.youtube.com/playlist?list=PLsparse")

        assert len(episodes) == 1
        assert episodes[0].description == ""
        assert episodes[0].duration_seconds is None
        assert episodes[0].upload_date is None
        assert episodes[0].playlist_index is None

    @pytest.mark.description("scan() skips entries without id or title")
    def test_scan_skips_invalid_entries(self) -> None:
        mock_info = {
            "title": "Mixed Playlist",
            "entries": [
                {"id": "valid1", "title": "Valid Video"},
                {"id": "no_title"},  # Missing title
                {"title": "No ID"},  # Missing id
                None,  # Null entry
                {"id": "valid2", "title": "Another Valid"},
            ],
        }

        with patch("voogle.sources.youtube_playlist.YoutubeDL") as mock_ydl_class:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = mock_info
            mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
            mock_ydl.__exit__ = MagicMock(return_value=False)
            mock_ydl_class.return_value = mock_ydl

            episodes = scan("https://www.youtube.com/playlist?list=PLmixed")

        assert len(episodes) == 2
        assert episodes[0].video_id == "valid1"
        assert episodes[1].video_id == "valid2"


# =============================================================================
# Fixture-Based Integration Tests (Dry Run)
# =============================================================================


class TestDryRunWithFixtures:
    """Integration-ish tests using JSON fixture files.

    These tests verify the full scan→emit_rss workflow without network calls.
    They use realistic fixture data to catch regressions in data mapping.
    """

    @pytest.fixture
    def playlist_fixture_path(self) -> Path:
        return Path(__file__).parent.parent / "fixtures" / "youtube" / "playlist_metadata.json"

    @pytest.fixture
    def playlist_metadata(self, playlist_fixture_path: Path) -> dict:
        import json

        return json.loads(playlist_fixture_path.read_text())

    @pytest.mark.description("scan() correctly maps fixture data to PlannedEpisode list")
    def test_scan_with_fixture_data(self, playlist_metadata: dict) -> None:
        with patch("voogle.sources.youtube_playlist.YoutubeDL") as mock_ydl_class:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = playlist_metadata
            mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
            mock_ydl.__exit__ = MagicMock(return_value=False)
            mock_ydl_class.return_value = mock_ydl

            episodes = scan("https://www.youtube.com/playlist?list=PLtest")

        assert len(episodes) == 3
        assert episodes[0].video_id == "dQw4w9WgXcQ"
        assert episodes[0].title == "Episode 1: Getting Started"
        assert episodes[0].playlist_title == "Test Podcast Playlist"
        assert episodes[0].expected_filename == "Episode 1: Getting Started [dQw4w9WgXcQ].mp3"

        # Second episode has special chars in ID
        assert episodes[1].video_id == "abc-_123XYZ"
        assert episodes[1].expected_filename == "Episode 2: Advanced Topics (Part 1) [abc-_123XYZ].mp3"

        # Third episode tests Q&A special chars
        assert episodes[2].title == "Episode 3: Q&A - Your Questions Answered!"

    @pytest.mark.description("Full dry-run: scan fixture → emit RSS → validate structure")
    def test_full_dryrun_workflow(self, playlist_metadata: dict, tmp_path: Path) -> None:
        # Step 1: Scan (mocked)
        with patch("voogle.sources.youtube_playlist.YoutubeDL") as mock_ydl_class:
            mock_ydl = MagicMock()
            mock_ydl.extract_info.return_value = playlist_metadata
            mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
            mock_ydl.__exit__ = MagicMock(return_value=False)
            mock_ydl_class.return_value = mock_ydl

            episodes = scan("https://www.youtube.com/playlist?list=PLtest")

        # Step 2: Simulate downloaded files (skip actual download)
        playlist_dir = tmp_path / "Test Podcast Playlist"
        playlist_dir.mkdir()
        for ep in episodes:
            (playlist_dir / ep.expected_filename).write_bytes(b"fake audio")

        # Step 3: Emit RSS
        feed_path = tmp_path / "feed.xml"
        result = emit_rss(episodes, tmp_path, feed_path, base_url="http://localhost:8080/local")

        # Step 4: Validate RSS structure
        assert result == feed_path
        tree = ET.parse(feed_path)
        root = tree.getroot()

        assert root.tag == "rss"
        channel = root.find("channel")
        assert channel.find("title").text == "Test Podcast Playlist"

        items = channel.findall("item")
        assert len(items) == 3

        # Verify enclosure URLs are correct
        first_enclosure = items[0].find("enclosure")
        assert "dQw4w9WgXcQ" in first_enclosure.get("url")
        assert first_enclosure.get("type") == "audio/mpeg"

    @pytest.mark.description("Dry-run handles special characters in filenames correctly")
    def test_dryrun_special_characters(self, tmp_path: Path) -> None:
        # Create episode with problematic characters
        episodes = [
            PlannedEpisode(
                video_id="test[id]123",  # Brackets in ID (edge case)
                title="Video: Part 1 - (Q&A)",
                description="Special chars test",
                duration_seconds=100,
                upload_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
                playlist_title="Test Playlist",
                playlist_index=1,
                expected_filename="Video: Part 1 - (Q&A) [test[id]123].mp3",
            ),
        ]

        # Create the file
        playlist_dir = tmp_path / "Test Playlist"
        playlist_dir.mkdir()
        (playlist_dir / episodes[0].expected_filename).write_bytes(b"audio")

        # Emit RSS
        feed_path = tmp_path / "feed.xml"
        emit_rss(episodes, tmp_path, feed_path, base_url="http://example.com")

        # Parse and verify
        tree = ET.parse(feed_path)
        item = tree.getroot().find("channel").find("item")
        assert item.find("title").text == "Video: Part 1 - (Q&A)"
        assert item.find("guid").text == "test[id]123"


# =============================================================================
# sync_media() Tests
# =============================================================================


class TestSyncMedia:
    @pytest.fixture
    def sample_episodes(self) -> list[PlannedEpisode]:
        return [
            PlannedEpisode(
                video_id="vid1",
                title="Video One",
                description="Desc 1",
                duration_seconds=100,
                upload_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
                playlist_title="Playlist",
                playlist_index=1,
                expected_filename="Video One [vid1].mp3",
            ),
            PlannedEpisode(
                video_id="vid2",
                title="Video Two",
                description="Desc 2",
                duration_seconds=200,
                upload_date=datetime(2024, 1, 2, tzinfo=timezone.utc),
                playlist_title="Playlist",
                playlist_index=2,
                expected_filename="Video Two [vid2].mp3",
            ),
        ]

    @pytest.mark.description("sync_media() skips already existing files")
    def test_skips_existing_files(
        self, sample_episodes: list[PlannedEpisode], tmp_path: Path
    ) -> None:
        # Files go in output_dir / playlist_title / filename
        playlist_dir = tmp_path / "Playlist"
        playlist_dir.mkdir()
        # Pre-create the file for vid1
        existing_file = playlist_dir / "Video One [vid1].mp3"
        existing_file.write_bytes(b"fake mp3 content")

        with patch("voogle.sources.youtube_playlist.YoutubeDL") as mock_ydl_class:
            mock_ydl = MagicMock()
            mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
            mock_ydl.__exit__ = MagicMock(return_value=False)
            mock_ydl_class.return_value = mock_ydl

            # output_dir is the root, playlist subfolder created automatically
            results = sync_media(sample_episodes, tmp_path)

        # vid1 should be skipped, vid2 should be attempted
        assert len(results) == 2
        assert results[0].status == DownloadStatus.SKIPPED
        assert results[0].filepath == existing_file

    @pytest.mark.description("sync_media() downloads missing files")
    def test_downloads_missing_files(
        self, sample_episodes: list[PlannedEpisode], tmp_path: Path
    ) -> None:
        with patch("voogle.sources.youtube_playlist.YoutubeDL") as mock_ydl_class:
            mock_ydl = MagicMock()
            mock_ydl.download.return_value = 0  # Success
            mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
            mock_ydl.__exit__ = MagicMock(return_value=False)
            mock_ydl_class.return_value = mock_ydl

            # Track which video is being downloaded
            download_index = [0]

            # Mock the file appearing after download
            def create_file_side_effect(urls: list[str]) -> int:
                playlist_dir = tmp_path / "Playlist"
                playlist_dir.mkdir(exist_ok=True)
                # Create file for current video being downloaded
                ep = sample_episodes[download_index[0]]
                (playlist_dir / ep.expected_filename).write_bytes(b"content")
                download_index[0] += 1
                return 0

            mock_ydl.download.side_effect = create_file_side_effect

            results = sync_media(sample_episodes, tmp_path)

        assert len(results) == 2
        # Both should be success after download creates files
        assert all(r.status == DownloadStatus.SUCCESS for r in results)

    @pytest.mark.description("sync_media() reports failures without crashing")
    def test_continues_on_failure(
        self, sample_episodes: list[PlannedEpisode], tmp_path: Path
    ) -> None:
        with patch("voogle.sources.youtube_playlist.YoutubeDL") as mock_ydl_class:
            mock_ydl = MagicMock()
            playlist_dir = tmp_path / "Playlist"

            # Track downloads by URL to simulate vid1 failing, vid2 succeeding
            def download_side_effect(urls: list[str]) -> int:
                url = urls[0] if urls else ""
                if "vid1" in url:
                    raise Exception("HTTP 403: Forbidden")
                # vid2 succeeds - create the file
                playlist_dir.mkdir(exist_ok=True)
                (playlist_dir / sample_episodes[1].expected_filename).write_bytes(
                    b"content"
                )
                return 0

            mock_ydl.download.side_effect = download_side_effect
            mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
            mock_ydl.__exit__ = MagicMock(return_value=False)
            mock_ydl_class.return_value = mock_ydl

            results = sync_media(sample_episodes, tmp_path)

        assert len(results) == 2
        # First failed (both web and android passes failed)
        assert results[0].status == DownloadStatus.FAILED
        assert "403" in str(results[0].error)
        assert results[1].status == DownloadStatus.SUCCESS

    @pytest.mark.description("sync_media() calls progress callback")
    def test_progress_callback(
        self, sample_episodes: list[PlannedEpisode], tmp_path: Path
    ) -> None:
        progress_calls: list[tuple] = []

        def on_progress(
            video_id: str, status: DownloadStatus, current: int, total: int
        ) -> None:
            progress_calls.append((video_id, status, current, total))

        with patch("voogle.sources.youtube_playlist.YoutubeDL") as mock_ydl_class:
            mock_ydl = MagicMock()
            playlist_dir = tmp_path / "Playlist"
            download_index = [0]

            def download_side_effect(urls: list[str]) -> int:
                playlist_dir.mkdir(exist_ok=True)
                # Create file for current video
                ep = sample_episodes[download_index[0]]
                (playlist_dir / ep.expected_filename).write_bytes(b"content")
                download_index[0] += 1
                return 0

            mock_ydl.download.side_effect = download_side_effect
            mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
            mock_ydl.__exit__ = MagicMock(return_value=False)
            mock_ydl_class.return_value = mock_ydl

            sync_media(sample_episodes, tmp_path, on_progress=on_progress)

        assert len(progress_calls) == 2
        assert progress_calls[0][0] == "vid1"
        assert progress_calls[0][2] == 1  # current
        assert progress_calls[0][3] == 2  # total
        assert progress_calls[1][0] == "vid2"
        assert progress_calls[1][2] == 2


# =============================================================================
# emit_rss() Tests
# =============================================================================


class TestEmitRss:
    @pytest.fixture
    def episodes_with_files(self, tmp_path: Path) -> tuple[list[PlannedEpisode], Path]:
        """Create episodes and their corresponding files.

        Returns (episodes, output_dir) where output_dir is the root
        and files are in output_dir / playlist_title / filename.
        """
        playlist_title = "My Podcast"
        playlist_dir = tmp_path / playlist_title
        playlist_dir.mkdir()

        episodes = [
            PlannedEpisode(
                video_id="vid1",
                title="Episode One",
                description="First episode description",
                duration_seconds=3600,
                upload_date=datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
                playlist_title=playlist_title,
                playlist_index=1,
                expected_filename="Episode One [vid1].mp3",
            ),
            PlannedEpisode(
                video_id="vid2",
                title="Episode Two",
                description="Second episode",
                duration_seconds=1800,
                upload_date=datetime(2024, 1, 20, 14, 30, 0, tzinfo=timezone.utc),
                playlist_title=playlist_title,
                playlist_index=2,
                expected_filename="Episode Two [vid2].mp3",
            ),
        ]

        # Create the files in playlist subfolder
        for ep in episodes:
            (playlist_dir / ep.expected_filename).write_bytes(b"fake audio content")

        # Return tmp_path as output_dir (root), not playlist_dir
        return episodes, tmp_path

    @pytest.mark.description("emit_rss() generates valid RSS XML")
    def test_generates_valid_xml(
        self, episodes_with_files: tuple[list[PlannedEpisode], Path], tmp_path: Path
    ) -> None:
        episodes, output_dir = episodes_with_files
        feed_path = tmp_path / "feed.xml"

        result = emit_rss(episodes, output_dir, feed_path)

        assert result == feed_path
        assert feed_path.exists()

        # Parse and validate XML structure
        tree = ET.parse(feed_path)
        root = tree.getroot()
        assert root.tag == "rss"
        assert root.get("version") == "2.0"

        channel = root.find("channel")
        assert channel is not None
        assert channel.find("title") is not None

        items = channel.findall("item")
        assert len(items) == 2

    @pytest.mark.description("emit_rss() includes correct item fields")
    def test_item_fields(
        self, episodes_with_files: tuple[list[PlannedEpisode], Path], tmp_path: Path
    ) -> None:
        episodes, output_dir = episodes_with_files
        feed_path = tmp_path / "feed.xml"

        emit_rss(episodes, output_dir, feed_path, base_url="http://localhost:8080")

        tree = ET.parse(feed_path)
        channel = tree.getroot().find("channel")
        items = channel.findall("item")

        first_item = items[0]
        assert first_item.find("title").text == "Episode One"
        assert first_item.find("description").text == "First episode description"

        enclosure = first_item.find("enclosure")
        assert enclosure is not None
        assert "Episode One [vid1].mp3" in enclosure.get("url")
        assert enclosure.get("type") == "audio/mpeg"

    @pytest.mark.description("emit_rss() only includes episodes with existing files")
    def test_only_includes_existing_files(self, tmp_path: Path) -> None:
        playlist_title = "TestPlaylist"
        playlist_dir = tmp_path / playlist_title
        playlist_dir.mkdir()

        episodes = [
            PlannedEpisode(
                video_id="exists",
                title="Exists",
                description="",
                duration_seconds=100,
                upload_date=None,
                playlist_title=playlist_title,
                playlist_index=1,
                expected_filename="Exists [exists].mp3",
            ),
            PlannedEpisode(
                video_id="missing",
                title="Missing",
                description="",
                duration_seconds=100,
                upload_date=None,
                playlist_title=playlist_title,
                playlist_index=2,
                expected_filename="Missing [missing].mp3",
            ),
        ]

        # Only create file for first episode (in playlist subfolder)
        (playlist_dir / "Exists [exists].mp3").write_bytes(b"content")

        feed_path = tmp_path / "feed.xml"
        emit_rss(episodes, tmp_path, feed_path)

        tree = ET.parse(feed_path)
        items = tree.getroot().find("channel").findall("item")
        assert len(items) == 1
        assert items[0].find("title").text == "Exists"

    @pytest.mark.description("emit_rss() uses base_url for enclosure URLs")
    def test_base_url_in_enclosure(
        self, episodes_with_files: tuple[list[PlannedEpisode], Path], tmp_path: Path
    ) -> None:
        episodes, output_dir = episodes_with_files
        feed_path = tmp_path / "feed.xml"

        emit_rss(
            episodes, output_dir, feed_path, base_url="http://example.com/media"
        )

        tree = ET.parse(feed_path)
        item = tree.getroot().find("channel").find("item")
        enclosure = item.find("enclosure")

        assert enclosure.get("url").startswith("http://example.com/media/")

    @pytest.mark.description("emit_rss() handles empty episode list")
    def test_empty_episodes(self, tmp_path: Path) -> None:
        output_dir = tmp_path / "Empty"
        output_dir.mkdir()
        feed_path = tmp_path / "feed.xml"

        result = emit_rss([], output_dir, feed_path)

        assert result == feed_path
        tree = ET.parse(feed_path)
        items = tree.getroot().find("channel").findall("item")
        assert len(items) == 0
