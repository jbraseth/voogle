# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for FetchingStage."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import responses
from voogle.pipeline import (
    ContentType,
    ContentTypeError,
    FetchError,
    FetchResult,
    StorageError,
)
from voogle.pipeline.fetching import FetchingStage

pytestmark = pytest.mark.unit


class TestFetchingStageInit:
    """Tests for FetchingStage initialization."""

    @pytest.mark.description("FetchingStage creates temp directory if none provided")
    def test_creates_temp_dir_if_none_provided(self) -> None:
        """Should create a temp directory when output_dir is None."""
        stage = FetchingStage()
        assert stage.output_dir.exists()
        assert stage.output_dir.is_dir()
        assert "voogle-fetch-" in str(stage.output_dir)

    @pytest.mark.description("FetchingStage uses provided output directory")
    def test_uses_provided_output_dir(self, tmp_path: Path) -> None:
        """Should use the provided output directory."""
        output_dir = tmp_path / "fetched"
        stage = FetchingStage(output_dir=output_dir)
        assert stage.output_dir == output_dir
        assert output_dir.exists()

    @pytest.mark.description("FetchingStage repr shows configuration")
    def test_repr(self, tmp_path: Path) -> None:
        """Should return informative repr string."""
        stage = FetchingStage(output_dir=tmp_path, enable_youtube=False)
        repr_str = repr(stage)
        assert "FetchingStage" in repr_str
        assert str(tmp_path) in repr_str
        assert "youtube=False" in repr_str

    @pytest.mark.description("FetchingStage str is human readable")
    def test_str(self, tmp_path: Path) -> None:
        """Should return human-readable string."""
        stage = FetchingStage(output_dir=tmp_path)
        str_str = str(stage)
        assert "FetchingStage" in str_str


class TestFetchingStageLocalFiles:
    """Tests for local file fetching."""

    @pytest.mark.description("FetchingStage fetches local MP3 file")
    def test_fetch_local_mp3(self, tmp_path: Path) -> None:
        """Should fetch local MP3 file and detect content type."""
        # Create test MP3 file
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        mp3_file = source_dir / "test.mp3"
        mp3_file.write_bytes(b"fake mp3 content")

        output_dir = tmp_path / "output"
        stage = FetchingStage(output_dir=output_dir)

        result = stage.process(str(mp3_file))

        assert result.source == str(mp3_file)
        assert result.content_type == ContentType.AUDIO_MP3
        assert result.size_bytes == 16
        assert Path(result.local_path).exists()
        assert "test.mp3" in result.local_path

    @pytest.mark.description("FetchingStage fetches local WAV file")
    def test_fetch_local_wav(self, tmp_path: Path) -> None:
        """Should fetch local WAV file."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        wav_file = source_dir / "test.wav"
        wav_file.write_bytes(b"fake wav content")

        output_dir = tmp_path / "output"
        stage = FetchingStage(output_dir=output_dir)

        result = stage.process(str(wav_file))

        assert result.content_type == ContentType.AUDIO_WAV

    @pytest.mark.description("FetchingStage handles file:// prefix")
    def test_fetch_file_protocol(self, tmp_path: Path) -> None:
        """Should handle file:// protocol prefix."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        mp3_file = source_dir / "test.mp3"
        mp3_file.write_bytes(b"fake mp3 content")

        output_dir = tmp_path / "output"
        stage = FetchingStage(output_dir=output_dir)

        result = stage.process(f"file://{mp3_file}")

        assert result.content_type == ContentType.AUDIO_MP3

    @pytest.mark.description("FetchingStage rejects missing local file")
    def test_fetch_missing_file_raises_error(self, tmp_path: Path) -> None:
        """Should raise FetchError for missing file."""
        stage = FetchingStage(output_dir=tmp_path)

        with pytest.raises(FetchError, match="not found"):
            stage.process("/nonexistent/file.mp3")

    @pytest.mark.description("FetchingStage rejects directory path")
    def test_fetch_directory_raises_error(self, tmp_path: Path) -> None:
        """Should raise FetchError when path is a directory."""
        stage = FetchingStage(output_dir=tmp_path / "output")

        with pytest.raises(FetchError, match="not a file"):
            stage.process(str(tmp_path))

    @pytest.mark.description("FetchingStage rejects empty source")
    def test_fetch_empty_source_raises_error(self, tmp_path: Path) -> None:
        """Should raise FetchError for empty source."""
        stage = FetchingStage(output_dir=tmp_path)

        with pytest.raises(FetchError, match="cannot be empty"):
            stage.process("")


