# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""BibleProject API schemas."""

from pydantic import BaseModel, Field


class CourseListItem(BaseModel):
    """Summary of a course for listing."""

    slug: str
    title: str
    session_count: int
    image: str | None = None


class SessionSummary(BaseModel):
    """Summary of a session within a course."""

    id: str
    title: str
    duration: float | None = None


class CourseDetail(BaseModel):
    """Detailed information about a course."""

    slug: str
    title: str
    description: str | None = None
    sessions: list[SessionSummary]


class ResolvedAsset(BaseModel):
    """A resolved asset with its CDN URL and metadata."""

    src: str
    alt: str = ""
    caption: str = ""
    title: str = ""
    asset_type: str = "unknown"


class Slide(BaseModel):
    """A single slide with resolved assets."""

    slide_index: int
    content: dict
    resolved_assets: dict[str, ResolvedAsset] = {}


class SessionSlides(BaseModel):
    """All slides for a session."""

    session_id: str
    total_slides: int
    slides: list[Slide]


class SlideAnimation(BaseModel):
    """Animation to apply to a slide at a specific time."""

    startTime: str | int  # "MM:SS" format or seconds
    variant: str
    stringValue: str | None = None
    stringArrayValue: list[str] | None = None  # For animations targeting multiple elements
    extraArg: str | None = None


class PresentationSlide(BaseModel):
    """A slide in the format expected by bp-slide-presentation."""

    startTime: int  # timestamp in seconds
    slide: dict  # Flattened: {"variant": "...", "sessionName": "...", ...}
    animations: list[SlideAnimation] = []


class ThemeColor(BaseModel):
    """Color values for the theme."""

    primary: str = "#104366"  # Default dark blue
    secondary: str = "#e24213"  # Default orange


class ThemeArtwork(BaseModel):
    """Artwork and colors for the presentation theme.

    Matches bp-slide-presentation's expected theme.artwork structure.
    """

    class_: str | None = Field(default=None, alias="class", serialization_alias="class")
    module: str | None = None  # Module artwork URL (1:1 square)
    color: ThemeColor = ThemeColor()

    model_config = {"populate_by_name": True}


class PresentationTheme(BaseModel):
    """Theme for the presentation matching bp-slide-presentation's expected structure."""

    artwork: ThemeArtwork = ThemeArtwork()


class PresentationData(BaseModel):
    """Data format expected by bp-slide-presentation web component."""

    presentationSlides: list[PresentationSlide]
    theme: PresentationTheme | None = None
