# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for Location type hierarchy."""

import pytest

from voogle.core.location import (
    CodeLocation,
    ElementSelectorLocation,
    ImageRegionLocation,
    Location,
    LocationType,
    PageBboxLocation,
    SlideLocation,
    TimestampLocation,
)

pytestmark = pytest.mark.unit


class TestTimestampLocation:
    """Tests for TimestampLocation."""

    @pytest.mark.description("Creates valid timestamp location with start only")
    def test_start_time_only(self) -> None:
        loc = TimestampLocation(start_time=10.5)
        assert loc.start_time == 10.5
        assert loc.end_time is None
        assert loc.location_type == LocationType.TIMESTAMP

    @pytest.mark.description("Creates valid timestamp location with start and end")
    def test_start_and_end_time(self) -> None:
        loc = TimestampLocation(start_time=10.5, end_time=20.0)
        assert loc.start_time == 10.5
        assert loc.end_time == 20.0

    @pytest.mark.description("Generates deep link with start time only")
    def test_deep_link_start_only(self) -> None:
        loc = TimestampLocation(start_time=10.5)
        url = loc.to_deep_link("https://example.com/audio")
        assert url == "https://example.com/audio?t=10.5"

    @pytest.mark.description("Generates deep link with time range")
    def test_deep_link_with_range(self) -> None:
        loc = TimestampLocation(start_time=10.5, end_time=20.0)
        url = loc.to_deep_link("https://example.com/audio")
        assert url == "https://example.com/audio?t=10.5,20.0"

    @pytest.mark.description("Appends to existing query params")
    def test_deep_link_with_existing_params(self) -> None:
        loc = TimestampLocation(start_time=10.5)
        url = loc.to_deep_link("https://example.com/audio?id=123")
        assert url == "https://example.com/audio?id=123&t=10.5"

    @pytest.mark.description("Negative start_time raises ValueError")
    def test_negative_start_time(self) -> None:
        with pytest.raises(ValueError, match="start_time must be >= 0"):
            TimestampLocation(start_time=-1.0)

    @pytest.mark.description("end_time before start_time raises ValueError")
    def test_end_before_start(self) -> None:
        with pytest.raises(ValueError, match="end_time must be >= start_time"):
            TimestampLocation(start_time=20.0, end_time=10.0)

    @pytest.mark.description("Location is frozen (immutable)")
    def test_immutable(self) -> None:
        loc = TimestampLocation(start_time=10.5)
        with pytest.raises(Exception):
            loc.start_time = 20.0  # type: ignore[misc]


class TestPageBboxLocation:
    """Tests for PageBboxLocation."""

    @pytest.mark.description("Creates valid page location with page only")
    def test_page_only(self) -> None:
        loc = PageBboxLocation(page=5)
        assert loc.page == 5
        assert loc.x == 0.0
        assert loc.y == 0.0
        assert loc.width == 100.0
        assert loc.height == 100.0
        assert loc.location_type == LocationType.PAGE_BBOX

    @pytest.mark.description("Creates valid page location with bbox")
    def test_with_bbox(self) -> None:
        loc = PageBboxLocation(page=3, x=10.0, y=20.0, width=50.0, height=30.0)
        assert loc.page == 3
        assert loc.x == 10.0
        assert loc.y == 20.0
        assert loc.width == 50.0
        assert loc.height == 30.0

    @pytest.mark.description("Generates deep link with page only")
    def test_deep_link_page_only(self) -> None:
        loc = PageBboxLocation(page=5)
        url = loc.to_deep_link("https://example.com/doc.pdf")
        assert url == "https://example.com/doc.pdf#page=5"

    @pytest.mark.description("Generates deep link with viewrect")
    def test_deep_link_with_viewrect(self) -> None:
        loc = PageBboxLocation(page=3, x=10.0, y=20.0, width=50.0, height=30.0)
        url = loc.to_deep_link("https://example.com/doc.pdf")
        assert url == "https://example.com/doc.pdf#page=3&viewrect=10,20,50,30"

    @pytest.mark.description("Invalid page number raises ValueError")
    def test_invalid_page(self) -> None:
        with pytest.raises(ValueError, match="page must be >= 1"):
            PageBboxLocation(page=0)

    @pytest.mark.description("Invalid bbox values raise ValueError")
    def test_invalid_bbox(self) -> None:
        with pytest.raises(ValueError, match="x must be between 0 and 100"):
            PageBboxLocation(page=1, x=-1.0)
        with pytest.raises(ValueError, match="width must be between 0 and 100"):
            PageBboxLocation(page=1, width=101.0)


