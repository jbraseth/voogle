# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""BibleProject API router.

Provides endpoints for serving course and slide data with resolved asset URLs.
"""

import json
import logging
from pathlib import Path

import fastapi

from voogle.bibleproject import assets
from voogle.schemas import bibleproject as bp_schemas
from voogle.settings import settings

logger = logging.getLogger(__name__)
router = fastapi.APIRouter(prefix="/bibleproject", tags=["bibleproject"])


def _get_bibleproject_dir() -> Path:
    """Get the BibleProject data directory."""
    return settings.data_dir / "bibleproject"


def _load_course_config(course_dir: Path) -> dict | None:
    """Load adapter_config.json from a course directory."""
    config_file = course_dir / "adapter_config.json"
    if not config_file.exists():
        return None
    try:
        return json.loads(config_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Failed to load course config from {config_file}: {e}")
        return None


def _count_sessions(course_dir: Path) -> int:
    """Count the number of sessions (slide files) in a course."""
    slides_dir = course_dir / "slides"
    if not slides_dir.exists():
        return 0
    return len(list(slides_dir.glob("*.json")))


def _get_course_image(course_dir: Path) -> str | None:
    """Get the course image URL if available."""
    # Look for image in config or assets
    config = _load_course_config(course_dir)
    if config and config.get("image"):
        return config["image"]
    return None


@router.get(
    "/courses",
    summary="List all available courses",
    response_model=list[bp_schemas.CourseListItem],
)
def list_courses() -> list[bp_schemas.CourseListItem]:
    """Get a list of all available BibleProject courses."""
    bp_dir = _get_bibleproject_dir()
    if not bp_dir.exists():
        return []

    courses: list[bp_schemas.CourseListItem] = []
    for item in sorted(bp_dir.iterdir()):
        if not item.is_dir():
            continue

        config = _load_course_config(item)
        if config is None:
            continue

        courses.append(
            bp_schemas.CourseListItem(
                slug=item.name,
                title=config.get("title", item.name),
                session_count=_count_sessions(item),
                image=_get_course_image(item),
            )
        )

    return courses


@router.get(
    "/courses/{slug}",
    summary="Get course details",
    response_model=bp_schemas.CourseDetail,
)
def get_course(slug: str) -> bp_schemas.CourseDetail:
    """Get detailed information about a course including its sessions."""
    bp_dir = _get_bibleproject_dir()
    course_dir = bp_dir / slug

    if not course_dir.exists():
        raise fastapi.HTTPException(status_code=404, detail=f"Course not found: {slug}")

    config = _load_course_config(course_dir)
    if config is None:
        raise fastapi.HTTPException(
            status_code=404, detail=f"Course config not found: {slug}"
        )

    # Load session information from slides
    sessions: list[bp_schemas.SessionSummary] = []
    slides_dir = course_dir / "slides"
    if slides_dir.exists():
        for slide_file in sorted(slides_dir.glob("*.json")):
            session_id = slide_file.stem
            # Try to load slide file to get title/duration
            try:
                slide_data = json.loads(slide_file.read_text(encoding="utf-8"))
                title = slide_data.get("title", session_id)
                duration = slide_data.get("duration")
            except (json.JSONDecodeError, OSError):
                title = session_id
                duration = None

            sessions.append(
                bp_schemas.SessionSummary(
                    id=session_id,
                    title=title,
                    duration=duration,
                )
            )

    return bp_schemas.CourseDetail(
        slug=slug,
        title=config.get("title", slug),
        description=config.get("description"),
        sessions=sessions,
    )


def _load_slides_data(course_slug: str, session_id: str) -> tuple[dict, dict]:
    """Load slides data and assets manifest for a session.

    Returns:
        Tuple of (slides_data dict, assets manifest dict)
    """
    bp_dir = _get_bibleproject_dir()
    course_dir = bp_dir / course_slug

    if not course_dir.exists():
        raise fastapi.HTTPException(
            status_code=404, detail=f"Course not found: {course_slug}"
        )

    slides_file = course_dir / "slides" / f"{session_id}.json"
    if not slides_file.exists():
        raise fastapi.HTTPException(
            status_code=404,
            detail=f"Session not found: {session_id} in course {course_slug}",
        )

    # Load slides
    try:
        slides_data = json.loads(slides_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        raise fastapi.HTTPException(
            status_code=500, detail=f"Failed to load slides: {e}"
        ) from e

    # Load assets manifest
    assets_file = course_dir / "assets.json"
    manifest: dict[str, assets.AssetInfo] = {}
    if assets_file.exists():
        try:
            manifest = assets.load_assets_manifest(assets_file)
        except (ValueError, OSError) as e:
            logger.warning(f"Failed to load assets manifest: {e}")

    return slides_data, manifest


@router.get(
    "/slides/{course_slug}/{session_id}",
    summary="Get slides for a session",
    response_model=bp_schemas.PresentationData,
)
def get_session_slides(course_slug: str, session_id: str) -> bp_schemas.PresentationData:
    """Get slides in the format expected by bp-slide-presentation web component.

    Returns data structured as:
    {
      "presentationSlides": [
        {
          "startTime": 0,  // timestamp in seconds
          "slide": { "variant": "title", "content": { ... } },
          "animations": [...]
        }
      ]
    }
    """
    slides_data, manifest = _load_slides_data(course_slug, session_id)

    # Get slides list from data
    slides_list = slides_data.get("slides", [])
    if not isinstance(slides_list, list):
        slides_list = []

    # Process each slide into bp-slide-presentation format
    presentation_slides: list[bp_schemas.PresentationSlide] = []
    for raw_slide in slides_list:
        if not isinstance(raw_slide, dict):
            continue

        # Resolve assets in the slide
        resolved_slide = assets.resolve_slide_assets(raw_slide, manifest)

        # Extract variant and content
        variant = resolved_slide.get("variant", "")
        content = resolved_slide.get("content", {})

        # Get timestamp (convert to int seconds)
        timestamp = raw_slide.get("timestamp", 0)
        if isinstance(timestamp, str):
            # Handle "MM:SS" format if present
            parts = timestamp.split(":")
            if len(parts) == 2:
                timestamp = int(parts[0]) * 60 + int(parts[1])
            else:
                timestamp = int(timestamp)

        # Process animations - keep original format as bp-slide-presentation expects
        raw_animations = raw_slide.get("animations", [])
        animations: list[bp_schemas.SlideAnimation] = []
        for anim in raw_animations:
            if isinstance(anim, dict):
                animations.append(
                    bp_schemas.SlideAnimation(
                        startTime=anim.get("startTime", 0),
                        variant=anim.get("variant", ""),
                        stringValue=anim.get("stringValue"),
                        extraArg=anim.get("extraArg"),
                    )
                )

        presentation_slides.append(
            bp_schemas.PresentationSlide(
                startTime=timestamp,
                slide=bp_schemas.SlideContent(
                    variant=variant,
                    content=content,
                ),
                animations=animations,
            )
        )

    return bp_schemas.PresentationData(presentationSlides=presentation_slides)
