# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for BibleProject slides API endpoints."""

import json
from pathlib import Path

import pytest
from starlette.testclient import TestClient

pytestmark = pytest.mark.unit


@pytest.fixture
def bibleproject_data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a mock BibleProject data directory and patch settings."""
    bp_dir = tmp_path / "bibleproject"
    bp_dir.mkdir(parents=True)

    # Patch settings.data_dir to use tmp_path
    from voogle import settings as settings_module

    monkeypatch.setattr(settings_module.settings, "repo_dir", tmp_path)
    # Force data_dir to return tmp_path for tests
    monkeypatch.setattr(
        type(settings_module.settings),
        "data_dir",
        property(lambda self: tmp_path),
    )

    return bp_dir


@pytest.fixture
def sample_course(bibleproject_data_dir: Path) -> Path:
    """Create a sample course with slides and assets."""
    course_dir = bibleproject_data_dir / "intro-to-bible"
    course_dir.mkdir(parents=True)

    # Create adapter config
    config = {
        "course_slug": "intro-to-bible",
        "title": "Introduction to the Bible",
        "description": "An overview of the Bible's structure and themes",
        "source": "bibleproject",
        "artwork_url": "https://cdn.example.com/intro-to-bible-artwork.jpg",
        "colors": {
            "primary": "#123456",
            "secondary": "#654321",
        },
    }
    (course_dir / "adapter_config.json").write_text(
        json.dumps(config), encoding="utf-8"
    )

    # Create slides directory
    slides_dir = course_dir / "slides"
    slides_dir.mkdir()

    # Create session slides in bp-slide-presentation format
    session1_slides = {
        "session_title": "Session 1: Overview",
        "duration": 3600.0,
        "slides": [
            {
                "timestamp": 0,
                "variant": "title",
                "content": {
                    "sessionName": "Overview",
                    "className": "Intro to Bible",
                },
                "animations": [],
            },
            {
                "timestamp": 60,
                "variant": "image",
                "content": {
                    "image": {"arc_id": "arc://image/002"},
                    "text": "The Old Testament",
                },
                "animations": [
                    {"startTime": 65, "variant": "highlight", "stringValue": "text"},
                ],
            },
            {
                "timestamp": 120,
                "variant": "multi-image",
                "content": {
                    "assets": [
                        {"arc_id": "arc://image/003"},
                        {"arc_id": "arc://image/004"},
                    ],
                    "text": "Multiple images",
                },
                "animations": [],
            },
        ],
    }
    (slides_dir / "session-1.json").write_text(
        json.dumps(session1_slides), encoding="utf-8"
    )

    session2_slides = {
        "session_title": "Session 2: Genesis",
        "slides": [
            {
                "timestamp": 0,
                "variant": "text",
                "content": {"text": "In the beginning..."},
                "animations": [],
            },
        ],
    }
    (slides_dir / "session-2.json").write_text(
        json.dumps(session2_slides), encoding="utf-8"
    )

    # Create assets manifest
    assets_data = {
        "assets": [
            {
                "arc_id": "arc://image/001",
                "asset_type": "image",
                "src": "https://cdn.example.com/img001.jpg",
                "alt": "Welcome image",
            },
            {
                "arc_id": "arc://image/002",
                "asset_type": "image",
                "src": "https://cdn.example.com/img002.jpg",
                "alt": "OT image",
            },
            {
                "arc_id": "arc://image/003",
                "asset_type": "image",
                "src": "https://cdn.example.com/img003.jpg",
                "alt": "Image 3",
            },
            {
                "arc_id": "arc://image/004",
                "asset_type": "video",
                "src": "https://cdn.example.com/vid004.mp4",
                "alt": "Video 4",
            },
        ]
    }
    (course_dir / "assets.json").write_text(json.dumps(assets_data), encoding="utf-8")

    return course_dir


@pytest.fixture
def api_client() -> TestClient:
    """Create a test client for the API."""
    from voogle.main import app

    return TestClient(app)


class TestListCourses:
    """Tests for GET /bibleproject/courses endpoint."""

    @pytest.mark.description("Returns empty list when no courses exist")
    def test_empty_list(
        self, api_client: TestClient, bibleproject_data_dir: Path
    ) -> None:
        response = api_client.get("/bibleproject/courses")

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.description("Returns course list with metadata")
    def test_list_courses(
        self, api_client: TestClient, sample_course: Path
    ) -> None:
        response = api_client.get("/bibleproject/courses")

        assert response.status_code == 200
        courses = response.json()
        assert len(courses) == 1
        assert courses[0]["slug"] == "intro-to-bible"
        assert courses[0]["title"] == "Introduction to the Bible"
        assert courses[0]["session_count"] == 2

    @pytest.mark.description("Returns multiple courses sorted")
    def test_multiple_courses(
        self, api_client: TestClient, bibleproject_data_dir: Path
    ) -> None:
        # Create additional course
        for slug in ["abraham", "genesis"]:
            course_dir = bibleproject_data_dir / slug
            course_dir.mkdir()
            (course_dir / "adapter_config.json").write_text(
                json.dumps({"title": slug.title()}), encoding="utf-8"
            )
            slides_dir = course_dir / "slides"
            slides_dir.mkdir()

        response = api_client.get("/bibleproject/courses")

        assert response.status_code == 200
        courses = response.json()
        assert len(courses) == 2
        # Should be sorted alphabetically
        assert courses[0]["slug"] == "abraham"
        assert courses[1]["slug"] == "genesis"


class TestGetCourse:
    """Tests for GET /bibleproject/courses/{slug} endpoint."""

    @pytest.mark.description("Returns 404 for non-existent course")
    def test_not_found(
        self, api_client: TestClient, bibleproject_data_dir: Path
    ) -> None:
        response = api_client.get("/bibleproject/courses/non-existent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.description("Returns course details with sessions")
    def test_get_course(
        self, api_client: TestClient, sample_course: Path
    ) -> None:
        response = api_client.get("/bibleproject/courses/intro-to-bible")

        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "intro-to-bible"
        assert data["title"] == "Introduction to the Bible"
        assert data["description"] == "An overview of the Bible's structure and themes"
        assert len(data["sessions"]) == 2

    @pytest.mark.description("Returns sessions with metadata")
    def test_session_metadata(
        self, api_client: TestClient, sample_course: Path
    ) -> None:
        response = api_client.get("/bibleproject/courses/intro-to-bible")

        data = response.json()
        sessions = sorted(data["sessions"], key=lambda s: s["id"])

        assert sessions[0]["id"] == "session-1"
        assert sessions[0]["title"] == "Session 1: Overview"
        assert sessions[0]["duration"] == 3600.0

        assert sessions[1]["id"] == "session-2"
        assert sessions[1]["title"] == "Session 2: Genesis"
        assert sessions[1]["duration"] is None


class TestGetSessionSlides:
    """Tests for GET /bibleproject/slides/{course_slug}/{session_id} endpoint."""

    @pytest.mark.description("Returns 404 for non-existent course")
    def test_course_not_found(
        self, api_client: TestClient, bibleproject_data_dir: Path
    ) -> None:
        response = api_client.get("/bibleproject/slides/non-existent/session-1")

        assert response.status_code == 404
        assert "course not found" in response.json()["detail"].lower()

    @pytest.mark.description("Returns 404 for non-existent session")
    def test_session_not_found(
        self, api_client: TestClient, sample_course: Path
    ) -> None:
        response = api_client.get("/bibleproject/slides/intro-to-bible/non-existent")

        assert response.status_code == 404
        assert "session not found" in response.json()["detail"].lower()

    @pytest.mark.description("Returns PresentationData with slides and theme")
    def test_slides_response_structure(
        self, api_client: TestClient, sample_course: Path
    ) -> None:
        response = api_client.get("/bibleproject/slides/intro-to-bible/session-1")

        assert response.status_code == 200
        data = response.json()
        # New format has presentationSlides and theme
        assert "presentationSlides" in data
        assert "theme" in data
        assert len(data["presentationSlides"]) == 3

    @pytest.mark.description("Returns theme with artwork URL from config")
    def test_theme_artwork_from_config(
        self, api_client: TestClient, sample_course: Path
    ) -> None:
        """Theme should use artwork_url from config, not derive from slug."""
        response = api_client.get("/bibleproject/slides/intro-to-bible/session-1")

        data = response.json()
        theme = data["theme"]
        assert theme["artwork"]["class"] == "https://cdn.example.com/intro-to-bible-artwork.jpg"
        assert theme["artwork"]["module"] == "https://cdn.example.com/intro-to-bible-artwork.jpg"

    @pytest.mark.description("Returns theme with colors from config")
    def test_theme_colors_from_config(
        self, api_client: TestClient, sample_course: Path
    ) -> None:
        response = api_client.get("/bibleproject/slides/intro-to-bible/session-1")

        data = response.json()
        color = data["theme"]["artwork"]["color"]
        assert color["primary"] == "#123456"
        assert color["secondary"] == "#654321"

    @pytest.mark.description("Returns flattened slide structure")
    def test_flattened_slide_structure(
        self, api_client: TestClient, sample_course: Path
    ) -> None:
        response = api_client.get("/bibleproject/slides/intro-to-bible/session-1")

        data = response.json()
        slide = data["presentationSlides"][0]

        # Slide structure should be flattened
        assert slide["startTime"] == 0
        assert slide["slide"]["variant"] == "title"
        assert slide["slide"]["sessionName"] == "Overview"
        assert slide["slide"]["className"] == "Intro to Bible"
        assert slide["animations"] == []

    @pytest.mark.description("Returns slide with animations")
    def test_slide_with_animations(
        self, api_client: TestClient, sample_course: Path
    ) -> None:
        response = api_client.get("/bibleproject/slides/intro-to-bible/session-1")

        data = response.json()
        slide = data["presentationSlides"][1]

        assert slide["startTime"] == 60
        assert len(slide["animations"]) == 1
        assert slide["animations"][0]["startTime"] == 65
        assert slide["animations"][0]["variant"] == "highlight"
        assert slide["animations"][0]["stringValue"] == "text"

    @pytest.mark.description("Includes nested image reference in slide content")
    def test_includes_image_in_content(
        self, api_client: TestClient, sample_course: Path
    ) -> None:
        response = api_client.get("/bibleproject/slides/intro-to-bible/session-1")

        data = response.json()
        slide = data["presentationSlides"][1]

        # The image object should be present in the flattened slide content
        assert "image" in slide["slide"]
        image = slide["slide"]["image"]
        # arc_id is preserved in content (asset resolution is separate)
        assert "arc_id" in image

    @pytest.mark.description("Works without assets.json file")
    def test_no_assets_manifest(
        self, api_client: TestClient, sample_course: Path
    ) -> None:
        # Remove assets.json
        (sample_course / "assets.json").unlink()

        response = api_client.get("/bibleproject/slides/intro-to-bible/session-1")

        assert response.status_code == 200
        data = response.json()
        # Should still work but arc_ids won't be resolved
        assert len(data["presentationSlides"]) == 3

    @pytest.mark.description("Uses default theme colors when not in config")
    def test_default_theme_colors(
        self, api_client: TestClient, bibleproject_data_dir: Path
    ) -> None:
        # Create course without colors in config
        course_dir = bibleproject_data_dir / "minimal"
        course_dir.mkdir()
        (course_dir / "adapter_config.json").write_text(
            json.dumps({"title": "Minimal"}), encoding="utf-8"
        )
        slides_dir = course_dir / "slides"
        slides_dir.mkdir()
        (slides_dir / "1.json").write_text(
            json.dumps({"slides": [{"variant": "title", "content": {}}]}),
            encoding="utf-8"
        )

        response = api_client.get("/bibleproject/slides/minimal/1")

        assert response.status_code == 200
        color = response.json()["theme"]["artwork"]["color"]
        # Default colors
        assert color["primary"] == "#104366"
        assert color["secondary"] == "#e24213"
