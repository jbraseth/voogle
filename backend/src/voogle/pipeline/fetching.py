# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Source fetching stage for the media processing pipeline.

This stage supports fetching content from multiple source types:
- HTTP/HTTPS URLs
- Local filesystem paths
- S3 cloud storage (s3://)
- Google Cloud Storage (gs://)
- YouTube videos (via yt-dlp)
- RSS feeds

The stage implements streaming for large files to avoid memory issues.
"""

from __future__ import annotations

import logging
import mimetypes
import re
import shutil
import subprocess
import tempfile
from collections.abc import Iterator
from pathlib import Path
from urllib.parse import urlparse

import requests
import xmltodict

from voogle.pipeline import (
    ContentType,
    ContentTypeError,
    FetchError,
    FetchResult,
    StorageError,
)

logger = logging.getLogger(__name__)

# Streaming chunk size (1MB)
STREAM_CHUNK_SIZE = 1024 * 1024

# Large file threshold (100MB) - files larger than this use streaming
LARGE_FILE_THRESHOLD = 100 * 1024 * 1024

# YouTube URL patterns
YOUTUBE_PATTERNS = [
    r"^https?://(www\.)?youtube\.com/watch\?v=[\w-]+",
    r"^https?://(www\.)?youtu\.be/[\w-]+",
    r"^https?://(www\.)?youtube\.com/shorts/[\w-]+",
]


class FetchingStage:
    """Stage for fetching content from various sources.

    Supports:
    - HTTP/HTTPS URLs with streaming for large files
    - Local file reading
    - S3 bucket access (requires boto3)
    - GCS bucket access (requires google-cloud-storage)
    - YouTube download via yt-dlp
    - RSS feed parsing

    Example:
        stage = FetchingStage(output_dir=Path("/tmp/fetched"))
        result = stage.process("https://example.com/audio.mp3")
        print(result.local_path)  # /tmp/fetched/audio.mp3
    """

    def __init__(
        self,
        output_dir: Path | None = None,
        enable_youtube: bool = True,
        youtube_format: str = "bestaudio[ext=m4a]/bestaudio/best",
        cookies_file: Path | None = None,
    ) -> None:
        """Initialize the fetching stage.

        Args:
            output_dir: Directory to store fetched content.
                        If None, uses a temporary directory.
            enable_youtube: Whether to enable YouTube downloads.
            youtube_format: yt-dlp format string for YouTube downloads.
            cookies_file: Path to cookies.txt for authenticated downloads.
        """
        self._output_dir = output_dir or Path(tempfile.mkdtemp(prefix="voogle-fetch-"))
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._enable_youtube = enable_youtube
        self._youtube_format = youtube_format
        self._cookies_file = cookies_file

        logger.info(f"FetchingStage initialized with output_dir={self._output_dir}")

    @property
    def output_dir(self) -> Path:
        """Return the output directory for fetched content."""
        return self._output_dir

    def process(self, source: str) -> FetchResult:
        """Fetch content from the given source.

        Args:
            source: Source URL or path to fetch from.
                   Supported schemes: http://, https://, file://,
                   s3://, gs://, or local path

        Returns:
            FetchResult with local path and metadata

        Raises:
            FetchError: If fetching fails
            ContentTypeError: If content type cannot be determined
        """
        if not source:
            raise FetchError("Source cannot be empty")

        logger.info(f"Fetching: {source}")

        # Determine source type and dispatch
        if self._is_youtube_url(source):
            return self._fetch_youtube(source)
        elif source.startswith("s3://"):
            return self._fetch_s3(source)
        elif source.startswith("gs://"):
            return self._fetch_gcs(source)
        elif source.startswith(("http://", "https://")):
            return self._fetch_url(source)
        elif source.startswith("file://"):
            return self._fetch_local(source[7:])  # Strip file:// prefix
        else:
            # Treat as local path
            return self._fetch_local(source)

    def process_rss(self, source: str) -> list[FetchResult]:
        """Parse RSS feed and return list of media items.

        Args:
            source: URL or path to RSS feed

        Returns:
            List of FetchResult objects for each media item in feed

        Raises:
            FetchError: If feed parsing fails
        """
        logger.info(f"Parsing RSS feed: {source}")

        # First fetch the RSS feed itself
        feed_result = self.process(source)

        try:
            with open(feed_result.local_path, encoding="utf-8") as f:
                feed_content = f.read()

            parsed = xmltodict.parse(feed_content)

            # Handle RSS 2.0 format
            channel = parsed.get("rss", {}).get("channel", {})
            items = channel.get("item", [])

            if isinstance(items, dict):
                items = [items]

            results: list[FetchResult] = []
            for item in items:
                enclosure = item.get("enclosure", {})
                if isinstance(enclosure, dict):
                    url = enclosure.get("@url")
                    if url:
                        try:
                            result = self.process(url)
                            results.append(result)
                        except FetchError as e:
                            logger.warning(f"Failed to fetch RSS item {url}: {e}")
                            continue

            logger.info(f"Parsed {len(results)} items from RSS feed")
            return results

        except Exception as e:
            raise FetchError(f"Failed to parse RSS feed: {e}") from e

    def _is_youtube_url(self, url: str) -> bool:
        """Check if URL is a YouTube video URL."""
        for pattern in YOUTUBE_PATTERNS:
            if re.match(pattern, url):
                return True
        return False

    def _fetch_url(self, url: str) -> FetchResult:
        """Fetch content from HTTP/HTTPS URL with streaming support."""
        try:
            # First, get headers to determine content type and size
            response = requests.head(url, allow_redirects=True, timeout=30)
            response.raise_for_status()

            content_length = int(response.headers.get("content-length", 0))
            content_type_header = response.headers.get("content-type", "")
            content_type = ContentType.from_mime(content_type_header)

            # If content type unknown, try to infer from URL extension
            if content_type == ContentType.UNKNOWN:
                parsed = urlparse(url)
                ext = Path(parsed.path).suffix
                if ext:
                    content_type = ContentType.from_extension(ext)

            # Determine output filename
            parsed = urlparse(url)
            filename = Path(parsed.path).name or "downloaded_content"
            if not Path(filename).suffix:
                # Add extension based on content type
                ext_map = {
                    ContentType.AUDIO_MP3: ".mp3",
                    ContentType.AUDIO_WAV: ".wav",
                    ContentType.AUDIO_OGG: ".ogg",
                    ContentType.AUDIO_M4A: ".m4a",
                    ContentType.VIDEO_MP4: ".mp4",
                    ContentType.VIDEO_WEBM: ".webm",
                }
                ext = ext_map.get(content_type, "")
                filename = f"{filename}{ext}"

            output_path = self._output_dir / filename

            # Use streaming for large files
            if content_length > LARGE_FILE_THRESHOLD:
                logger.info(f"Streaming large file: {content_length} bytes")
                self._stream_download(url, output_path)
            else:
                self._direct_download(url, output_path)

            actual_size = output_path.stat().st_size

            return FetchResult(
                source=url,
                local_path=str(output_path),
                content_type=content_type,
                size_bytes=actual_size,
                metadata={
                    "original_content_type": content_type_header,
                    "original_content_length": content_length,
                },
            )

        except requests.RequestException as e:
            raise FetchError(f"Failed to fetch URL {url}: {e}") from e

    def _stream_download(self, url: str, output_path: Path) -> None:
        """Stream download large file in chunks."""
        with requests.get(url, stream=True, timeout=300) as response:
            response.raise_for_status()
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=STREAM_CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)

    def _direct_download(self, url: str, output_path: Path) -> None:
        """Download file directly into memory then write."""
        response = requests.get(url, timeout=120)
        response.raise_for_status()
        with open(output_path, "wb") as f:
            f.write(response.content)

    def _fetch_local(self, path: str) -> FetchResult:
        """Fetch content from local filesystem."""
        source_path = Path(path)

        if not source_path.exists():
            raise FetchError(f"Local file not found: {path}")

        if not source_path.is_file():
            raise FetchError(f"Path is not a file: {path}")

        # Detect content type from extension first (more reliable), then MIME type
        content_type = ContentType.from_extension(source_path.suffix)
        if content_type == ContentType.UNKNOWN:
            mime_type, _ = mimetypes.guess_type(str(source_path))
            if mime_type:
                content_type = ContentType.from_mime(mime_type)

        # Copy to output directory if not already there
        output_path = self._output_dir / source_path.name
        if source_path.resolve() != output_path.resolve():
            shutil.copy2(source_path, output_path)
        else:
            output_path = source_path

        return FetchResult(
            source=path,
            local_path=str(output_path),
            content_type=content_type,
            size_bytes=output_path.stat().st_size,
            metadata={"original_path": str(source_path.absolute())},
        )

    def _fetch_s3(self, uri: str) -> FetchResult:
        """Fetch content from S3 bucket."""
        try:
            import boto3
        except ImportError as e:
            raise StorageError("boto3 is required for S3 support: pip install boto3") from e

        # Parse s3://bucket/key format
        parsed = urlparse(uri)
        bucket = parsed.netloc
        key = parsed.path.lstrip("/")

        if not bucket or not key:
            raise FetchError(f"Invalid S3 URI format: {uri}")

        logger.info(f"Fetching from S3: bucket={bucket}, key={key}")

        try:
            s3 = boto3.client("s3")

            # Get object metadata
            head = s3.head_object(Bucket=bucket, Key=key)
            content_length = head.get("ContentLength", 0)
            content_type_header = head.get("ContentType", "")
            content_type = ContentType.from_mime(content_type_header)

            # Determine output filename
            filename = Path(key).name
            output_path = self._output_dir / filename

            # Download with streaming for large files
            if content_length > LARGE_FILE_THRESHOLD:
                logger.info(f"Streaming large S3 object: {content_length} bytes")
                s3.download_file(bucket, key, str(output_path))
            else:
                response = s3.get_object(Bucket=bucket, Key=key)
                with open(output_path, "wb") as f:
                    f.write(response["Body"].read())

            return FetchResult(
                source=uri,
                local_path=str(output_path),
                content_type=content_type,
                size_bytes=output_path.stat().st_size,
                metadata={
                    "bucket": bucket,
                    "key": key,
                    "etag": head.get("ETag", ""),
                    "last_modified": str(head.get("LastModified", "")),
                },
            )

        except Exception as e:
            raise FetchError(f"Failed to fetch from S3 {uri}: {e}") from e

    def _fetch_gcs(self, uri: str) -> FetchResult:
        """Fetch content from Google Cloud Storage."""
        try:
            from google.cloud import storage
        except ImportError as e:
            raise StorageError(
                "google-cloud-storage is required for GCS support: "
                "pip install google-cloud-storage"
            ) from e

        # Parse gs://bucket/path format
        parsed = urlparse(uri)
        bucket_name = parsed.netloc
        blob_path = parsed.path.lstrip("/")

        if not bucket_name or not blob_path:
            raise FetchError(f"Invalid GCS URI format: {uri}")

        logger.info(f"Fetching from GCS: bucket={bucket_name}, path={blob_path}")

        try:
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_path)

            # Get metadata
            blob.reload()
            content_type_header = blob.content_type or ""
            content_type = ContentType.from_mime(content_type_header)

            # Determine output filename
            filename = Path(blob_path).name
            output_path = self._output_dir / filename

            # Download
            blob.download_to_filename(str(output_path))

            return FetchResult(
                source=uri,
                local_path=str(output_path),
                content_type=content_type,
                size_bytes=output_path.stat().st_size,
                metadata={
                    "bucket": bucket_name,
                    "path": blob_path,
                    "generation": str(blob.generation),
                    "updated": str(blob.updated),
                },
            )

        except Exception as e:
            raise FetchError(f"Failed to fetch from GCS {uri}: {e}") from e

    def _fetch_youtube(self, url: str) -> FetchResult:
        """Fetch audio from YouTube video using yt-dlp."""
        if not self._enable_youtube:
            raise FetchError("YouTube downloads are disabled")

        # Check if yt-dlp is available
        if not shutil.which("yt-dlp"):
            raise FetchError("yt-dlp is required for YouTube downloads: pip install yt-dlp")

        logger.info(f"Downloading from YouTube: {url}")

        try:
            # Extract video ID for filename
            video_id = self._extract_youtube_id(url)
            output_template = str(self._output_dir / f"{video_id}.%(ext)s")

            cmd = [
                "yt-dlp",
                "-f",
                self._youtube_format,
                "-o",
                output_template,
                "--no-playlist",
                "--print",
                "filename",
            ]

            if self._cookies_file and self._cookies_file.exists():
                cmd.extend(["--cookies", str(self._cookies_file)])

            cmd.append(url)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
            )

            if result.returncode != 0:
                raise FetchError(f"yt-dlp failed: {result.stderr}")

            # Get the output filename from yt-dlp
            output_file = result.stdout.strip().split("\n")[-1]
            output_path = Path(output_file)

            if not output_path.exists():
                raise FetchError(f"Downloaded file not found: {output_path}")

            # Detect content type
            content_type = ContentType.from_extension(output_path.suffix)

            return FetchResult(
                source=url,
                local_path=str(output_path),
                content_type=content_type,
                size_bytes=output_path.stat().st_size,
                metadata={
                    "video_id": video_id,
                    "format": self._youtube_format,
                },
            )

        except subprocess.TimeoutExpired as e:
            raise FetchError(f"YouTube download timed out: {url}") from e
        except subprocess.SubprocessError as e:
            raise FetchError(f"YouTube download failed: {e}") from e

    def _extract_youtube_id(self, url: str) -> str:
        """Extract video ID from YouTube URL."""
        patterns = [
            r"v=([a-zA-Z0-9_-]{11})",
            r"youtu\.be/([a-zA-Z0-9_-]{11})",
            r"shorts/([a-zA-Z0-9_-]{11})",
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        # Fallback: use hash of URL
        import hashlib

        return hashlib.md5(url.encode()).hexdigest()[:11]

    def stream_content(self, source: str) -> Iterator[bytes]:
        """Stream content from source in chunks.

        Useful for processing large files without loading into memory.

        Args:
            source: Source URL or path

        Yields:
            Chunks of content bytes

        Raises:
            FetchError: If streaming fails
        """
        if source.startswith(("http://", "https://")):
            try:
                with requests.get(source, stream=True, timeout=300) as response:
                    response.raise_for_status()
                    for chunk in response.iter_content(chunk_size=STREAM_CHUNK_SIZE):
                        if chunk:
                            yield chunk
            except requests.RequestException as e:
                raise FetchError(f"Failed to stream URL {source}: {e}") from e
        else:
            # Local file streaming
            path = source[7:] if source.startswith("file://") else source
            try:
                with open(path, "rb") as f:
                    while chunk := f.read(STREAM_CHUNK_SIZE):
                        yield chunk
            except OSError as e:
                raise FetchError(f"Failed to stream file {path}: {e}") from e

    def detect_content_type(self, source: str) -> ContentType:
        """Detect content type without downloading full content.

        Args:
            source: Source URL or path

        Returns:
            Detected ContentType

        Raises:
            ContentTypeError: If type cannot be determined
        """
        if source.startswith(("http://", "https://")):
            try:
                response = requests.head(source, allow_redirects=True, timeout=30)
                content_type_header = response.headers.get("content-type", "")
                content_type = ContentType.from_mime(content_type_header)
                if content_type != ContentType.UNKNOWN:
                    return content_type
            except requests.RequestException:
                pass

            # Try extension
            parsed = urlparse(source)
            ext = Path(parsed.path).suffix
            if ext:
                return ContentType.from_extension(ext)

            raise ContentTypeError(f"Cannot determine content type for URL: {source}")

        else:
            # Local file
            path = source[7:] if source.startswith("file://") else source
            source_path = Path(path)

            # Try MIME type
            mime_type, _ = mimetypes.guess_type(str(source_path))
            if mime_type:
                return ContentType.from_mime(mime_type)

            # Try extension
            if source_path.suffix:
                return ContentType.from_extension(source_path.suffix)

            raise ContentTypeError(f"Cannot determine content type for file: {path}")

    def __repr__(self) -> str:
        """Return string representation."""
        return f"FetchingStage(output_dir={self._output_dir}, youtube={self._enable_youtube})"

    def __str__(self) -> str:
        """Return human-readable string."""
        return f"<FetchingStage: output={self._output_dir}>"
