# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for BibleProject Classroom source adapter.

Tests are organized by function:
- Data types (ArtifactType, SessionArtifact, CompoundSession)
- extract_mux_playback_ids() - Mux player detection
- extract_pdf_url() - PDF link detection
- parse_session() - Session parsing
- emit_rss() - RSS feed generation with multi-item encoding
- BibleProjectAdapter - Full adapter workflow
"""

from datetime import datetime, timezone
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

from voogle.sources.bibleproject import (
    ArtifactType,
    BibleProjectAdapter,
    CompoundSession,
    SessionArtifact,
    emit_rss,
    extract_mux_playback_ids,
    extract_pdf_url,
    mux_stream_url,
    parse_session,
)

pytestmark = pytest.mark.unit


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def fixtures_dir() -> Path:
    return Path(__file__).parent.parent.parent / "fixtures" / "bibleproject"


@pytest.fixture
def main_only_html(fixtures_dir: Path) -> str:
    return (fixtures_dir / "session_main_only.html").read_text()


@pytest.fixture
def main_slides_html(fixtures_dir: Path) -> str:
    return (fixtures_dir / "session_main_slides.html").read_text()


@pytest.fixture
def main_pdf_html(fixtures_dir: Path) -> str:
    return (fixtures_dir / "session_main_pdf.html").read_text()


@pytest.fixture
def all_artifacts_html(fixtures_dir: Path) -> str:
    return (fixtures_dir / "session_all_artifacts.html").read_text()


@pytest.fixture
def js_config_html(fixtures_dir: Path) -> str:
    return (fixtures_dir / "session_js_config.html").read_text()


# =============================================================================
# Data Type Tests
# =============================================================================


class TestArtifactType:
    @pytest.mark.description("ArtifactType enum has expected values")
    def test_artifact_type_values(self) -> None:
        assert ArtifactType.MAIN_VIDEO.value == "main"
        assert ArtifactType.SLIDES_VIDEO.value == "slides"
        assert ArtifactType.TEACHER_NOTES.value == "pdf"


class TestSessionArtifact:
    @pytest.mark.description("SessionArtifact correctly identifies video artifacts")
    def test_is_video_for_main(self) -> None:
        artifact = SessionArtifact(
            artifact_type=ArtifactType.MAIN_VIDEO,
            url="https://stream.mux.com/abc123.m3u8",
            mux_playback_id="abc123",
            title_suffix="Main Video",
            mime_type="video/mp4",
        )
        assert artifact.is_video is True

    @pytest.mark.description("SessionArtifact correctly identifies video artifacts for slides")
    def test_is_video_for_slides(self) -> None:
        artifact = SessionArtifact(
            artifact_type=ArtifactType.SLIDES_VIDEO,
            url="https://stream.mux.com/def456.m3u8",
            mux_playback_id="def456",
            title_suffix="Slides",
            mime_type="video/mp4",
        )
        assert artifact.is_video is True

    @pytest.mark.description("SessionArtifact correctly identifies PDF as non-video")
    def test_is_video_for_pdf(self) -> None:
        artifact = SessionArtifact(
            artifact_type=ArtifactType.TEACHER_NOTES,
            url="https://example.com/notes.pdf",
            mux_playback_id=None,
            title_suffix="Teacher Notes",
            mime_type="application/pdf",
        )
        assert artifact.is_video is False


class TestCompoundSession:
    @pytest.mark.description("CompoundSession provides accessors for different artifact types")
    def test_artifact_accessors(self) -> None:
        main = SessionArtifact(
            artifact_type=ArtifactType.MAIN_VIDEO,
            url="https://stream.mux.com/main.m3u8",
            mux_playback_id="main",
            title_suffix="Main Video",
            mime_type="video/mp4",
        )
        slides = SessionArtifact(
            artifact_type=ArtifactType.SLIDES_VIDEO,
            url="https://stream.mux.com/slides.m3u8",
            mux_playback_id="slides",
            title_suffix="Slides",
            mime_type="video/mp4",
        )
        pdf = SessionArtifact(
            artifact_type=ArtifactType.TEACHER_NOTES,
            url="https://example.com/notes.pdf",
            mux_playback_id=None,
            title_suffix="Teacher Notes",
            mime_type="application/pdf",
        )

        session = CompoundSession(
            session_id="s1",
            session_title="Session 1",
            session_url="https://example.com/s1",
            course_title="Test Course",
            course_slug="test-course",
            description="Test description",
            artifacts=[main, slides, pdf],
        )

        assert session.main_video == main
        assert session.slides_video == slides
        assert session.teacher_notes == pdf

    @pytest.mark.description("CompoundSession returns None for missing artifact types")
    def test_missing_artifact_accessors(self) -> None:
        main = SessionArtifact(
            artifact_type=ArtifactType.MAIN_VIDEO,
            url="https://stream.mux.com/main.m3u8",
            mux_playback_id="main",
            title_suffix="Main Video",
            mime_type="video/mp4",
        )

        session = CompoundSession(
            session_id="s1",
            session_title="Session 1",
            session_url="https://example.com/s1",
            course_title="Test Course",
            course_slug="test-course",
            description="",
            artifacts=[main],
        )

        assert session.main_video == main
        assert session.slides_video is None
        assert session.teacher_notes is None


# =============================================================================
# extract_mux_playback_ids() Tests
# =============================================================================


class TestExtractMuxPlaybackIds:
    @pytest.mark.description("Extract single Mux playback ID from main-only session")
    def test_main_only(self, main_only_html: str) -> None:
        ids = extract_mux_playback_ids(main_only_html)
        assert len(ids) == 1
        assert ids[0] == "abc123mainvideo"

    @pytest.mark.description("Extract both Mux playback IDs from main+slides session")
    def test_main_and_slides(self, main_slides_html: str) -> None:
        ids = extract_mux_playback_ids(main_slides_html)
        assert len(ids) == 2
        assert ids[0] == "def456mainvideo"
        assert ids[1] == "ghi789slidesvid"

    @pytest.mark.description("Extract multiple IDs from session with all artifacts")
    def test_all_artifacts(self, all_artifacts_html: str) -> None:
        ids = extract_mux_playback_ids(all_artifacts_html)
        assert len(ids) == 2
        assert ids[0] == "mno345mainvideo"
        assert ids[1] == "pqr678slidesvid"

    @pytest.mark.description("Extract IDs from JavaScript config patterns")
    def test_js_config_patterns(self, js_config_html: str) -> None:
        ids = extract_mux_playback_ids(js_config_html)
        assert len(ids) >= 2
        assert "stu901jsconfig" in ids
        assert "vwx234altconfig" in ids

    @pytest.mark.description("Deduplicate repeated playback IDs")
    def test_deduplication(self) -> None:
        html = '''
        <mux-player playback-id="abc123"></mux-player>
        <div data-playback-id="abc123"></div>
        <script>{ playbackId: "abc123" }</script>
        '''
        ids = extract_mux_playback_ids(html)
        assert len(ids) == 1
        assert ids[0] == "abc123"

    @pytest.mark.description("Return empty list when no Mux IDs found")
    def test_no_ids(self) -> None:
        html = "<html><body>No video here</body></html>"
        ids = extract_mux_playback_ids(html)
        assert ids == []


# =============================================================================
# extract_pdf_url() Tests
# =============================================================================


class TestExtractPdfUrl:
    @pytest.mark.description("Extract PDF URL from session with teacher notes")
    def test_extract_pdf(self, main_pdf_html: str) -> None:
        url = extract_pdf_url(main_pdf_html)
        assert url == "https://classroom.bibleproject.com/downloads/session3-teacher-notes.pdf"

    @pytest.mark.description("Extract PDF URL from session with all artifacts")
    def test_extract_pdf_all_artifacts(self, all_artifacts_html: str) -> None:
        url = extract_pdf_url(all_artifacts_html)
        assert url == "https://classroom.bibleproject.com/downloads/session4-teacher-notes.pdf"

    @pytest.mark.description("Extract relative PDF URL")
    def test_relative_pdf_url(self, js_config_html: str) -> None:
        url = extract_pdf_url(js_config_html)
        assert url == "/assets/pdfs/session5-notes.pdf"

    @pytest.mark.description("Return None when no PDF found")
    def test_no_pdf(self, main_only_html: str) -> None:
        url = extract_pdf_url(main_only_html)
        assert url is None


# =============================================================================
# mux_stream_url() Tests
# =============================================================================


class TestMuxStreamUrl:
    @pytest.mark.description("Generate correct Mux HLS stream URL")
    def test_stream_url(self) -> None:
        url = mux_stream_url("abc123xyz")
        assert url == "https://stream.mux.com/abc123xyz.m3u8"


# =============================================================================
# parse_session() Tests
# =============================================================================


class TestParseSession:
    @pytest.mark.description("Parse session with only main video")
    def test_main_only(self, main_only_html: str) -> None:
        session = parse_session(
            html=main_only_html,
            session_url="https://example.com/s1",
            session_id="s1",
            session_title="Session 1",
            course_title="Test Course",
            course_slug="test-course",
        )

        assert session.session_id == "s1"
        assert session.session_title == "Session 1"
        assert len(session.artifacts) == 1
        assert session.main_video is not None
        assert session.main_video.mux_playback_id == "abc123mainvideo"
        assert session.slides_video is None
        assert session.teacher_notes is None

    @pytest.mark.description("Parse session with main + slides videos")
    def test_main_slides(self, main_slides_html: str) -> None:
        session = parse_session(
            html=main_slides_html,
            session_url="https://example.com/s2",
            session_id="s2",
            session_title="Session 2",
            course_title="Test Course",
            course_slug="test-course",
        )

        assert len(session.artifacts) == 2
        assert session.main_video is not None
        assert session.main_video.mux_playback_id == "def456mainvideo"
        assert session.slides_video is not None
        assert session.slides_video.mux_playback_id == "ghi789slidesvid"
        assert session.teacher_notes is None

    @pytest.mark.description("Parse session with main video + PDF")
    def test_main_pdf(self, main_pdf_html: str) -> None:
        session = parse_session(
            html=main_pdf_html,
            session_url="https://example.com/s3",
            session_id="s3",
            session_title="Session 3",
            course_title="Test Course",
            course_slug="test-course",
        )

        assert len(session.artifacts) == 2
        assert session.main_video is not None
        assert session.slides_video is None
        assert session.teacher_notes is not None
        assert session.teacher_notes.mime_type == "application/pdf"

    @pytest.mark.description("Parse session with all artifacts")
    def test_all_artifacts(self, all_artifacts_html: str) -> None:
        session = parse_session(
            html=all_artifacts_html,
            session_url="https://example.com/s4",
            session_id="s4",
            session_title="Session 4",
            course_title="Test Course",
            course_slug="test-course",
        )

        assert len(session.artifacts) == 3
        assert session.main_video is not None
        assert session.slides_video is not None
        assert session.teacher_notes is not None

    @pytest.mark.description("Raise ValueError when no Mux IDs found")
    def test_no_video_raises(self) -> None:
        html = "<html><body>No video</body></html>"
        with pytest.raises(ValueError, match="No Mux playback IDs found"):
            parse_session(
                html=html,
                session_url="https://example.com/s1",
                session_id="s1",
                session_title="Session 1",
                course_title="Test",
                course_slug="test",
            )


# =============================================================================
# emit_rss() Tests
# =============================================================================


class TestEmitRss:
    @pytest.mark.description("Session with 3 artifacts produces 3 RSS items")
    def test_compound_session_rss(self, tmp_path: Path) -> None:
        main = SessionArtifact(
            artifact_type=ArtifactType.MAIN_VIDEO,
            url="https://stream.mux.com/main.m3u8",
            mux_playback_id="main",
            title_suffix="Main Video",
            mime_type="video/mp4",
        )
        slides = SessionArtifact(
            artifact_type=ArtifactType.SLIDES_VIDEO,
            url="https://stream.mux.com/slides.m3u8",
            mux_playback_id="slides",
            title_suffix="Slides",
            mime_type="video/mp4",
        )
        pdf = SessionArtifact(
            artifact_type=ArtifactType.TEACHER_NOTES,
            url="https://example.com/notes.pdf",
            mux_playback_id=None,
            title_suffix="Teacher Notes",
            mime_type="application/pdf",
        )

        session = CompoundSession(
            session_id="s1",
            session_title="Introduction",
            session_url="https://example.com/s1",
            course_title="Test Course",
            course_slug="test-course",
            description="Test description",
            artifacts=[main, slides, pdf],
        )

        output_path = tmp_path / "feed.xml"
        emit_rss([session], output_path)

        tree = ET.parse(output_path)
        items = tree.findall(".//item")
        assert len(items) == 3

        # Verify titles
        titles = [item.find("title").text for item in items]
        assert "Introduction - Main Video" in titles
        assert "Introduction - Slides" in titles
        assert "Introduction - Teacher Notes" in titles

        # Verify MIME types
        enclosures = [item.find("enclosure") for item in items]
        types = [e.get("type") for e in enclosures]
        assert types.count("video/mp4") == 2
        assert types.count("application/pdf") == 1

    @pytest.mark.description("GUIDs follow correct format")
    def test_guid_format(self, tmp_path: Path) -> None:
        main = SessionArtifact(
            artifact_type=ArtifactType.MAIN_VIDEO,
            url="https://stream.mux.com/main.m3u8",
            mux_playback_id="main",
            title_suffix="Main Video",
            mime_type="video/mp4",
        )

        session = CompoundSession(
            session_id="s1",
            session_title="Introduction",
            session_url="https://example.com/s1",
            course_title="Test Course",
            course_slug="test-course",
            description="",
            artifacts=[main],
        )

        output_path = tmp_path / "feed.xml"
        emit_rss([session], output_path)

        tree = ET.parse(output_path)
        guid = tree.find(".//item/guid")
        assert guid.text == "bibleproject:test-course:s1:main"
        assert guid.get("isPermaLink") == "false"

    @pytest.mark.description("Single session with only main video produces 1 item")
    def test_single_artifact(self, tmp_path: Path) -> None:
        main = SessionArtifact(
            artifact_type=ArtifactType.MAIN_VIDEO,
            url="https://stream.mux.com/main.m3u8",
            mux_playback_id="main",
            title_suffix="Main Video",
            mime_type="video/mp4",
        )

        session = CompoundSession(
            session_id="s1",
            session_title="Session 1",
            session_url="https://example.com/s1",
            course_title="Test Course",
            course_slug="test-course",
            description="",
            artifacts=[main],
        )

        output_path = tmp_path / "feed.xml"
        emit_rss([session], output_path)

        tree = ET.parse(output_path)
        items = tree.findall(".//item")
        assert len(items) == 1

    @pytest.mark.description("Multiple sessions produce correct item count")
    def test_multiple_sessions(self, tmp_path: Path) -> None:
        # Session 1: 2 artifacts
        s1_main = SessionArtifact(
            artifact_type=ArtifactType.MAIN_VIDEO,
            url="https://stream.mux.com/s1main.m3u8",
            mux_playback_id="s1main",
            title_suffix="Main Video",
            mime_type="video/mp4",
        )
        s1_slides = SessionArtifact(
            artifact_type=ArtifactType.SLIDES_VIDEO,
            url="https://stream.mux.com/s1slides.m3u8",
            mux_playback_id="s1slides",
            title_suffix="Slides",
            mime_type="video/mp4",
        )
        session1 = CompoundSession(
            session_id="s1",
            session_title="Session 1",
            session_url="https://example.com/s1",
            course_title="Test Course",
            course_slug="test-course",
            description="",
            artifacts=[s1_main, s1_slides],
        )

        # Session 2: 1 artifact
        s2_main = SessionArtifact(
            artifact_type=ArtifactType.MAIN_VIDEO,
            url="https://stream.mux.com/s2main.m3u8",
            mux_playback_id="s2main",
            title_suffix="Main Video",
            mime_type="video/mp4",
        )
        session2 = CompoundSession(
            session_id="s2",
            session_title="Session 2",
            session_url="https://example.com/s2",
            course_title="Test Course",
            course_slug="test-course",
            description="",
            artifacts=[s2_main],
        )

        output_path = tmp_path / "feed.xml"
        emit_rss([session1, session2], output_path)

        tree = ET.parse(output_path)
        items = tree.findall(".//item")
        assert len(items) == 3  # 2 from session1 + 1 from session2

    @pytest.mark.description("Empty session list produces valid empty RSS")
    def test_empty_sessions(self, tmp_path: Path) -> None:
        output_path = tmp_path / "feed.xml"
        emit_rss([], output_path)

        tree = ET.parse(output_path)
        assert tree.getroot().tag == "rss"
        items = tree.findall(".//item")
        assert len(items) == 0


# =============================================================================
# BibleProjectAdapter Tests
# =============================================================================


class TestBibleProjectAdapter:
    @pytest.mark.description("Adapter generates feeds from config files")
    def test_generate_feeds(self, tmp_path: Path) -> None:
        config_dir = tmp_path / "config"
        output_dir = tmp_path / "output"
        config_dir.mkdir()

        # Create test config
        config = {
            "course_slug": "test-course",
            "course_title": "Test Course",
            "sessions": [
                {
                    "session_id": "s1",
                    "session_title": "Session 1",
                    "session_url": "https://example.com/s1",
                    "mux_ids": ["main123", "slides456"],
                    "pdf_url": "https://example.com/notes.pdf",
                }
            ],
        }

        import json
        (config_dir / "test-course.json").write_text(json.dumps(config))

        adapter = BibleProjectAdapter(config_dir, output_dir)
        feeds = adapter.generate_feeds()

        assert len(feeds) == 1
        assert feeds[0].source_id == "bibleproject"
        assert feeds[0].channel_url == "local://bibleproject/test-course"
        assert feeds[0].path.exists()

        # Verify RSS content
        tree = ET.parse(feeds[0].path)
        items = tree.findall(".//item")
        assert len(items) == 3  # main + slides + pdf

    @pytest.mark.description("Adapter returns empty list for missing config dir")
    def test_missing_config_dir(self, tmp_path: Path) -> None:
        config_dir = tmp_path / "nonexistent"
        output_dir = tmp_path / "output"

        adapter = BibleProjectAdapter(config_dir, output_dir)
        feeds = adapter.generate_feeds()

        assert feeds == []

    @pytest.mark.description("Adapter returns empty list for empty config dir")
    def test_empty_config_dir(self, tmp_path: Path) -> None:
        config_dir = tmp_path / "config"
        output_dir = tmp_path / "output"
        config_dir.mkdir()

        adapter = BibleProjectAdapter(config_dir, output_dir)
        feeds = adapter.generate_feeds()

        assert feeds == []

    @pytest.mark.description("Adapter properties return correct values")
    def test_adapter_properties(self, tmp_path: Path) -> None:
        config_dir = tmp_path / "config"
        output_dir = tmp_path / "output"

        adapter = BibleProjectAdapter(config_dir, output_dir)

        assert adapter.adapter_id == "bibleproject"
        assert adapter.config_dir == config_dir
        assert adapter.output_dir == output_dir
