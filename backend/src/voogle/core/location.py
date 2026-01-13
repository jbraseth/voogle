# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Polymorphic Location type system for deep-linking to content sources.

This module defines a hierarchy of Location types that represent specific
positions within different media formats (audio, PDF, web, code, slides, images).
Each location type implements a to_deep_link method for generating navigable URLs.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Literal
from urllib.parse import urlencode


class LocationType(str, Enum):
    """Discriminator enum for Location type serialization."""

    TIMESTAMP = "timestamp"
    PAGE_BBOX = "page_bbox"
    ELEMENT_SELECTOR = "element_selector"
    CODE = "code"
    SLIDE = "slide"
    IMAGE_REGION = "image_region"


class Location(ABC):
    """Abstract base class for all location types.

    Each subclass represents a specific position within a content source
    and can generate a deep link URL to navigate directly to that position.
    """

    @property
    @abstractmethod
    def location_type(self) -> LocationType:
        """Return the discriminator for this location type."""

    @abstractmethod
    def to_deep_link(self, base_url: str) -> str:
        """Generate a deep link URL for this location.

        Args:
            base_url: The base URL of the content source.

        Returns:
            A URL with appropriate fragment or query parameters
            to navigate directly to this location.
        """


@dataclass(frozen=True)
class TimestampLocation(Location):
    """Location within audio/video content defined by time range.

    Attributes:
        start_time: Start position in seconds.
        end_time: Optional end position in seconds.
    """

    start_time: float
    end_time: float | None = None

    def __post_init__(self) -> None:
        if self.start_time < 0:
            raise ValueError("start_time must be >= 0")
        if self.end_time is not None and self.end_time < self.start_time:
            raise ValueError("end_time must be >= start_time")

    @property
    def location_type(self) -> Literal[LocationType.TIMESTAMP]:
        return LocationType.TIMESTAMP

    def to_deep_link(self, base_url: str) -> str:
        """Generate a deep link with timestamp fragment.

        Uses the Media Fragments URI standard (t=start,end).
        """
        t_param = f"t={self.start_time:.1f}"
        if self.end_time is not None:
            t_param = f"t={self.start_time:.1f},{self.end_time:.1f}"

        separator = "&" if "?" in base_url else "?"
        if "#" in base_url:
            base, fragment = base_url.rsplit("#", 1)
            return f"{base}#{t_param}&{fragment}"
        return f"{base_url}{separator}{t_param}"


@dataclass(frozen=True)
class PageBboxLocation(Location):
    """Location within a PDF document defined by page and bounding box.

    Attributes:
        page: 1-indexed page number.
        x: Left edge of bounding box (0-100, percentage of page width).
        y: Top edge of bounding box (0-100, percentage of page height).
        width: Width of bounding box (0-100, percentage of page width).
        height: Height of bounding box (0-100, percentage of page height).
    """

    page: int
    x: float = 0.0
    y: float = 0.0
    width: float = 100.0
    height: float = 100.0

    def __post_init__(self) -> None:
        if self.page < 1:
            raise ValueError("page must be >= 1")
        for name, val in [("x", self.x), ("y", self.y), ("width", self.width), ("height", self.height)]:
            if val < 0 or val > 100:
                raise ValueError(f"{name} must be between 0 and 100")

    @property
    def location_type(self) -> Literal[LocationType.PAGE_BBOX]:
        return LocationType.PAGE_BBOX

    def to_deep_link(self, base_url: str) -> str:
        """Generate a deep link with PDF page fragment.

        Uses the PDF Open Parameters standard (#page=N).
        """
        fragment = f"page={self.page}"
        if not (self.x == 0 and self.y == 0 and self.width == 100 and self.height == 100):
            fragment += f"&viewrect={self.x:.0f},{self.y:.0f},{self.width:.0f},{self.height:.0f}"
        return f"{base_url}#{fragment}"


