# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Regression tests for RSS feed parsing edge cases.

These tests lock in the fix for single-item RSS parsing (dict vs list edge case).
When an RSS feed contains exactly one <item>, xmltodict returns a dict instead
of a list, which can break iteration if not handled properly.
"""

from pathlib import Path

import pytest
import xmltodict

from voogle.collection import feed


pytestmark = pytest.mark.unit

FIXTURES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "rss"


def _parse_feed_items(xml_content: str) -> list[dict]:
    """Parse RSS XML and return items as a normalized list.

    This helper mimics how read_episodes() should handle items,
    ensuring dict-to-list normalization for single-item feeds.
    """
    parsed = xmltodict.parse(xml_content)
    items = parsed["rss"]["channel"].get("item", [])

    # Normalize: xmltodict returns dict for single item, list for multiple
    if isinstance(items, dict):
        items = [items]

    return items


class TestSingleItemRssParsing:
    """Regression tests for single-item RSS feed parsing."""

    @pytest.mark.description("Single-item RSS feed returns exactly one episode")
    def test_single_item_feed_parses_successfully(self) -> None:
        """When RSS has exactly one <item>, it should parse as a list of one."""
        xml_content = (FIXTURES_DIR / "single_item.xml").read_text()
        items = _parse_feed_items(xml_content)

        assert isinstance(items, list), "Items must be a list, not dict"
        assert len(items) == 1, "Should have exactly one episode"
        assert items[0]["title"] == "The Only Episode"
        assert items[0]["guid"] == "ep-001"

    @pytest.mark.description("Multi-item RSS feed returns all episodes")
    def test_multi_item_feed_parses_all_episodes(self) -> None:
        """Standard case: multiple <item> elements parse as a list."""
        xml_content = (FIXTURES_DIR / "multi_item.xml").read_text()
        items = _parse_feed_items(xml_content)

        assert isinstance(items, list), "Items must be a list"
        assert len(items) == 3, "Should have three episodes"
        assert items[0]["title"] == "Episode One"
        assert items[1]["title"] == "Episode Two"
        assert items[2]["title"] == "Episode Three"

    @pytest.mark.description("Empty RSS feed returns empty list")
    def test_empty_feed_returns_empty_list(self) -> None:
        """When RSS has no <item> elements, return empty list gracefully."""
        xml_content = (FIXTURES_DIR / "empty_feed.xml").read_text()
        items = _parse_feed_items(xml_content)

        assert isinstance(items, list), "Items must be a list"
        assert len(items) == 0, "Should have zero episodes"


class TestXmltodictBehavior:
    """Document xmltodict's dict vs list behavior to catch future regressions."""

    @pytest.mark.description("xmltodict returns dict for single item (raw behavior)")
    def test_xmltodict_single_item_is_dict(self) -> None:
        """Verify xmltodict's raw behavior that we're protecting against."""
        xml_content = (FIXTURES_DIR / "single_item.xml").read_text()
        parsed = xmltodict.parse(xml_content)
        raw_items = parsed["rss"]["channel"]["item"]

        # This is the bug: xmltodict returns a dict for single item
        assert isinstance(raw_items, dict), (
            "xmltodict should return dict for single item - "
            "if this fails, xmltodict behavior changed"
        )

    @pytest.mark.description("xmltodict returns list for multiple items")
    def test_xmltodict_multi_item_is_list(self) -> None:
        """Verify xmltodict returns list when multiple items exist."""
        xml_content = (FIXTURES_DIR / "multi_item.xml").read_text()
        parsed = xmltodict.parse(xml_content)
        raw_items = parsed["rss"]["channel"]["item"]

        assert isinstance(raw_items, list), "xmltodict should return list for multiple items"


class TestNormalizeItems:
    """Tests for feed._normalize_items() function (the actual fix)."""

    @pytest.mark.description("Single item dict is normalized to list")
    def test_normalize_single_item_dict(self) -> None:
        """When xmltodict returns a dict, normalize to list of one."""
        channel_info = {"item": {"title": "Episode One", "guid": "ep-001"}}
        result = feed._normalize_items(channel_info)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["title"] == "Episode One"

    @pytest.mark.description("Multiple items list is unchanged")
    def test_normalize_multi_item_list(self) -> None:
        """When xmltodict returns a list, keep it as-is."""
        channel_info = {"item": [{"title": "Ep 1"}, {"title": "Ep 2"}]}
        result = feed._normalize_items(channel_info)

        assert isinstance(result, list)
        assert len(result) == 2

    @pytest.mark.description("Missing items returns empty list")
    def test_normalize_missing_items(self) -> None:
        """When no items key exists, return empty list."""
        channel_info = {"title": "Empty Channel"}
        result = feed._normalize_items(channel_info)

        assert isinstance(result, list)
        assert len(result) == 0


class TestEpisodeDurationParsing:
    """Tests for episode duration parsing edge cases."""

    @pytest.mark.description("Duration in HH:MM:SS format parses correctly")
    def test_duration_hhmmss(self) -> None:
        """Duration like '1:05:45' should parse to seconds."""
        assert feed._episode_duration("1:05:45") == 3945  # 1*3600 + 5*60 + 45

    @pytest.mark.description("Duration in MM:SS format parses correctly")
    def test_duration_mmss(self) -> None:
        """Duration like '30:00' should parse to seconds."""
        assert feed._episode_duration("30:00") == 1800  # 30*60 + 0

    @pytest.mark.description("Duration as integer seconds parses correctly")
    def test_duration_integer(self) -> None:
        """Duration like '1800' (raw seconds) should parse."""
        assert feed._episode_duration("1800") == 1800

    @pytest.mark.description("None duration returns -1")
    def test_duration_none(self) -> None:
        """Missing duration should return -1."""
        assert feed._episode_duration(None) == -1


class TestEpisodeGuidParsing:
    """Tests for episode GUID parsing edge cases."""

    @pytest.mark.description("String GUID returns as-is")
    def test_guid_string(self) -> None:
        """Simple string GUID should return unchanged."""
        assert feed._episode_guid("ep-001") == "ep-001"

    @pytest.mark.description("Dict GUID extracts #text value")
    def test_guid_dict(self) -> None:
        """GUID as dict with #text should extract the text."""
        assert feed._episode_guid({"#text": "ep-002", "@isPermaLink": "false"}) == "ep-002"
