# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for feed module - PDF detection and resource parsing."""

import pytest
from voogle.collection.feed import (
    RESOURCE_MIME_TYPES,
    ResourceData,
    _is_resource_item,
)

pytestmark = pytest.mark.unit


@pytest.mark.description("PDF MIME type is in RESOURCE_MIME_TYPES set")
def test_resource_mime_types_contains_pdf() -> None:
    """Verify PDF is recognized as a resource type."""
    assert "application/pdf" in RESOURCE_MIME_TYPES


@pytest.mark.description("_is_resource_item returns True for PDF enclosures")
def test_is_resource_item_pdf() -> None:
    """Test PDF items are identified as resources."""
    pdf_item = {
        "title": "Teacher Notes",
        "enclosure": {"@url": "https://example.com/notes.pdf", "@type": "application/pdf"},
    }
    assert _is_resource_item(pdf_item) is True


@pytest.mark.description("_is_resource_item returns False for audio enclosures")
def test_is_resource_item_audio() -> None:
    """Test audio items are not identified as resources."""
    audio_item = {
        "title": "Episode 1",
        "enclosure": {"@url": "https://example.com/ep1.mp3", "@type": "audio/mpeg"},
    }
    assert _is_resource_item(audio_item) is False


@pytest.mark.description("_is_resource_item returns False when no enclosure")
def test_is_resource_item_no_enclosure() -> None:
    """Test items without enclosure are not resources."""
    no_enclosure_item = {"title": "Title Only"}
    assert _is_resource_item(no_enclosure_item) is False


@pytest.mark.description("_is_resource_item returns False for video enclosures")
def test_is_resource_item_video() -> None:
    """Test video items are not identified as resources."""
    video_item = {
        "title": "Main Video",
        "enclosure": {"@url": "https://stream.mux.com/abc.m3u8", "@type": "video/mp4"},
    }
    assert _is_resource_item(video_item) is False


@pytest.mark.description("ResourceData dataclass stores all fields correctly")
def test_resource_data_dataclass() -> None:
    """Test ResourceData dataclass creation."""
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    data = ResourceData(
        guid="test-guid",
        title="Test Title",
        description="Test description",
        original_url="https://example.com/test.pdf",
        mime_type="application/pdf",
        date=now,
    )
    assert data.guid == "test-guid"
    assert data.title == "Test Title"
    assert data.description == "Test description"
    assert data.original_url == "https://example.com/test.pdf"
    assert data.mime_type == "application/pdf"
    assert data.date == now