class TestFetchingStageURLs:
    """Tests for URL fetching with mocked HTTP responses."""

    @responses.activate
    @pytest.mark.description("FetchingStage fetches HTTP URL")
    def test_fetch_http_url(self, tmp_path: Path) -> None:
        """Should fetch content from HTTP URL."""
        url = "http://example.com/audio.mp3"
        content = b"fake mp3 content from url"

        # Mock HEAD request
        responses.add(
            responses.HEAD,
            url,
            headers={
                "content-type": "audio/mpeg",
                "content-length": str(len(content)),
            },
        )

        # Mock GET request
        responses.add(responses.GET, url, body=content)

        stage = FetchingStage(output_dir=tmp_path)
        result = stage.process(url)

        assert result.source == url
        assert result.content_type == ContentType.AUDIO_MP3
        assert result.size_bytes == len(content)
        assert Path(result.local_path).read_bytes() == content

    @responses.activate
    @pytest.mark.description("FetchingStage infers content type from URL extension")
    def test_infers_content_type_from_extension(self, tmp_path: Path) -> None:
        """Should infer content type from URL extension when header missing."""
        url = "http://example.com/audio.mp3"
        content = b"fake mp3 content"

        responses.add(
            responses.HEAD,
            url,
            headers={
                "content-type": "application/octet-stream",  # Unknown MIME
                "content-length": str(len(content)),
            },
        )
        responses.add(responses.GET, url, body=content)

        stage = FetchingStage(output_dir=tmp_path)
        result = stage.process(url)

        assert result.content_type == ContentType.AUDIO_MP3

    @responses.activate
    @pytest.mark.description("FetchingStage handles HTTPS URLs")
    def test_fetch_https_url(self, tmp_path: Path) -> None:
        """Should fetch content from HTTPS URL."""
        url = "https://secure.example.com/audio.wav"
        content = b"secure wav content"

        responses.add(
            responses.HEAD,
            url,
            headers={
                "content-type": "audio/wav",
                "content-length": str(len(content)),
            },
        )
        responses.add(responses.GET, url, body=content)

        stage = FetchingStage(output_dir=tmp_path)
        result = stage.process(url)

        assert result.content_type == ContentType.AUDIO_WAV


class TestFetchingStageContentTypeDetection:
    """Tests for content type detection."""

    @pytest.mark.description("ContentType detects MP3 from MIME type")
    def test_content_type_from_mime_mp3(self) -> None:
        """Should detect MP3 from MIME type."""
        assert ContentType.from_mime("audio/mpeg") == ContentType.AUDIO_MP3
        assert ContentType.from_mime("audio/mpeg; charset=utf-8") == ContentType.AUDIO_MP3

    @pytest.mark.description("ContentType detects from file extension")
    def test_content_type_from_extension(self) -> None:
        """Should detect content type from file extension."""
        assert ContentType.from_extension(".mp3") == ContentType.AUDIO_MP3
        assert ContentType.from_extension(".wav") == ContentType.AUDIO_WAV
        assert ContentType.from_extension(".MP3") == ContentType.AUDIO_MP3  # Case insensitive
        assert ContentType.from_extension(".mp4") == ContentType.VIDEO_MP4

    @pytest.mark.description("ContentType returns UNKNOWN for unrecognized types")
    def test_content_type_unknown(self) -> None:
        """Should return UNKNOWN for unrecognized types."""
        assert ContentType.from_mime("application/weird") == ContentType.UNKNOWN
        assert ContentType.from_extension(".xyz") == ContentType.UNKNOWN

    @pytest.mark.description("ContentType is_audio and is_video work correctly")
    def test_content_type_is_media(self) -> None:
        """Should correctly identify audio and video types."""
        assert ContentType.AUDIO_MP3.is_audio()
        assert not ContentType.AUDIO_MP3.is_video()
        assert ContentType.AUDIO_MP3.is_media()

        assert ContentType.VIDEO_MP4.is_video()
        assert not ContentType.VIDEO_MP4.is_audio()
        assert ContentType.VIDEO_MP4.is_media()

        assert not ContentType.APPLICATION_RSS.is_media()

    @pytest.mark.description("FetchingStage detect_content_type for local file")
    def test_detect_content_type_local(self, tmp_path: Path) -> None:
        """Should detect content type of local file without reading."""
        mp3_file = tmp_path / "test.mp3"
        mp3_file.write_bytes(b"content")

        stage = FetchingStage(output_dir=tmp_path / "output")
        content_type = stage.detect_content_type(str(mp3_file))

        assert content_type == ContentType.AUDIO_MP3

    @pytest.mark.description("FetchingStage detect_content_type raises for unknown")
    def test_detect_content_type_unknown_raises(self, tmp_path: Path) -> None:
        """Should raise ContentTypeError for unknown type."""
        unknown_file = tmp_path / "data"
        unknown_file.write_bytes(b"content")

        stage = FetchingStage(output_dir=tmp_path / "output")

        with pytest.raises(ContentTypeError):
            stage.detect_content_type(str(unknown_file))


