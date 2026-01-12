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
from voogle.models import media
from voogle.schemas import bibleproject as bp_schemas
from voogle.schemas import media as media_schemas
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


# BibleProject CDN base URL for static assets
BP_CDN_BASE = "https://d3kfvpfexuy5fk.cloudfront.net/_static/assets"


def _get_class_artwork_url(artwork_slug: str) -> str:
    """Derive class artwork URL from artwork slug.

    BibleProject uses predictable CDN URLs:
    https://d3kfvpfexuy5fk.cloudfront.net/_static/assets/artwork/{slug}/class-{slug}-square.jpg

    Note: The artwork_slug may differ from the course directory slug.
    For example, "1-corinthians" uses artwork slug "1-corinthians-lucy-peppiatt".
    """
    return f"{BP_CDN_BASE}/artwork/{artwork_slug}/class-{artwork_slug}-square.jpg"


def _get_bp_slug_from_metadata(course_slug: str) -> str | None:
    """Extract the actual BibleProject class slug from scraped metadata.

    The metadata session_url contains the real BP slug, e.g.:
    https://bibleproject.com/classroom/1-corinthians-lucy-peppiatt/sessions/1
    -> returns "1-corinthians-lucy-peppiatt"
    """
    import re

    metadata_dir = Path.home() / "projects/bibleproject-research/data/metadata" / course_slug
    if not metadata_dir.exists():
        return None

    # Try to read the first session's metadata
    session_file = metadata_dir / "1.json"
    if not session_file.exists():
        # Try to find any session file
        session_files = list(metadata_dir.glob("*.json"))
        if not session_files:
            return None
        session_file = session_files[0]

    try:
        data = json.loads(session_file.read_text(encoding="utf-8"))
        session_url = data.get("session_url", "")
        match = re.search(r"/classroom/([^/]+)/", session_url)
        if match:
            return match.group(1)
    except (json.JSONDecodeError, OSError):
        pass

    return None


