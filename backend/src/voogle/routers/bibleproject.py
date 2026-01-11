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
    return settings.data_dir / "local" / "bibleproject"


def _load_course_config(course_dir: Path) -> dict | None:
    """Load config.json from a course directory."""
    config_file = course_dir / "config.json"
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


@router.get(
    "/slides/{course_slug}/{session_id}",
    summary="Get slides for a session",
    response_model=bp_schemas.SessionSlides,
)
def get_session_slides(course_slug: str, session_id: str) -> bp_schemas.SessionSlides:
    """Get all slides for a session with resolved asset URLs."""
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

    # Load assets manifest (stored at bibleproject root level)
    assets_file = _get_bibleproject_dir() / "assets.json"
    manifest: dict[str, assets.AssetInfo] = {}
    if assets_file.exists():
        try:
            manifest = assets.load_assets_manifest(assets_file)
        except (ValueError, OSError) as e:
            logger.warning(f"Failed to load assets manifest: {e}")

    # Get slides list from data
    slides_list = slides_data.get("slides", [])
    if not isinstance(slides_list, list):
        slides_list = []

    # Process each slide
    processed_slides: list[bp_schemas.Slide] = []
    for idx, raw_slide in enumerate(slides_list):
        if not isinstance(raw_slide, dict):
            continue

        # Resolve assets in the slide
        resolved_slide = assets.resolve_slide_assets(raw_slide, manifest)

        # Collect all resolved assets into a dict
        resolved_assets: dict[str, bp_schemas.ResolvedAsset] = {}

        # From top-level resolved_asset
        if "resolved_asset" in resolved_slide and "arc_id" in raw_slide:
            asset_data = resolved_slide["resolved_asset"]
            resolved_assets[raw_slide["arc_id"]] = bp_schemas.ResolvedAsset(
                src=asset_data.get("src", ""),
                alt=asset_data.get("alt", ""),
                caption=asset_data.get("caption", ""),
                title=asset_data.get("title", ""),
                asset_type=asset_data.get("asset_type", "unknown"),
            )

        # From nested image
        if "image" in resolved_slide and isinstance(resolved_slide["image"], dict):
            image = resolved_slide["image"]
            if "arc_id" in image and "src" in image:
                resolved_assets[image["arc_id"]] = bp_schemas.ResolvedAsset(
                    src=image.get("src", ""),
                    alt=image.get("alt", ""),
                    caption=image.get("caption", ""),
                    title=image.get("title", ""),
                    asset_type=image.get("asset_type", "image"),
                )

        # From assets array
        if "assets" in resolved_slide and isinstance(resolved_slide["assets"], list):
            for asset_item in resolved_slide["assets"]:
                if isinstance(asset_item, dict) and "arc_id" in asset_item and "src" in asset_item:
                    resolved_assets[asset_item["arc_id"]] = bp_schemas.ResolvedAsset(
                        src=asset_item.get("src", ""),
                        alt=asset_item.get("alt", ""),
                        caption=asset_item.get("caption", ""),
                        title=asset_item.get("title", ""),
                        asset_type=asset_item.get("asset_type", "unknown"),
                    )

        processed_slides.append(
            bp_schemas.Slide(
                slide_index=idx,
                content=resolved_slide,
                resolved_assets=resolved_assets,
            )
        )

    return bp_schemas.SessionSlides(
        session_id=session_id,
        total_slides=len(processed_slides),
        slides=processed_slides,
    )
