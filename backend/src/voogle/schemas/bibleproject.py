# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""BibleProject API schemas."""

from pydantic import BaseModel


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
    extraArg: str | None = None


class SlideContent(BaseModel):
    """The slide content with variant and data."""

    variant: str
    content: dict


class PresentationSlide(BaseModel):
    """A slide in the format expected by bp-slide-presentation."""

    startTime: int  # timestamp in seconds
    slide: SlideContent
    animations: list[SlideAnimation] = []


class PresentationData(BaseModel):
    """Data format expected by bp-slide-presentation web component."""

    presentationSlides: list[PresentationSlide]