@dataclass(frozen=True)
class ElementSelectorLocation(Location):
    """Location within a web page defined by CSS/XPath selector.

    Attributes:
        selector: CSS selector or XPath expression.
        selector_type: Type of selector ('css' or 'xpath').
        text_match: Optional text to highlight within the element.
    """

    selector: str
    selector_type: Literal["css", "xpath"] = "css"
    text_match: str | None = None

    def __post_init__(self) -> None:
        if not self.selector:
            raise ValueError("selector must not be empty")

    @property
    def location_type(self) -> Literal[LocationType.ELEMENT_SELECTOR]:
        return LocationType.ELEMENT_SELECTOR

    def to_deep_link(self, base_url: str) -> str:
        """Generate a deep link with text fragment or element ID.

        Uses Text Fragments standard for text highlighting.
        """
        if self.text_match:
            encoded_text = self.text_match.replace(" ", "%20")
            return f"{base_url}#:~:text={encoded_text}"
        if self.selector.startswith("#") and self.selector_type == "css":
            return f"{base_url}{self.selector}"
        params = urlencode({"selector": self.selector, "type": self.selector_type})
        return f"{base_url}?{params}"


@dataclass(frozen=True)
class CodeLocation(Location):
    """Location within source code defined by file path and line range.

    Attributes:
        file_path: Path to the source file.
        start_line: 1-indexed starting line number.
        end_line: Optional 1-indexed ending line number.
        column: Optional column number.
        git_ref: Optional git commit SHA for reproducible code locations.
    """

    file_path: str
    start_line: int
    end_line: int | None = None
    column: int | None = None
    git_ref: str | None = None

    def __post_init__(self) -> None:
        if not self.file_path:
            raise ValueError("file_path must not be empty")
        if self.start_line < 1:
            raise ValueError("start_line must be >= 1")
        if self.end_line is not None and self.end_line < self.start_line:
            raise ValueError("end_line must be >= start_line")
        if self.column is not None and self.column < 1:
            raise ValueError("column must be >= 1")

    @property
    def location_type(self) -> Literal[LocationType.CODE]:
        return LocationType.CODE

    def to_deep_link(self, base_url: str) -> str:
        """Generate a deep link with line number fragment and optional git ref.

        Uses GitHub-style line references (#L10-L20) and blob/ref paths.

        Args:
            base_url: The base URL of the code repository (e.g., https://github.com/org/repo).

        Returns:
            URL with optional ref and line fragment (e.g., /blob/abc123/file.py#L10-L20).
        """
        fragment = f"L{self.start_line}"
        if self.end_line is not None and self.end_line != self.start_line:
            fragment += f"-L{self.end_line}"

        if self.git_ref:
            return f"{base_url}/blob/{self.git_ref}/{self.file_path}#{fragment}"
        return f"{base_url}/{self.file_path}#{fragment}"


@dataclass(frozen=True)
class SlideLocation(Location):
    """Location within a slide presentation.

    Attributes:
        slide_number: 1-indexed slide number.
        element_id: Optional ID of specific element on the slide.
    """

    slide_number: int
    element_id: str | None = None

    def __post_init__(self) -> None:
        if self.slide_number < 1:
            raise ValueError("slide_number must be >= 1")

    @property
    def location_type(self) -> Literal[LocationType.SLIDE]:
        return LocationType.SLIDE

    def to_deep_link(self, base_url: str) -> str:
        """Generate a deep link to a specific slide.

        Uses standard slide= query parameter.
        """
        separator = "&" if "?" in base_url else "?"
        url = f"{base_url}{separator}slide={self.slide_number}"
        if self.element_id:
            url += f"#{self.element_id}"
        return url


@dataclass(frozen=True)
class ImageRegionLocation(Location):
    """Location within an image defined by a rectangular region.

    Attributes:
        x: Left edge of region (0-100, percentage of image width).
        y: Top edge of region (0-100, percentage of image height).
        width: Width of region (0-100, percentage of image width).
        height: Height of region (0-100, percentage of image height).
    """

    x: float
    y: float
    width: float
    height: float

    def __post_init__(self) -> None:
        for name, val in [("x", self.x), ("y", self.y), ("width", self.width), ("height", self.height)]:
            if val < 0 or val > 100:
                raise ValueError(f"{name} must be between 0 and 100")

    @property
    def location_type(self) -> Literal[LocationType.IMAGE_REGION]:
        return LocationType.IMAGE_REGION

    def to_deep_link(self, base_url: str) -> str:
        """Generate a deep link with IIIF-style region parameters.

        Uses xywh= fragment for image region specification.
        """
        xywh = f"xywh=percent:{self.x:.1f},{self.y:.1f},{self.width:.1f},{self.height:.1f}"
        return f"{base_url}#{xywh}"