class TestElementSelectorLocation:
    """Tests for ElementSelectorLocation."""

    @pytest.mark.description("Creates valid selector location")
    def test_css_selector(self) -> None:
        loc = ElementSelectorLocation(selector=".content p:first-child")
        assert loc.selector == ".content p:first-child"
        assert loc.selector_type == "css"
        assert loc.text_match is None
        assert loc.location_type == LocationType.ELEMENT_SELECTOR

    @pytest.mark.description("Creates valid xpath selector location")
    def test_xpath_selector(self) -> None:
        loc = ElementSelectorLocation(selector="//div[@id='main']", selector_type="xpath")
        assert loc.selector == "//div[@id='main']"
        assert loc.selector_type == "xpath"

    @pytest.mark.description("Generates deep link with text fragment")
    def test_deep_link_with_text_match(self) -> None:
        loc = ElementSelectorLocation(selector=".content", text_match="hello world")
        url = loc.to_deep_link("https://example.com/page")
        assert url == "https://example.com/page#:~:text=hello%20world"

    @pytest.mark.description("Generates deep link with ID selector")
    def test_deep_link_id_selector(self) -> None:
        loc = ElementSelectorLocation(selector="#section-1")
        url = loc.to_deep_link("https://example.com/page")
        assert url == "https://example.com/page#section-1"

    @pytest.mark.description("Generates deep link with generic selector")
    def test_deep_link_generic_selector(self) -> None:
        loc = ElementSelectorLocation(selector=".content p")
        url = loc.to_deep_link("https://example.com/page")
        assert "selector=.content+p" in url or "selector=.content%20p" in url

    @pytest.mark.description("Empty selector raises ValueError")
    def test_empty_selector(self) -> None:
        with pytest.raises(ValueError, match="selector must not be empty"):
            ElementSelectorLocation(selector="")


class TestCodeLocation:
    """Tests for CodeLocation."""

    @pytest.mark.description("Creates valid code location with line only")
    def test_line_only(self) -> None:
        loc = CodeLocation(file_path="src/main.py", start_line=42)
        assert loc.file_path == "src/main.py"
        assert loc.start_line == 42
        assert loc.end_line is None
        assert loc.column is None
        assert loc.location_type == LocationType.CODE

    @pytest.mark.description("Creates valid code location with line range")
    def test_line_range(self) -> None:
        loc = CodeLocation(file_path="src/main.py", start_line=10, end_line=20)
        assert loc.start_line == 10
        assert loc.end_line == 20

    @pytest.mark.description("Generates deep link with single line")
    def test_deep_link_single_line(self) -> None:
        loc = CodeLocation(file_path="src/main.py", start_line=42)
        url = loc.to_deep_link("https://github.com/user/repo/blob/main")
        assert url == "https://github.com/user/repo/blob/main/src/main.py#L42"

    @pytest.mark.description("Generates deep link with line range")
    def test_deep_link_line_range(self) -> None:
        loc = CodeLocation(file_path="src/main.py", start_line=10, end_line=20)
        url = loc.to_deep_link("https://github.com/user/repo/blob/main")
        assert url == "https://github.com/user/repo/blob/main/src/main.py#L10-L20"

    @pytest.mark.description("Empty file_path raises ValueError")
    def test_empty_file_path(self) -> None:
        with pytest.raises(ValueError, match="file_path must not be empty"):
            CodeLocation(file_path="", start_line=1)

    @pytest.mark.description("Invalid line numbers raise ValueError")
    def test_invalid_line_numbers(self) -> None:
        with pytest.raises(ValueError, match="start_line must be >= 1"):
            CodeLocation(file_path="main.py", start_line=0)
        with pytest.raises(ValueError, match="end_line must be >= start_line"):
            CodeLocation(file_path="main.py", start_line=20, end_line=10)