class TestFetchingStageYouTube:
    """Tests for YouTube URL detection."""

    @pytest.mark.description("FetchingStage detects YouTube URLs")
    def test_youtube_url_detection(self, tmp_path: Path) -> None:
        """Should detect various YouTube URL formats."""
        stage = FetchingStage(output_dir=tmp_path)

        youtube_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/shorts/dQw4w9WgXcQ",
        ]

        for url in youtube_urls:
            assert stage._is_youtube_url(url), f"Should detect: {url}"

    @pytest.mark.description("FetchingStage rejects non-YouTube URLs")
    def test_non_youtube_urls(self, tmp_path: Path) -> None:
        """Should not detect non-YouTube URLs as YouTube."""
        stage = FetchingStage(output_dir=tmp_path)

        non_youtube_urls = [
            "https://example.com/video.mp4",
            "https://vimeo.com/123456",
            "https://youtube.com/",  # No video ID
        ]

        for url in non_youtube_urls:
            assert not stage._is_youtube_url(url), f"Should not detect: {url}"

    @pytest.mark.description("FetchingStage extracts YouTube video ID")
    def test_extract_youtube_id(self, tmp_path: Path) -> None:
        """Should extract video ID from various YouTube URL formats."""
        stage = FetchingStage(output_dir=tmp_path)

        test_cases = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/shorts/abc123def45", "abc123def45"),
        ]

        for url, expected_id in test_cases:
            assert stage._extract_youtube_id(url) == expected_id

    @pytest.mark.description("FetchingStage raises when YouTube disabled")
    def test_youtube_disabled_raises_error(self, tmp_path: Path) -> None:
        """Should raise FetchError when YouTube is disabled."""
        stage = FetchingStage(output_dir=tmp_path, enable_youtube=False)

        with pytest.raises(FetchError, match="disabled"):
            stage.process("https://www.youtube.com/watch?v=dQw4w9WgXcQ")


class TestFetchingStageStreaming:
    """Tests for streaming functionality."""

    @pytest.mark.description("FetchingStage streams local file content")
    def test_stream_local_file(self, tmp_path: Path) -> None:
        """Should stream local file content in chunks."""
        # Create a test file
        test_file = tmp_path / "test.mp3"
        test_content = b"A" * 1000 + b"B" * 1000
        test_file.write_bytes(test_content)

        stage = FetchingStage(output_dir=tmp_path / "output")

        chunks = list(stage.stream_content(str(test_file)))
        combined = b"".join(chunks)

        assert combined == test_content

    @pytest.mark.description("FetchingStage stream raises for missing file")
    def test_stream_missing_file_raises(self, tmp_path: Path) -> None:
        """Should raise FetchError for missing file."""
        stage = FetchingStage(output_dir=tmp_path)

        with pytest.raises(FetchError, match="Failed to stream"):
            list(stage.stream_content("/nonexistent/file.mp3"))


