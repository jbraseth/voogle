# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for Fragment dataclass and ContentType enum."""
import pytest

from voogle.core import ContentType, Fragment

pytestmark = pytest.mark.unit


class TestContentType:
    """Tests for ContentType enum."""

    @pytest.mark.description("All content types have string values")
    def test_content_type_values(self) -> None:
        assert ContentType.AUDIO.value == "audio"
        assert ContentType.VIDEO.value == "video"
        assert ContentType.DOCUMENT.value == "document"
        assert ContentType.SLIDE.value == "slide"
        assert ContentType.TEXT.value == "text"

    @pytest.mark.description("ContentType can be created from string value")
    def test_content_type_from_value(self) -> None:
        assert ContentType("audio") == ContentType.AUDIO
        assert ContentType("video") == ContentType.VIDEO


class TestFragment:
    """Tests for Fragment dataclass."""

    @pytest.mark.description("Fragment with all required fields creates successfully")
    def test_create_with_required_fields(self) -> None:
        fragment = Fragment(
            id="test-123",
            text="Hello world",
            score=0.9,
            source_id="src-1",
            source_type=ContentType.AUDIO,
            location=None,
            deep_link=None,
            metadata={},
        )
        assert fragment.id == "test-123"
        assert fragment.text == "Hello world"
        assert fragment.score == 0.9
        assert fragment.source_id == "src-1"
        assert fragment.source_type == ContentType.AUDIO
        assert fragment.location is None
        assert fragment.deep_link is None
        assert fragment.metadata == {}

    @pytest.mark.description("Fragment with optional fields creates successfully")
    def test_create_with_optional_fields(self) -> None:
        fragment = Fragment(
            id="test-456",
            text="Sample text",
            score=0.75,
            source_id="src-2",
            source_type=ContentType.VIDEO,
            location={"start": 10.5, "end": 20.0},
            deep_link="https://example.com/video?t=10",
            metadata={"episode": "ep-001", "chapter": 3},
        )
        assert fragment.location == {"start": 10.5, "end": 20.0}
        assert fragment.deep_link == "https://example.com/video?t=10"
        assert fragment.metadata == {"episode": "ep-001", "chapter": 3}

    @pytest.mark.description("Fragment defaults metadata to empty dict")
    def test_default_metadata(self) -> None:
        fragment = Fragment(
            id="test",
            text="text",
            score=0.5,
            source_id="src",
            source_type=ContentType.TEXT,
            location=None,
            deep_link=None,
        )
        assert fragment.metadata == {}

    @pytest.mark.description("Fragment with empty id raises ValueError")
    def test_empty_id_raises(self) -> None:
        with pytest.raises(ValueError, match="id cannot be empty"):
            Fragment(
                id="",
                text="Hello",
                score=0.5,
                source_id="src",
                source_type=ContentType.AUDIO,
                location=None,
                deep_link=None,
                metadata={},
            )

    @pytest.mark.description("Fragment with empty text raises ValueError")
    def test_empty_text_raises(self) -> None:
        with pytest.raises(ValueError, match="text cannot be empty"):
            Fragment(
                id="test",
                text="",
                score=0.5,
                source_id="src",
                source_type=ContentType.AUDIO,
                location=None,
                deep_link=None,
                metadata={},
            )

    @pytest.mark.description("Fragment with empty source_id raises ValueError")
    def test_empty_source_id_raises(self) -> None:
        with pytest.raises(ValueError, match="source_id cannot be empty"):
            Fragment(
                id="test",
                text="Hello",
                score=0.5,
                source_id="",
                source_type=ContentType.AUDIO,
                location=None,
                deep_link=None,
                metadata={},
            )

    @pytest.mark.description("Fragment with score below 0 raises ValueError")
    def test_score_below_zero_raises(self) -> None:
        with pytest.raises(ValueError, match="score must be between 0.0 and 1.0"):
            Fragment(
                id="test",
                text="Hello",
                score=-0.1,
                source_id="src",
                source_type=ContentType.AUDIO,
                location=None,
                deep_link=None,
                metadata={},
            )

    @pytest.mark.description("Fragment with score above 1 raises ValueError")
    def test_score_above_one_raises(self) -> None:
        with pytest.raises(ValueError, match="score must be between 0.0 and 1.0"):
            Fragment(
                id="test",
                text="Hello",
                score=1.1,
                source_id="src",
                source_type=ContentType.AUDIO,
                location=None,
                deep_link=None,
                metadata={},
            )

    @pytest.mark.description("Fragment with boundary scores (0.0 and 1.0) succeeds")
    def test_boundary_scores(self) -> None:
        fragment_zero = Fragment(
            id="test",
            text="Hello",
            score=0.0,
            source_id="src",
            source_type=ContentType.AUDIO,
            location=None,
            deep_link=None,
            metadata={},
        )
        assert fragment_zero.score == 0.0

        fragment_one = Fragment(
            id="test",
            text="Hello",
            score=1.0,
            source_id="src",
            source_type=ContentType.AUDIO,
            location=None,
            deep_link=None,
            metadata={},
        )
        assert fragment_one.score == 1.0

    @pytest.mark.description("Fragment is immutable (frozen dataclass)")
    def test_immutable(self) -> None:
        fragment = Fragment(
            id="test",
            text="Hello",
            score=0.5,
            source_id="src",
            source_type=ContentType.AUDIO,
            location=None,
            deep_link=None,
            metadata={},
        )
        with pytest.raises(Exception):  # FrozenInstanceError
            fragment.text = "Changed"  # type: ignore[misc]

    @pytest.mark.description("Fragment has string representation")
    def test_str_representation(self) -> None:
        fragment = Fragment(
            id="test",
            text="hello",
            score=0.9,
            source_id="src1",
            source_type=ContentType.AUDIO,
            location=None,
            deep_link=None,
            metadata={},
        )
        result = str(fragment)
        assert "test" in result
        assert "hello" in result

    @pytest.mark.description("Fragment supports all ContentType values")
    def test_all_content_types(self) -> None:
        for content_type in ContentType:
            fragment = Fragment(
                id=f"test-{content_type.value}",
                text="Sample",
                score=0.5,
                source_id="src",
                source_type=content_type,
                location=None,
                deep_link=None,
                metadata={},
            )
            assert fragment.source_type == content_type
