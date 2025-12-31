# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""YouTube playlist source adapter for Voogle.

Provides three main operations:
- scan(): Get playlist metadata without downloading
- sync_media(): Download audio files with skip/retry logic
- emit_rss(): Generate RSS feed for Voogle ingestion

Uses yt-dlp for YouTube interaction. No cookies by default.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import format_datetime
from enum import Enum
from pathlib import Path

from yt_dlp import YoutubeDL


class DownloadStatus(Enum):
    """Status of a download attempt."""

    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class YouTubePlaylistError(Exception):
    """Raised when playlist operations fail."""


@dataclass
class PlannedEpisode:
    """Metadata about a YouTube video before downloading."""

    video_id: str
    title: str
    description: str
    duration_seconds: int | None
    upload_date: datetime | None
    playlist_title: str
    playlist_index: int | None
    expected_filename: str


@dataclass
class DownloadResult:
    """Result of attempting to download a single video."""

    video_id: str
    status: DownloadStatus
    filepath: Path | None
    error: str | None


def _parse_upload_date(date_str: str | None) -> datetime | None:
    """Parse yt-dlp upload_date format (YYYYMMDD) to datetime."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y%m%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _make_filename(title: str, video_id: str) -> str:
    """Generate expected filename for a video."""
    return f"{title} [{video_id}].mp3"


def scan(playlist_url: str) -> list[PlannedEpisode]:
    """Scan playlist and return metadata for all videos.

    Does NOT download anything. Uses yt-dlp extract_info with download=False.

    Args:
        playlist_url: YouTube playlist URL

    Returns:
        List of PlannedEpisode with metadata for each video

    Raises:
        YouTubePlaylistError: On network error, invalid URL, etc.
    """
    opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
        "skip_download": True,
        "ignoreerrors": True,
    }

    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(playlist_url, download=False)
    except Exception as e:
        raise YouTubePlaylistError(f"Failed to scan playlist: {e}") from e

    if info is None:
        raise YouTubePlaylistError("Failed to extract playlist info")

    playlist_title = info.get("title", "Unknown Playlist")
    entries = info.get("entries", [])

    episodes = []
    for entry in entries:
        if entry is None:
            continue

        video_id = entry.get("id")
        title = entry.get("title")

        if not video_id or not title:
            continue

        episodes.append(
            PlannedEpisode(
                video_id=video_id,
                title=title,
                description=entry.get("description", "") or "",
                duration_seconds=entry.get("duration"),
                upload_date=_parse_upload_date(entry.get("upload_date")),
                playlist_title=playlist_title,
                playlist_index=entry.get("playlist_index"),
                expected_filename=_make_filename(title, video_id),
            )
        )

    print(f"Scanned: {playlist_title} ({len(episodes)} videos)")
    return episodes


def sync_media(
    episodes: list[PlannedEpisode],
    output_dir: Path,
    on_progress: Callable[[str, DownloadStatus, int, int], None] | None = None,
) -> list[DownloadResult]:
    """Download audio files for episodes that don't exist yet.

    - Skips files that already exist in output_dir
    - Two-pass strategy: web client first, android fallback on failure
    - Extracts audio to MP3 using FFmpeg postprocessor
    - Failed downloads don't stop the process

    Args:
        episodes: List of PlannedEpisode to download
        output_dir: Root directory for downloads (playlist subfolder created)
        on_progress: Optional callback (video_id, status, current, total)

    Returns:
        List of DownloadResult (one per input episode)
    """
    if not episodes:
        return []

    results: list[DownloadResult] = []
    total = len(episodes)

    # Group by playlist for output organization
    playlist_title = episodes[0].playlist_title
    playlist_dir = output_dir / playlist_title
    playlist_dir.mkdir(parents=True, exist_ok=True)

    for i, episode in enumerate(episodes, 1):
        expected_path = playlist_dir / episode.expected_filename

        # Check if file already exists
        if expected_path.exists():
            result = DownloadResult(
                video_id=episode.video_id,
                status=DownloadStatus.SKIPPED,
                filepath=expected_path,
                error=None,
            )
            results.append(result)
            if on_progress:
                on_progress(episode.video_id, DownloadStatus.SKIPPED, i, total)
            print(f"  Skipped: {episode.expected_filename} (exists)")
            continue

        # Try to download
        result = _download_video(episode, playlist_dir)
        results.append(result)

        if on_progress:
            on_progress(episode.video_id, result.status, i, total)

        if result.status == DownloadStatus.SUCCESS:
            print(f"  Downloaded: {episode.expected_filename}")
        else:
            print(f"  Failed: {episode.expected_filename} - {result.error}")

    return results


def _download_video(episode: PlannedEpisode, output_dir: Path) -> DownloadResult:
    """Download a single video with two-pass strategy."""
    video_url = f"https://www.youtube.com/watch?v={episode.video_id}"
    expected_path = output_dir / episode.expected_filename

    # Common options
    base_opts = {
        "format": (
            "18/"
            "ba[ext=m4a][protocol!=m3u8]/"
            "best[ext=mp4][vcodec!=none][acodec!=none][height<=360]/"
            "bestaudio[protocol!=m3u8]"
        ),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "0",
            }
        ],
        "outtmpl": str(output_dir / f"{episode.title} [{episode.video_id}].%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": False,
        "retries": 3,
    }

    # Pass 1: Web client
    web_opts = {
        **base_opts,
        "extractor_args": {"youtube": {"player_client": ["web"]}},
    }

    try:
        with YoutubeDL(web_opts) as ydl:
            ydl.download([video_url])

        if expected_path.exists():
            return DownloadResult(
                video_id=episode.video_id,
                status=DownloadStatus.SUCCESS,
                filepath=expected_path,
                error=None,
            )
    except Exception as web_error:
        # Pass 2: Android fallback
        android_opts = {
            **base_opts,
            "extractor_args": {"youtube": {"player_client": ["android"]}},
        }

        try:
            with YoutubeDL(android_opts) as ydl:
                ydl.download([video_url])

            if expected_path.exists():
                return DownloadResult(
                    video_id=episode.video_id,
                    status=DownloadStatus.SUCCESS,
                    filepath=expected_path,
                    error=None,
                )
        except Exception as android_error:
            return DownloadResult(
                video_id=episode.video_id,
                status=DownloadStatus.FAILED,
                filepath=None,
                error=f"Web: {web_error}, Android: {android_error}",
            )

    # File didn't appear after download
    return DownloadResult(
        video_id=episode.video_id,
        status=DownloadStatus.FAILED,
        filepath=None,
        error="Download completed but file not found",
    )


def emit_rss(
    episodes: list[PlannedEpisode],
    output_dir: Path,
    feed_path: Path,
    base_url: str = "",
) -> Path:
    """Generate RSS feed XML for successfully downloaded episodes.

    Only includes episodes where MP3 file exists in output_dir.

    Args:
        episodes: List of PlannedEpisode
        output_dir: Directory containing downloaded files
        feed_path: Where to write the RSS XML file
        base_url: Base URL for enclosure URLs (e.g., "http://localhost:8080/local")

    Returns:
        Path to generated feed.xml
    """
    # Determine playlist title
    playlist_title = episodes[0].playlist_title if episodes else "YouTube Playlist"
    playlist_dir = output_dir / playlist_title if episodes else output_dir

    # Create RSS structure
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = playlist_title
    ET.SubElement(channel, "description").text = f"Episodes from {playlist_title}"
    ET.SubElement(channel, "link").text = base_url or "https://youtube.com"

    # Add items for episodes with existing files
    for episode in episodes:
        file_path = playlist_dir / episode.expected_filename
        if not file_path.exists():
            continue

        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = episode.title
        ET.SubElement(item, "description").text = episode.description
        ET.SubElement(item, "guid").text = episode.video_id

        if episode.upload_date:
            ET.SubElement(item, "pubDate").text = format_datetime(episode.upload_date)

        # Enclosure URL
        if base_url:
            enclosure_url = f"{base_url}/{playlist_title}/{episode.expected_filename}"
        else:
            enclosure_url = f"{playlist_title}/{episode.expected_filename}"

        file_size = file_path.stat().st_size
        ET.SubElement(
            item,
            "enclosure",
            url=enclosure_url,
            type="audio/mpeg",
            length=str(file_size),
        )

    # Write XML file
    tree = ET.ElementTree(rss)
    feed_path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(feed_path, encoding="unicode", xml_declaration=True)

    return feed_path