class TestFetchingStageRSS:
    """Tests for RSS feed parsing."""

    @pytest.mark.description("FetchingStage parses RSS feed")
    def test_parse_rss_feed(self, tmp_path: Path) -> None:
        """Should parse RSS feed and extract media URLs."""
        # Create test RSS feed
        rss_content = """<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
            <channel>
                <title>Test Podcast</title>
                <item>
                    <title>Episode 1</title>
                    <enclosure url="http://example.com/ep1.mp3" type="audio/mpeg" />
                </item>
                <item>
                    <title>Episode 2</title>
                    <enclosure url="http://example.com/ep2.mp3" type="audio/mpeg" />
                </item>
            </channel>
        </rss>
        """

        rss_file = tmp_path / "source" / "feed.xml"
        rss_file.parent.mkdir()
        rss_file.write_text(rss_content)

        stage = FetchingStage(output_dir=tmp_path / "output")

        # Mock HTTP responses for the episode URLs
        with responses.RequestsMock() as rsps:
            for url in ["http://example.com/ep1.mp3", "http://example.com/ep2.mp3"]:
                rsps.add(
                    responses.HEAD,
                    url,
                    headers={"content-type": "audio/mpeg", "content-length": "100"},
                )
                rsps.add(responses.GET, url, body=b"audio content")

            results = stage.process_rss(str(rss_file))

        assert len(results) == 2
        assert all(r.content_type == ContentType.AUDIO_MP3 for r in results)


class TestFetchingStageCloudStorage:
    """Tests for cloud storage (S3/GCS) error handling."""

    @pytest.mark.description("FetchingStage raises StorageError for S3 without boto3")
    def test_s3_without_boto3(self, tmp_path: Path) -> None:
        """Should raise StorageError when boto3 is not installed."""
        stage = FetchingStage(output_dir=tmp_path)

        with patch.dict("sys.modules", {"boto3": None}):
            with pytest.raises((StorageError, FetchError, ImportError)):
                stage.process("s3://bucket/key.mp3")

    @pytest.mark.description("FetchingStage validates S3 URI format")
    def test_s3_invalid_uri(self, tmp_path: Path) -> None:
        """Should raise FetchError for invalid S3 URI."""
        stage = FetchingStage(output_dir=tmp_path)

        # Mock boto3 import
        mock_boto3 = MagicMock()
        with patch.dict("sys.modules", {"boto3": mock_boto3}):
            with pytest.raises(FetchError, match="Invalid S3 URI"):
                stage.process("s3:///no-bucket")

    @pytest.mark.description("FetchingStage validates GCS URI format")
    def test_gcs_invalid_uri(self, tmp_path: Path) -> None:
        """Should raise FetchError for invalid GCS URI."""
        stage = FetchingStage(output_dir=tmp_path)

        # Mock google.cloud.storage import
        mock_storage = MagicMock()
        mock_google = MagicMock()
        mock_google.cloud = MagicMock()
        mock_google.cloud.storage = mock_storage

        modules = {
            "google": mock_google,
            "google.cloud": mock_google.cloud,
            "google.cloud.storage": mock_storage,
        }
        with patch.dict("sys.modules", modules):
            with pytest.raises(FetchError, match="Invalid GCS URI"):
                stage.process("gs:///no-bucket")


class TestFetchResult:
    """Tests for FetchResult dataclass."""

    @pytest.mark.description("FetchResult is immutable")
    def test_fetch_result_immutable(self, tmp_path: Path) -> None:
        """FetchResult should be immutable."""
        result = FetchResult(
            source="test",
            local_path=str(tmp_path / "test.mp3"),
            content_type=ContentType.AUDIO_MP3,
            size_bytes=100,
            metadata={},
        )

        from dataclasses import FrozenInstanceError

        with pytest.raises(FrozenInstanceError):
            result.source = "changed"  # type: ignore

    @pytest.mark.description("FetchResult stores all fields correctly")
    def test_fetch_result_fields(self, tmp_path: Path) -> None:
        """FetchResult should store all provided fields."""
        local_path = str(tmp_path / "test.mp3")
        metadata = {"key": "value"}

        result = FetchResult(
            source="http://example.com/test.mp3",
            local_path=local_path,
            content_type=ContentType.AUDIO_MP3,
            size_bytes=12345,
            metadata=metadata,
        )

        assert result.source == "http://example.com/test.mp3"
        assert result.local_path == local_path
        assert result.content_type == ContentType.AUDIO_MP3
        assert result.size_bytes == 12345
        assert result.metadata == metadata
