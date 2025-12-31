# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""BibleProject Classroom source adapter for Voogle.

Detects compound sessions containing multiple Mux playback IDs
(main video + slides video) plus PDF teacher notes. Generates RSS feeds
that emit separate items for each artifact so Voogle can index them
independently.
"""

from __future__ import annotations

import json
import logging
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from email.utils import format_datetime
from enum import Enum
from pathlib import Path

from voogle.sources import ConfigurationError, FeedGenerationError, LocalFeed

logger = logging.getLogger(__name__)


class ArtifactType(Enum):
    """Type of learning artifact in a session."""

    MAIN_VIDEO = "main"
    SLIDES_VIDEO = "slides"
    TEACHER_NOTES = "pdf"


@dataclass(frozen=True)
class SessionArtifact:
    """A single artifact within a compound session."""

    artifact_type: ArtifactType
    url: str  # Mux stream URL or PDF URL
    mux_playback_id: str | None  # Only for video artifacts
    title_suffix: str  # "Main Video", "Slides", "Teacher Notes"
    mime_type: str  # "video/mp4", "application/pdf"

    @property
    def is_video(self) -> bool:
        return self.artifact_type in (ArtifactType.MAIN_VIDEO, ArtifactType.SLIDES_VIDEO)


@dataclass
class CompoundSession:
    """A session page that may contain multiple artifacts."""

    session_id: str
    session_title: str
    session_url: str
    course_title: str
    course_slug: str
    description: str
    artifacts: list[SessionArtifact]
    published_at: datetime | None = None

    @property
    def main_video(self) -> SessionArtifact | None:
        return next(
            (a for a in self.artifacts if a.artifact_type == ArtifactType.MAIN_VIDEO),
            None,
        )

    @property
    def slides_video(self) -> SessionArtifact | None:
        return next(
            (a for a in self.artifacts if a.artifact_type == ArtifactType.SLIDES_VIDEO),
            None,
        )

    @property
    def teacher_notes(self) -> SessionArtifact | None:
        return next(
            (a for a in self.artifacts if a.artifact_type == ArtifactType.TEACHER_NOTES),
            None,
        )


# Regex patterns for Mux playback ID extraction
# Pattern 1: mux-player custom element with playback-id attribute
MUX_PLAYER_PATTERN = re.compile(
    r'<mux-player[^>]*\bplayback-id=["\']([a-zA-Z0-9]+)["\']', re.IGNORECASE
)

# Pattern 2: data attribute on container elements
DATA_ATTR_PATTERN = re.compile(
    r'data-(?:mux-)?playback-id=["\']([a-zA-Z0-9]+)["\']', re.IGNORECASE
)

# Pattern 3: JavaScript config object patterns
JS_CONFIG_PATTERN = re.compile(
    r'playback[_-]?[Ii]d["\']?\s*[:=]\s*["\']([a-zA-Z0-9]+)["\']'
)

# Pattern for PDF URLs
PDF_URL_PATTERN = re.compile(
    r'href=["\']([^"\']*\.pdf)["\']', re.IGNORECASE
)


def extract_mux_playback_ids(html: str) -> list[str]:
    """Extract all Mux playback IDs from session page HTML.

    Mux players are typically embedded with playback IDs in:
    - mux-player custom element with playback-id attribute
    - data-playback-id or data-mux-playback-id attributes
    - JavaScript configuration objects

    Returns list of playback IDs in order of appearance (deduplicated).
    """
    ids: list[str] = []
    seen: set[str] = set()

    # Try each pattern and collect unique IDs in order
    for pattern in [MUX_PLAYER_PATTERN, DATA_ATTR_PATTERN, JS_CONFIG_PATTERN]:
        for match in pattern.finditer(html):
            playback_id = match.group(1)
            if playback_id not in seen:
                ids.append(playback_id)
                seen.add(playback_id)

    return ids


def extract_pdf_url(html: str) -> str | None:
    """Extract teacher notes PDF URL from session page HTML.

    Look for download links with .pdf extension.
    Returns the first PDF URL found, or None if not found.
    """
    match = PDF_URL_PATTERN.search(html)
    if match:
        return match.group(1)
    return None


def mux_stream_url(playback_id: str) -> str:
    """Convert Mux playback ID to HLS stream URL.

    Returns URL in format: https://stream.mux.com/{playback_id}.m3u8
    """
    return f"https://stream.mux.com/{playback_id}.m3u8"


def parse_session(
    html: str,
    session_url: str,
    session_id: str,
    session_title: str,
    course_title: str,
    course_slug: str,
    description: str = "",
    published_at: datetime | None = None,
) -> CompoundSession:
    """Parse a session page into a CompoundSession with all artifacts.

    Args:
        html: Raw HTML of the session page
        session_url: URL of the session page
        session_id: Unique identifier for the session
        session_title: Title of the session
        course_title: Title of the parent course
        course_slug: URL-friendly slug for the course
        description: Session description text
        published_at: Optional publication date

    Returns:
        CompoundSession with all detected artifacts

    Raises:
        ValueError: If no main video found (required)
    """
    artifacts: list[SessionArtifact] = []

    # Extract Mux playback IDs
    playback_ids = extract_mux_playback_ids(html)

    if not playback_ids:
        raise ValueError(f"No Mux playback IDs found in session: {session_url}")

    # First playback ID is the main video
    main_id = playback_ids[0]
    artifacts.append(
        SessionArtifact(
            artifact_type=ArtifactType.MAIN_VIDEO,
            url=mux_stream_url(main_id),
            mux_playback_id=main_id,
            title_suffix="Main Video",
            mime_type="video/mp4",
        )
    )

    # Second playback ID (if present) is the slides video
    if len(playback_ids) >= 2:
        slides_id = playback_ids[1]
        artifacts.append(
            SessionArtifact(
                artifact_type=ArtifactType.SLIDES_VIDEO,
                url=mux_stream_url(slides_id),
                mux_playback_id=slides_id,
                title_suffix="Slides",
                mime_type="video/mp4",
            )
        )

    # Extract PDF URL if present
    pdf_url = extract_pdf_url(html)
    if pdf_url:
        artifacts.append(
            SessionArtifact(
                artifact_type=ArtifactType.TEACHER_NOTES,
                url=pdf_url,
                mux_playback_id=None,
                title_suffix="Teacher Notes",
                mime_type="application/pdf",
            )
        )

    return CompoundSession(
        session_id=session_id,
        session_title=session_title,
        session_url=session_url,
        course_title=course_title,
        course_slug=course_slug,
        description=description,
        artifacts=artifacts,
        published_at=published_at,
    )


def emit_rss(
    sessions: list[CompoundSession],
    output_path: Path,
    channel_title: str | None = None,
    channel_link: str | None = None,
) -> Path:
    """Generate RSS feed XML with separate items for each artifact.

    Each artifact in each session becomes a separate RSS item with:
    - Clear title: "{Session Title} - {Artifact Suffix}"
    - Unique GUID: "bibleproject:{course_slug}:{session_id}:{artifact_type}"
    - Correct MIME type in enclosure

    Args:
        sessions: List of CompoundSession objects
        output_path: Where to write the RSS XML file
        channel_title: Optional channel title (defaults to course title)
        channel_link: Optional channel link URL

    Returns:
        Path to generated feed.xml
    """
    if not sessions:
        # Create empty but valid RSS
        rss = ET.Element("rss", version="2.0")
        channel = ET.SubElement(rss, "channel")
        ET.SubElement(channel, "title").text = channel_title or "BibleProject Classroom"
        ET.SubElement(channel, "description").text = "BibleProject Classroom content"
        ET.SubElement(channel, "link").text = channel_link or "https://classroom.bibleproject.com"

        tree = ET.ElementTree(rss)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        tree.write(output_path, encoding="unicode", xml_declaration=True)
        return output_path

    # Use first session's course info for channel metadata
    first_session = sessions[0]
    title = channel_title or f"BibleProject Classroom: {first_session.course_title}"
    link = channel_link or first_session.session_url

    # Create RSS structure
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = title
    ET.SubElement(channel, "description").text = f"Content from {first_session.course_title}"
    ET.SubElement(channel, "link").text = link
    ET.SubElement(channel, "language").text = "en"

    # Add items for each artifact in each session
    for session in sessions:
        for artifact in session.artifacts:
            item = ET.SubElement(channel, "item")

            # Title: "Session Title - Artifact Suffix"
            item_title = f"{session.session_title} - {artifact.title_suffix}"
            ET.SubElement(item, "title").text = item_title

            # Description based on artifact type
            if artifact.artifact_type == ArtifactType.MAIN_VIDEO:
                if session.description:
                    desc = f"Primary lesson content: {session.description}"
                else:
                    desc = f"Primary lesson content for {session.session_title}"
            elif artifact.artifact_type == ArtifactType.SLIDES_VIDEO:
                desc = f"Presentation slides for {session.session_title}"
            else:
                desc = f"Downloadable PDF notes for {session.session_title}"
            ET.SubElement(item, "description").text = desc

            # GUID: bibleproject:{course_slug}:{session_id}:{artifact_type}
            guid = f"bibleproject:{session.course_slug}:{session.session_id}:{artifact.artifact_type.value}"
            ET.SubElement(item, "guid", isPermaLink="false").text = guid

            # Publication date
            if session.published_at:
                ET.SubElement(item, "pubDate").text = format_datetime(session.published_at)

            # Enclosure with correct MIME type
            ET.SubElement(
                item,
                "enclosure",
                url=artifact.url,
                type=artifact.mime_type,
                length="0",  # Length unknown for streams
            )

    # Write XML file
    tree = ET.ElementTree(rss)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(output_path, encoding="unicode", xml_declaration=True)

    return output_path


class BibleProjectAdapter:
    """Adapter for BibleProject Classroom content.

    Reads course configurations from data/local/bibleproject/
    Generates RSS feeds to data/generated-feeds/bibleproject/

    Configuration format (data/local/bibleproject/course-name.json):
    {
        "course_slug": "how-to-read",
        "course_title": "How to Read the Bible",
        "course_url": "https://classroom.bibleproject.com/courses/how-to-read",
        "sessions": [
            {
                "session_id": "s1",
                "session_title": "Session 1: Introduction",
                "session_url": "https://classroom.bibleproject.com/courses/.../s1",
                "description": "Learn the basics...",
                "mux_ids": ["abc123main", "def456slides"],
                "pdf_url": "https://classroom.bibleproject.com/downloads/s1-notes.pdf"
            }
        ]
    }
    """

    def __init__(self, config_dir: Path, output_dir: Path) -> None:
        self._config_dir = config_dir
        self._output_dir = output_dir

    @property
    def adapter_id(self) -> str:
        return "bibleproject"

    @property
    def config_dir(self) -> Path:
        return self._config_dir

    @property
    def output_dir(self) -> Path:
        return self._output_dir

    def generate_feeds(self) -> list[LocalFeed]:
        """Generate RSS feeds from BibleProject course configs.

        Returns:
            List of LocalFeed objects for each generated feed

        Raises:
            ConfigurationError: If config is invalid
            FeedGenerationError: If feed generation fails
        """
        feeds: list[LocalFeed] = []

        if not self._config_dir.exists():
            logger.info(f"Config directory does not exist: {self._config_dir}")
            return feeds

        config_files = list(self._config_dir.glob("*.json"))
        if not config_files:
            logger.info(f"No config files found in {self._config_dir}")
            return feeds

        self._output_dir.mkdir(parents=True, exist_ok=True)

        for config_file in config_files:
            try:
                feed = self._generate_single_feed(config_file)
                feeds.append(feed)
                logger.info(f"Generated feed: {feed.channel_url}")
            except Exception as e:
                raise FeedGenerationError(
                    f"Failed to generate feed from {config_file.name}: {e}"
                ) from e

        return feeds

    def _generate_single_feed(self, config_file: Path) -> LocalFeed:
        """Generate RSS feed from a single config file."""
        # Read config
        try:
            with open(config_file, encoding="utf-8") as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in {config_file}: {e}") from e

        # Validate required fields
        self._validate_config(config, config_file.name)

        course_slug = config["course_slug"]
        course_title = config["course_title"]
        course_url = config.get("course_url", f"https://classroom.bibleproject.com/courses/{course_slug}")

        # Build sessions from config
        sessions: list[CompoundSession] = []
        for session_config in config.get("sessions", []):
            session = self._build_session_from_config(
                session_config, course_title, course_slug
            )
            sessions.append(session)

        # Generate RSS
        feed_filename = f"{config_file.stem}.xml"
        feed_path = self._output_dir / feed_filename

        emit_rss(
            sessions,
            feed_path,
            channel_title=f"BibleProject Classroom: {course_title}",
            channel_link=course_url,
        )

        # Return LocalFeed reference
        channel_url = f"local://bibleproject/{course_slug}"
        return LocalFeed(
            path=feed_path.absolute(),
            source_id=self.adapter_id,
            channel_url=channel_url,
        )

    def _validate_config(self, config: dict, filename: str) -> None:
        """Validate config has required fields."""
        required = ["course_slug", "course_title"]
        missing = [f for f in required if f not in config]
        if missing:
            raise ConfigurationError(
                f"Config {filename} missing required fields: {missing}"
            )

    def _build_session_from_config(
        self, session_config: dict, course_title: str, course_slug: str
    ) -> CompoundSession:
        """Build a CompoundSession from config dict."""
        artifacts: list[SessionArtifact] = []

        mux_ids = session_config.get("mux_ids", [])
        if mux_ids:
            # First ID is main video
            artifacts.append(
                SessionArtifact(
                    artifact_type=ArtifactType.MAIN_VIDEO,
                    url=mux_stream_url(mux_ids[0]),
                    mux_playback_id=mux_ids[0],
                    title_suffix="Main Video",
                    mime_type="video/mp4",
                )
            )

            # Second ID (if present) is slides
            if len(mux_ids) >= 2:
                artifacts.append(
                    SessionArtifact(
                        artifact_type=ArtifactType.SLIDES_VIDEO,
                        url=mux_stream_url(mux_ids[1]),
                        mux_playback_id=mux_ids[1],
                        title_suffix="Slides",
                        mime_type="video/mp4",
                    )
                )

        # PDF if present
        pdf_url = session_config.get("pdf_url")
        if pdf_url:
            artifacts.append(
                SessionArtifact(
                    artifact_type=ArtifactType.TEACHER_NOTES,
                    url=pdf_url,
                    mux_playback_id=None,
                    title_suffix="Teacher Notes",
                    mime_type="application/pdf",
                )
            )

        return CompoundSession(
            session_id=session_config.get("session_id", "unknown"),
            session_title=session_config.get("session_title", "Unknown Session"),
            session_url=session_config.get("session_url", ""),
            course_title=course_title,
            course_slug=course_slug,
            description=session_config.get("description", ""),
            artifacts=artifacts,
            published_at=None,
        )


__all__ = [
    "ArtifactType",
    "BibleProjectAdapter",
    "CompoundSession",
    "SessionArtifact",
    "emit_rss",
    "extract_mux_playback_ids",
    "extract_pdf_url",
    "mux_stream_url",
    "parse_session",
]
