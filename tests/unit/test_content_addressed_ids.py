# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for content-addressed fragment ID generation."""
import pytest

from voogle.core.fragment import (
    detect_collision,
    detect_content_change,
    generate_fragment_id,
)

pytestmark = pytest.mark.unit


class TestGenerateFragmentId:
    """Tests for generate_fragment_id function."""

    @pytest.mark.description("Generated ID is 32 hex characters (128 bits)")
    def test_id_length_and_format(self) -> None:
        result = generate_fragment_id("src1", "hello world", {})
        assert len(result) == 32
        assert all(c in "0123456789abcdef" for c in result)

    @pytest.mark.description("Same inputs produce same ID (deterministic)")
    def test_deterministic(self) -> None:
        id1 = generate_fragment_id("src1", "hello world", {"page": 1})
        id2 = generate_fragment_id("src1", "hello world", {"page": 1})
        assert id1 == id2

    @pytest.mark.description("Different source_id produces different ID")
    def test_different_source_id(self) -> None:
        id1 = generate_fragment_id("src1", "hello world", {})
        id2 = generate_fragment_id("src2", "hello world", {})
        assert id1 != id2

    @pytest.mark.description("Different content produces different ID")
    def test_different_content(self) -> None:
        id1 = generate_fragment_id("src1", "hello world", {})
        id2 = generate_fragment_id("src1", "hello universe", {})
        assert id1 != id2

    @pytest.mark.description("Different location produces different ID")
    def test_different_location(self) -> None:
        id1 = generate_fragment_id("src1", "hello world", {"page": 1})
        id2 = generate_fragment_id("src1", "hello world", {"page": 2})
        assert id1 != id2

    @pytest.mark.description("None location is equivalent to empty dict")
    def test_none_location_equals_empty_dict(self) -> None:
        id1 = generate_fragment_id("src1", "hello world", None)
        id2 = generate_fragment_id("src1", "hello world", {})
        assert id1 == id2

    @pytest.mark.description("Location dict key order doesn't affect ID")
    def test_location_key_order_independent(self) -> None:
        id1 = generate_fragment_id("src1", "hello", {"a": 1, "b": 2})
        id2 = generate_fragment_id("src1", "hello", {"b": 2, "a": 1})
        assert id1 == id2

    @pytest.mark.description("Empty source_id raises ValueError")
    def test_empty_source_id_raises(self) -> None:
        with pytest.raises(ValueError, match="source_id cannot be empty"):
            generate_fragment_id("", "hello world", {})

    @pytest.mark.description("Empty content raises ValueError")
    def test_empty_content_raises(self) -> None:
        with pytest.raises(ValueError, match="content cannot be empty"):
            generate_fragment_id("src1", "", {})

    @pytest.mark.description("Complex location dict produces stable ID")
    def test_complex_location(self) -> None:
        location = {
            "start_time": 10.5,
            "end_time": 20.0,
            "page": 3,
            "metadata": {"chapter": "intro"},
        }
        id1 = generate_fragment_id("src1", "hello", location)
        id2 = generate_fragment_id("src1", "hello", location)
        assert id1 == id2
        assert len(id1) == 32

    @pytest.mark.description("Unicode content produces valid ID")
    def test_unicode_content(self) -> None:
        result = generate_fragment_id("src1", "Cześć świecie 🌍", {})
        assert len(result) == 32
        assert all(c in "0123456789abcdef" for c in result)


class TestDetectCollision:
    """Tests for detect_collision function."""

    @pytest.mark.description("No collision when IDs differ")
    def test_no_collision_different_ids(self) -> None:
        id1 = generate_fragment_id("src1", "hello", {})
        id2 = generate_fragment_id("src1", "world", {})
        result = detect_collision(
            id1, id2, "src1", "hello", {}, "src1", "world", {}
        )
        assert result is False

    @pytest.mark.description("No collision when IDs match and inputs identical")
    def test_no_collision_same_inputs(self) -> None:
        frag_id = generate_fragment_id("src1", "hello", {"page": 1})
        result = detect_collision(
            frag_id, frag_id,
            "src1", "hello", {"page": 1},
            "src1", "hello", {"page": 1},
        )
        assert result is False

    @pytest.mark.description("Collision detected when IDs match but content differs")
    def test_collision_detected_different_content(self) -> None:
        # Simulate a hash collision by using same ID with different inputs
        fake_collision_id = "a" * 32
        result = detect_collision(
            fake_collision_id, fake_collision_id,
            "src1", "hello", {},
            "src1", "world", {},
        )
        assert result is True

    @pytest.mark.description("Collision detected when IDs match but source_id differs")
    def test_collision_detected_different_source(self) -> None:
        fake_collision_id = "b" * 32
        result = detect_collision(
            fake_collision_id, fake_collision_id,
            "src1", "hello", {},
            "src2", "hello", {},
        )
        assert result is True

    @pytest.mark.description("Collision detected when IDs match but location differs")
    def test_collision_detected_different_location(self) -> None:
        fake_collision_id = "c" * 32
        result = detect_collision(
            fake_collision_id, fake_collision_id,
            "src1", "hello", {"page": 1},
            "src1", "hello", {"page": 2},
        )
        assert result is True

    @pytest.mark.description("None and empty dict locations are considered equal")
    def test_none_equals_empty_dict(self) -> None:
        frag_id = generate_fragment_id("src1", "hello", {})
        result = detect_collision(
            frag_id, frag_id,
            "src1", "hello", None,
            "src1", "hello", {},
        )
        assert result is False


class TestDetectContentChange:
    """Tests for detect_content_change function."""

    @pytest.mark.description("No change detected for identical content")
    def test_no_change_same_content(self) -> None:
        old_id = generate_fragment_id("src1", "hello world", {"page": 1})
        result = detect_content_change(old_id, "src1", "hello world", {"page": 1})
        assert result is False

    @pytest.mark.description("Change detected when content differs")
    def test_change_detected_different_content(self) -> None:
        old_id = generate_fragment_id("src1", "hello world", {})
        result = detect_content_change(old_id, "src1", "hello universe", {})
        assert result is True

    @pytest.mark.description("Change detected when source_id differs")
    def test_change_detected_different_source(self) -> None:
        old_id = generate_fragment_id("src1", "hello world", {})
        result = detect_content_change(old_id, "src2", "hello world", {})
        assert result is True

    @pytest.mark.description("Change detected when location differs")
    def test_change_detected_different_location(self) -> None:
        old_id = generate_fragment_id("src1", "hello world", {"page": 1})
        result = detect_content_change(old_id, "src1", "hello world", {"page": 2})
        assert result is True

    @pytest.mark.description("None and empty dict locations are equivalent")
    def test_none_location_equivalent(self) -> None:
        old_id = generate_fragment_id("src1", "hello world", {})
        result = detect_content_change(old_id, "src1", "hello world", None)
        assert result is False

    @pytest.mark.description("Minor whitespace change detected")
    def test_whitespace_change_detected(self) -> None:
        old_id = generate_fragment_id("src1", "hello world", {})
        result = detect_content_change(old_id, "src1", "hello  world", {})
        assert result is True