def _get_course_image(course_dir: Path) -> str | None:
    """Get the course image URL.

    Priority:
    1. artwork_url from adapter_config.json (explicit URL)
    2. Derive from BP slug in metadata
    3. Fallback to directory name
    """
    course_slug = course_dir.name
    config = _load_course_config(course_dir)

    # 1. Use explicit artwork_url if available
    if config and config.get("artwork_url"):
        return config["artwork_url"]

    # 2. Get the real BP slug from metadata (may differ from directory name)
    bp_slug = _get_bp_slug_from_metadata(course_slug)
    if bp_slug:
        return _get_class_artwork_url(bp_slug)

    # 3. Fallback to directory name
    return _get_class_artwork_url(course_slug)


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
        # Sort numerically (1, 2, 3...) not alphabetically (1, 10, 11...)
        slide_files = list(slides_dir.glob("*.json"))
        slide_files.sort(key=lambda f: int(f.stem) if f.stem.isdigit() else f.stem)
        for slide_file in slide_files:
            session_id = slide_file.stem
            # Try to load slide file to get title/duration
            try:
                slide_data = json.loads(slide_file.read_text(encoding="utf-8"))
                # Try session_title first (production format), fall back to title (test format)
                title = slide_data.get("session_title") or slide_data.get("title", session_id)
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
      ],
      "theme": { "primary_color": "#...", "secondary_color": "#..." }
    }
    """
    slides_data, manifest = _load_slides_data(course_slug, session_id)

    # Build theme with derived artwork URLs and colors from config
    bp_dir = _get_bibleproject_dir()
    course_dir = bp_dir / course_slug
    config = _load_course_config(course_dir)

    # Artwork URLs - use config artwork_url if available, otherwise derive from slug
    class_artwork = _get_course_image(course_dir)
    # Module artwork would need module slug - use class artwork as fallback for now
    module_artwork = class_artwork

    # Colors come from config if available, otherwise use defaults
    color_data = {}
    if config:
        color_data = config.get("colors", {})

    theme = bp_schemas.PresentationTheme(
        artwork=bp_schemas.ThemeArtwork(
            class_=class_artwork,
            module=module_artwork,
            color=bp_schemas.ThemeColor(
                primary=color_data.get("primary", "#104366"),
                secondary=color_data.get("secondary", "#e24213"),
            ),
        )
    )

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

        # Extract variant and content, then flatten
        variant = resolved_slide.get("variant", "")
        content = resolved_slide.get("content", {})

        # Flatten: merge variant with content at top level
        # bp-slide expects {"variant": "title", "sessionName": "...", ...}
        # not {"variant": "title", "content": {"sessionName": "..."}}
        flattened_slide = {"variant": variant, **content}

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
                        stringArrayValue=anim.get("stringArrayValue"),
                        extraArg=anim.get("extraArg"),
                    )
                )

        presentation_slides.append(
            bp_schemas.PresentationSlide(
                startTime=timestamp,
                slide=flattened_slide,
                animations=animations,
            )
        )

    return bp_schemas.PresentationData(presentationSlides=presentation_slides, theme=theme)


@router.get(
    "/episodes/{course_slug}/{session_id}",
    summary="Get episode info for a session",
    response_model=media_schemas.EpisodeOut,
)
async def get_session_episode(
    course_slug: str, session_id: str
) -> media_schemas.EpisodeOut:  # type: ignore[valid-type]
    """Get episode information for a BibleProject session.

    Looks up the episode by its guid which follows the format:
    bibleproject:{course_slug}:{session_id}
    """
    guid = f"bibleproject:{course_slug}:{session_id}"

    try:
        episode = await media.Episode.objects.get(guid=guid)
        return episode
    except Exception:
        raise fastapi.HTTPException(
            status_code=404,
            detail=f"Episode not found for session: {course_slug}/{session_id}",
        )


def _get_visual_by_arc_id(arc_id: str) -> dict | None:
    """Search all course assets for a visual by arc_id."""
    bp_dir = _get_bibleproject_dir()
    if not bp_dir.exists():
        return None

    for course_dir in bp_dir.iterdir():
        if not course_dir.is_dir():
            continue
        assets_file = course_dir / "assets.json"
        if not assets_file.exists():
            continue
        try:
            data = json.loads(assets_file.read_text(encoding="utf-8"))
            for asset in data.get("assets", []):
                if asset.get("arc_id") == arc_id:
                    return asset
        except (json.JSONDecodeError, OSError):
            continue
    return None


@router.post(
    "/graphql",
    summary="GraphQL-like endpoint for bp-web-components visuals",
)
async def graphql_visuals(request: fastapi.Request) -> dict:
    """Handle GraphQL-like queries for visual assets.

    This endpoint mimics the BibleProject GraphQL API for the bp-web-components
    library to fetch visual data (diagrams, images, literary designs, etc.)
    """
    try:
        body = await request.json()
    except Exception:
        return {"data": None, "errors": [{"message": "Invalid JSON"}]}

    query_str = body.get("query", "")
    variables = body.get("variables", {})
    visual_id = variables.get("id", "")

    if not visual_id:
        return {"data": None, "errors": [{"message": "Missing id variable"}]}

    # Look up the asset
    asset = _get_visual_by_arc_id(visual_id)
    if not asset:
        return {"data": None, "errors": [{"message": f"Visual not found: {visual_id}"}]}

    asset_type = asset.get("asset_type", "")

    # Map asset to the expected GraphQL response format based on type
    if "literaryDesign" in query_str:
        return {
            "data": {
                "literaryDesign": {
                    "id": asset.get("arc_id"),
                    "title": asset.get("title"),
                    "reference": asset.get("reference"),
                    "caption": asset.get("caption"),
                    "usx": asset.get("usx"),
                    "html": asset.get("html"),
                }
            }
        }

    # Default visual response
    visual_data: dict = {
        "alt": asset.get("alt"),
        "caption": asset.get("caption"),
        "src": asset.get("src"),
        "title": asset.get("title"),
    }

    if asset_type == "table":
        visual_data = {
            "body": asset.get("body"),
            "minWidth": asset.get("minWidth"),
            "slideWidth": asset.get("slideWidth"),
        }
    elif asset_type == "video":
        visual_data["externalId"] = asset.get("externalId")
    elif asset_type == "macro_literary_design":
        # macro_literary_design stores JSON config in the 'html' field
        config = None
        html_data = asset.get("html")
        if html_data:
            try:
                config = json.loads(html_data) if isinstance(html_data, str) else html_data
            except (json.JSONDecodeError, TypeError):
                config = None
        visual_data = {
            "caption": asset.get("caption"),
            "config": config,
            "id": asset.get("arc_id"),
            "reference": asset.get("reference"),
            "title": asset.get("title"),
            "type": "macro_literary_design",
        }

    return {
        "data": {
            "visual": {
                "id": asset.get("arc_id"),
                "data": visual_data,
            }
        }
    }
