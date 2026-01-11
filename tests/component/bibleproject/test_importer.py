# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Tests for BibleProject importer module."""

import json

import pytest

from voogle.bibleproject.importer import ImportResult, import_all_courses, import_course

pytestmark = pytest.mark.component


@pytest.fixture
def mock_course_data(tmp_path):
    """Create mock research data structure for testing."""
    source_dir = tmp_path / "source"
    target_dir = tmp_path / "target"
    source_dir.mkdir()
    target_dir.mkdir()

    # Create a mock course
    course_dir = source_dir / "intro-to-bible"
    course_dir.mkdir()

    # Create metadata.json
    metadata = {
        "title": "Introduction to the Bible",
        "description": "A beginner's guide to the Bible",
    }
    (course_dir / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")

    # Create transcripts directory with VTT file
    transcripts_dir = course_dir / "transcripts"
    transcripts_dir.mkdir()
    vtt_content = """WEBVTT

00:00:00.000 --> 00:00:05.000
Hello, welcome to the course.

00:00:05.000 --> 00:00:10.000
Let's get started.
"""
    (transcripts_dir / "lesson1.vtt").write_text(vtt_content, encoding="utf-8")

    # Create slides directory
    slides_dir = course_dir / "slides"
    slides_dir.mkdir()
    (slides_dir / "slide1.json").write_text('{"title": "Slide 1"}', encoding="utf-8")
    (slides_dir / "slide2.json").write_text('{"title": "Slide 2"}', encoding="utf-8")

    # Create assets.json
    assets = {"assets": [{"arc_id": "arc://image/test", "src": "https://example.com/image.png"}]}
    (course_dir / "assets.json").write_text(json.dumps(assets), encoding="utf-8")

    return source_dir, target_dir


@pytest.fixture
def mock_multiple_courses(tmp_path):
    """Create mock data with multiple courses."""
    source_dir = tmp_path / "source"
    target_dir = tmp_path / "target"
    source_dir.mkdir()
    target_dir.mkdir()

    for course_name in ["course-a", "course-b", "course-c"]:
        course_dir = source_dir / course_name
        course_dir.mkdir()

        metadata = {"title": f"Course {course_name.upper()}", "description": f"Description for {course_name}"}
        (course_dir / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")

        transcripts_dir = course_dir / "transcripts"
        transcripts_dir.mkdir()
        vtt_content = f"""WEBVTT

00:00:00.000 --> 00:00:05.000
Content for {course_name}
"""
        (transcripts_dir / "main.vtt").write_text(vtt_content, encoding="utf-8")

    return source_dir, target_dir


class TestImportCourse:
    """Tests for import_course function."""

    def test_import_course_success(self, mock_course_data):
        """Test successful import of a single course."""
        source_dir, target_dir = mock_course_data

        result = import_course("intro-to-bible", source_dir, target_dir)

        assert result.success is True
        assert result.course_slug == "intro-to-bible"
        assert result.vtt_files_converted == 1
        assert result.slides_copied == 2
        assert result.assets_copied is True
        assert len(result.errors) == 0

    def test_import_course_creates_target_directory(self, mock_course_data):
        """Test that target directory structure is created."""
        source_dir, target_dir = mock_course_data

        import_course("intro-to-bible", source_dir, target_dir)

        course_target = target_dir / "intro-to-bible"
        assert course_target.exists()
        assert (course_target / "transcripts").exists()
        assert (course_target / "slides").exists()

    def test_import_course_creates_adapter_config(self, mock_course_data):
        """Test that adapter_config.json is generated."""
        source_dir, target_dir = mock_course_data

        import_course("intro-to-bible", source_dir, target_dir)

        config_path = target_dir / "intro-to-bible" / "adapter_config.json"
        assert config_path.exists()

        config = json.loads(config_path.read_text())
        assert config["course_slug"] == "intro-to-bible"
        assert config["title"] == "Introduction to the Bible"
        assert config["source"] == "bibleproject"

    def test_import_course_converts_vtt_to_csv(self, mock_course_data):
        """Test that VTT files are converted to CSV."""
        source_dir, target_dir = mock_course_data

        import_course("intro-to-bible", source_dir, target_dir)

        csv_path = target_dir / "intro-to-bible" / "transcripts" / "lesson1.csv"
        assert csv_path.exists()

        content = csv_path.read_text()
        lines = content.strip().split("\n")
        assert len(lines) == 2  # Two cues from the VTT

    def test_import_course_copies_slides(self, mock_course_data):
        """Test that slide files are copied."""
        source_dir, target_dir = mock_course_data

        import_course("intro-to-bible", source_dir, target_dir)

        slides_dir = target_dir / "intro-to-bible" / "slides"
        assert (slides_dir / "slide1.json").exists()
        assert (slides_dir / "slide2.json").exists()

    def test_import_course_copies_assets(self, mock_course_data):
        """Test that assets.json is copied."""
        source_dir, target_dir = mock_course_data

        import_course("intro-to-bible", source_dir, target_dir)

        assets_path = target_dir / "intro-to-bible" / "assets.json"
        assert assets_path.exists()

        assets = json.loads(assets_path.read_text())
        assert "assets" in assets

    def test_import_course_nonexistent_source(self, tmp_path):
        """Test importing from a non-existent source directory."""
        source_dir = tmp_path / "source"
        target_dir = tmp_path / "target"
        source_dir.mkdir()
        target_dir.mkdir()

        result = import_course("nonexistent", source_dir, target_dir)

        assert result.success is False
        assert len(result.errors) > 0
        assert "not found" in result.errors[0].lower()

    def test_import_course_partial_data(self, tmp_path):
        """Test importing a course with only some data present."""
        source_dir = tmp_path / "source"
        target_dir = tmp_path / "target"
        source_dir.mkdir()
        target_dir.mkdir()

        # Create course with only transcripts
        course_dir = source_dir / "partial-course"
        course_dir.mkdir()
        transcripts_dir = course_dir / "transcripts"
        transcripts_dir.mkdir()
        vtt_content = """WEBVTT

00:00:00.000 --> 00:00:05.000
Partial content.
"""
        (transcripts_dir / "main.vtt").write_text(vtt_content, encoding="utf-8")

        result = import_course("partial-course", source_dir, target_dir)

        assert result.success is True
        assert result.vtt_files_converted == 1
        assert result.slides_copied == 0
        assert result.assets_copied is False


class TestImportAllCourses:
    """Tests for import_all_courses function."""

    def test_import_all_courses_success(self, mock_multiple_courses):
        """Test importing multiple courses at once."""
        source_dir, target_dir = mock_multiple_courses

        results = import_all_courses(source_dir, target_dir)

        assert len(results) == 3
        assert all(r.success for r in results)
        slugs = {r.course_slug for r in results}
        assert slugs == {"course-a", "course-b", "course-c"}

    def test_import_all_courses_empty_source(self, tmp_path):
        """Test importing from empty source directory."""
        source_dir = tmp_path / "source"
        target_dir = tmp_path / "target"
        source_dir.mkdir()
        target_dir.mkdir()

        results = import_all_courses(source_dir, target_dir)

        assert len(results) == 0

    def test_import_all_courses_nonexistent_source(self, tmp_path):
        """Test importing from non-existent source."""
        source_dir = tmp_path / "nonexistent"
        target_dir = tmp_path / "target"

        results = import_all_courses(source_dir, target_dir)

        assert len(results) == 0

    def test_import_all_courses_skips_files(self, tmp_path):
        """Test that files in source root are skipped."""
        source_dir = tmp_path / "source"
        target_dir = tmp_path / "target"
        source_dir.mkdir()
        target_dir.mkdir()

        # Create a file in root (should be skipped)
        (source_dir / "readme.txt").write_text("readme")

        # Create a course directory
        course_dir = source_dir / "real-course"
        course_dir.mkdir()
        (course_dir / "metadata.json").write_text('{"title": "Real Course"}')

        results = import_all_courses(source_dir, target_dir)

        assert len(results) == 1
        assert results[0].course_slug == "real-course"


class TestImportResult:
    """Tests for ImportResult dataclass."""

    def test_import_result_defaults(self):
        """Test ImportResult default values."""
        result = ImportResult(course_slug="test", success=True)

        assert result.course_slug == "test"
        assert result.success is True
        assert result.vtt_files_converted == 0
        assert result.slides_copied == 0
        assert result.assets_copied is False
        assert result.errors == []

    def test_import_result_with_errors(self):
        """Test ImportResult with errors."""
        result = ImportResult(
            course_slug="test",
            success=False,
            errors=["Error 1", "Error 2"],
        )

        assert result.success is False
        assert len(result.errors) == 2