class TestSlideLocation:
    """Tests for SlideLocation."""

    @pytest.mark.description("Creates valid slide location")
    def test_slide_only(self) -> None:
        loc = SlideLocation(slide_number=5)
        assert loc.slide_number == 5
        assert loc.element_id is None
        assert loc.location_type == LocationType.SLIDE

    @pytest.mark.description("Creates valid slide location with element")
    def test_with_element_id(self) -> None:
        loc = SlideLocation(slide_number=3, element_id="title-box")
        assert loc.slide_number == 3
        assert loc.element_id == "title-box"

    @pytest.mark.description("Generates deep link with slide number")
    def test_deep_link_slide_only(self) -> None:
        loc = SlideLocation(slide_number=5)
        url = loc.to_deep_link("https://docs.google.com/presentation/d/abc")
        assert url == "https://docs.google.com/presentation/d/abc?slide=5"

    @pytest.mark.description("Generates deep link with element ID")
    def test_deep_link_with_element(self) -> None:
        loc = SlideLocation(slide_number=3, element_id="title-box")
        url = loc.to_deep_link("https://example.com/slides")
        assert url == "https://example.com/slides?slide=3#title-box"

    @pytest.mark.description("Invalid slide_number raises ValueError")
    def test_invalid_slide_number(self) -> None:
        with pytest.raises(ValueError, match="slide_number must be >= 1"):
            SlideLocation(slide_number=0)


class TestImageRegionLocation:
    """Tests for ImageRegionLocation."""

    @pytest.mark.description("Creates valid image region location")
    def test_valid_region(self) -> None:
        loc = ImageRegionLocation(x=10.0, y=20.0, width=30.0, height=40.0)
        assert loc.x == 10.0
        assert loc.y == 20.0
        assert loc.width == 30.0
        assert loc.height == 40.0
        assert loc.location_type == LocationType.IMAGE_REGION

    @pytest.mark.description("Generates deep link with region")
    def test_deep_link(self) -> None:
        loc = ImageRegionLocation(x=10.0, y=20.0, width=30.0, height=40.0)
        url = loc.to_deep_link("https://example.com/image.jpg")
        assert url == "https://example.com/image.jpg#xywh=percent:10.0,20.0,30.0,40.0"

    @pytest.mark.description("Invalid region values raise ValueError")
    def test_invalid_region(self) -> None:
        with pytest.raises(ValueError, match="x must be between 0 and 100"):
            ImageRegionLocation(x=-1.0, y=0.0, width=50.0, height=50.0)
        with pytest.raises(ValueError, match="height must be between 0 and 100"):
            ImageRegionLocation(x=0.0, y=0.0, width=50.0, height=150.0)


class TestLocationPolymorphism:
    """Tests for Location abstract base class behavior."""

    @pytest.mark.description("All location types are instances of Location")
    def test_isinstance(self) -> None:
        locations = [
            TimestampLocation(start_time=10.0),
            PageBboxLocation(page=1),
            ElementSelectorLocation(selector=".test"),
            CodeLocation(file_path="test.py", start_line=1),
            SlideLocation(slide_number=1),
            ImageRegionLocation(x=0.0, y=0.0, width=100.0, height=100.0),
        ]
        for loc in locations:
            assert isinstance(loc, Location)

    @pytest.mark.description("Each location type has unique discriminator")
    def test_unique_discriminators(self) -> None:
        locations = [
            TimestampLocation(start_time=10.0),
            PageBboxLocation(page=1),
            ElementSelectorLocation(selector=".test"),
            CodeLocation(file_path="test.py", start_line=1),
            SlideLocation(slide_number=1),
            ImageRegionLocation(x=0.0, y=0.0, width=100.0, height=100.0),
        ]
        types = [loc.location_type for loc in locations]
        assert len(types) == len(set(types))
