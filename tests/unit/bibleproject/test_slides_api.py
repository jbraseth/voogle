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
    original_data_dir = type(settings_module.settings).data_dir
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
    }
    (course_dir / "adapter_config.json").write_text(
        json.dumps(config), encoding="utf-8"
    )

    # Create slides directory
    slides_dir = course_dir / "slides"
    slides_dir.mkdir()

    # Create session slides
    session1_slides = {
        "title": "Session 1: Overview",
        "duration": 3600.0,
        "slides": [
            {
                "arc_id": "arc://image/001",
                "text": "Welcome to the Bible",
            },
            {
                "image": {"arc_id": "arc://image/002"},
                "text": "The Old Testament",
            },
            {
                "assets": [
                    {"arc_id": "arc://image/003"},
                    {"arc_id": "arc://image/004"},
                ],
                "text": "Multiple images",
            },
        ],
    }
    (slides_dir / "session-1.json").write_text(
        json.dumps(session1_slides), encoding="utf-8"
    )

    session2_slides = {
        "title": "Session 2: Genesis",
        "slides": [
            {"text": "In the beginning..."},
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
                "caption": "Welcome to the course",
                "title": "Welcome",
            },
            {
                "arc_id": "arc://image/002",
                "asset_type": "image",
                "src": "https://cdn.example.com/img002.jpg",
                "alt": "Old Testament",
                "caption": "",
                "title": "OT Overview",
            },
            {
                "arc_id": "arc://image/003",
                "asset_type": "image",
                "src": "https://cdn.example.com/img003.jpg",
                "alt": "Image 3",
                "caption": "",
                "title": "",
            },
            {
                "arc_id": "arc://image/004",
                "asset_type": "video",
                "src": "https://cdn.example.com/vid004.mp4",
                "alt": "",
                "caption": "Video clip",
                "title": "Video",
            },
        ]
    }
    (course_dir / "assets.json").write_text(
        json.dumps(assets_data), encoding="utf-8"
    )

    return course_dir


@pytest.fixture
def api_client() -> TestClient:
    """Create a test client for the API."""
    from voogle import main

    return TestClient(main.app)


class TestListCourses:
    """Tests for GET /bibleproject/courses endpoint."""

    @pytest.mark.description("Returns empty list when no courses exist")
    def test_empty_list(
        self, api_client: TestClient, bibleproject_data_dir: Path
    ) -> None:
        response = api_client.get("/bibleproject/courses")

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.description("Returns list of courses with metadata")
    def test_list_courses(
        self, api_client: TestClient, sample_course: Path
    ) -> None:
        response = api_client.get("/bibleproject/courses")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["slug"] == "intro-to-bible"
        assert data[0]["title"] == "Introduction to the Bible"
        assert data[0]["session_count"] == 2

    @pytest.mark.description("Lists multiple courses sorted by name")
    def test_multiple_courses(
        self, api_client: TestClient, bibleproject_data_dir: Path
    ) -> None:
        # Create two courses
        for slug, title in [("aaa-course", "AAA Course"), ("zzz-course", "ZZZ Course")]:
            course_dir = bibleproject_data_dir / slug
            course_dir.mkdir()
            (course_dir / "adapter_config.json").write_text(
                json.dumps({"title": title}), encoding="utf-8"
            )

        response = api_client.get("/bibleproject/courses")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["slug"] == "aaa-course"
        assert data[1]["slug"] == "zzz-course"


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

    @pytest.mark.description("Returns slides with total count")
    def test_slides_response_structure(
        self, api_client: TestClient, sample_course: Path
    ) -> None:
        response = api_client.get("/bibleproject/slides/intro-to-bible/session-1")

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "session-1"
        assert data["total_slides"] == 3
        assert len(data["slides"]) == 3

    @pytest.mark.description("Resolves top-level arc_id to CDN URL")
    def test_resolves_top_level_arc_id(
        self, api_client: TestClient, sample_course: Path
    ) -> None:
        response = api_client.get("/bibleproject/slides/intro-to-bible/session-1")

        data = response.json()
        slide = data["slides"][0]

        assert slide["slide_index"] == 0
        assert "arc://image/001" in slide["resolved_assets"]
        asset = slide["resolved_assets"]["arc://image/001"]
        assert asset["src"] == "https://cdn.example.com/img001.jpg"
        assert asset["alt"] == "Welcome image"
        assert asset["asset_type"] == "image"

    @pytest.mark.description("Resolves nested image arc_id")
    def test_resolves_nested_image(
        self, api_client: TestClient, sample_course: Path
    ) -> None:
        response = api_client.get("/bibleproject/slides/intro-to-bible/session-1")

        data = response.json()
        slide = data["slides"][1]

        assert "arc://image/002" in slide["resolved_assets"]
        asset = slide["resolved_assets"]["arc://image/002"]
        assert asset["src"] == "https://cdn.example.com/img002.jpg"

    @pytest.mark.description("Resolves assets array")
    def test_resolves_assets_array(
        self, api_client: TestClient, sample_course: Path
    ) -> None:
        response = api_client.get("/bibleproject/slides/intro-to-bible/session-1")

        data = response.json()
        slide = data["slides"][2]

        assert "arc://image/003" in slide["resolved_assets"]
        assert "arc://image/004" in slide["resolved_assets"]
        assert slide["resolved_assets"]["arc://image/003"]["asset_type"] == "image"
        assert slide["resolved_assets"]["arc://image/004"]["asset_type"] == "video"
        assert slide["resolved_assets"]["arc://image/004"]["src"] == "https://cdn.example.com/vid004.mp4"

    @pytest.mark.description("Handles slides without assets")
    def test_slides_without_assets(
        self, api_client: TestClient, sample_course: Path
    ) -> None:
        response = api_client.get("/bibleproject/slides/intro-to-bible/session-2")

        assert response.status_code == 200
        data = response.json()
        assert data["total_slides"] == 1
        slide = data["slides"][0]
        assert slide["resolved_assets"] == {}
        assert slide["content"]["text"] == "In the beginning..."

    @pytest.mark.description("Works without assets.json file")
    def test_no_assets_manifest(
        self, api_client: TestClient, sample_course: Path
    ) -> None:
        # Remove assets.json
        (sample_course / "assets.json").unlink()

        response = api_client.get("/bibleproject/slides/intro-to-bible/session-1")

        assert response.status_code == 200
        data = response.json()
        # Should still work but with no resolved assets
        assert data["total_slides"] == 3
        # Arc IDs should not be resolved since manifest is missing
        assert data["slides"][0]["resolved_assets"] == {}
