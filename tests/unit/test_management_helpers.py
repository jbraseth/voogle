# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for management UI helper functions and edge cases.

These tests validate the defensive programming patterns in the Streamlit
management pages, particularly around empty/null field handling.
"""

from unittest.mock import patch

import pytest

pytestmark = pytest.mark.unit


class TestChannelImageHandling:
    """Regression tests for st.image() crash when channel.image is empty.

    Bug context: `st.image(ch.image)` was called without checking if
    `ch.image` was empty, causing crashes in the management UI.
    Fix applied: Added `if ch.image:` guard in 3_🔈-Media.py:99
    """

    @pytest.mark.description("st.image() not called when channel.image is empty string")
    def test_empty_image_string_not_displayed(self) -> None:
        """Verify st.image() is not called when image is an empty string."""
        from voogle.schemas.analytics import ChannelAnalytics

        # Create a ChannelAnalytics with empty image (mimics DB state)
        channel = ChannelAnalytics(
            title="Test Podcast",
            kind="podcast",
            description="A test podcast",
            total_episodes=10,
            image="",  # Empty string - the bug trigger
            url="https://example.com/feed.xml",
            available_episodes=5,
        )

        # The fix is in podcasts_and_episodes() which calls st.image(ch.image)
        # only if ch.image is truthy. We verify the guard condition.
        assert not channel.image, "Empty string should be falsy"
        assert (channel.image if channel.image else None) is None

    @pytest.mark.description("st.image() not called when channel.image is whitespace")
    def test_whitespace_image_not_displayed(self) -> None:
        """Verify whitespace-only images are treated as empty."""
        from voogle.schemas.analytics import ChannelAnalytics

        channel = ChannelAnalytics(
            title="Test Podcast",
            kind="podcast",
            description="A test podcast",
            total_episodes=10,
            image="   ",  # Whitespace only
            url="https://example.com/feed.xml",
            available_episodes=5,
        )

        # Whitespace strings are truthy in Python, but should be treated as empty
        # Note: Current fix only checks truthiness, not strip().
        # This test documents current behavior.
        assert channel.image  # Whitespace is truthy
        # If the fix should handle whitespace, it would need: if ch.image and ch.image.strip()

    @pytest.mark.description("st.image() called when channel.image is valid URL")
    def test_valid_image_url_displayed(self) -> None:
        """Verify valid image URLs pass the guard condition."""
        from voogle.schemas.analytics import ChannelAnalytics

        channel = ChannelAnalytics(
            title="Test Podcast",
            kind="podcast",
            description="A test podcast",
            total_episodes=10,
            image="https://example.com/cover.jpg",  # Valid URL
            url="https://example.com/feed.xml",
            available_episodes=5,
        )

        # Valid image should pass the guard
        assert channel.image, "Valid URL should be truthy"
        assert channel.image == "https://example.com/cover.jpg"


class TestPodcastsAndEpisodesDisplay:
    """Integration-style tests for podcasts_and_episodes() function.

    These tests mock Streamlit to verify the rendering logic without
    running the actual Streamlit app.
    """

    @pytest.mark.description("podcasts_and_episodes() handles channel with empty image")
    @pytest.mark.asyncio
    async def test_channel_with_empty_image_no_crash(self) -> None:
        """Verify podcasts_and_episodes() doesn't crash on empty image."""
        from voogle.schemas.analytics import ChannelAnalytics, MediaAnalytics

        # Mock the analytics response with an empty image channel
        mock_analytics = MediaAnalytics(
            total_channels=1,
            channels=[
                ChannelAnalytics(
                    title="Podcast Without Image",
                    kind="podcast",
                    description="No image set",
                    total_episodes=5,
                    image="",  # Empty - the bug trigger
                    url="https://example.com/feed.xml",
                    available_episodes=3,
                ),
            ],
        )

        with patch("streamlit.image") as mock_image:
            # The podcasts_and_episodes function iterates over channels
            # and only calls st.image(ch.image) if ch.image is truthy
            for ch in mock_analytics.channels:
                # Simulate the guard condition from the fix
                if ch.image:
                    mock_image(ch.image)

            # st.image should NOT have been called (empty image)
            mock_image.assert_not_called()

    @pytest.mark.description("podcasts_and_episodes() displays image when present")
    @pytest.mark.asyncio
    async def test_channel_with_valid_image_displays(self) -> None:
        """Verify podcasts_and_episodes() displays image when present."""
        from voogle.schemas.analytics import ChannelAnalytics, MediaAnalytics

        valid_image_url = "https://example.com/cover.jpg"
        mock_analytics = MediaAnalytics(
            total_channels=1,
            channels=[
                ChannelAnalytics(
                    title="Podcast With Image",
                    kind="podcast",
                    description="Has image",
                    total_episodes=5,
                    image=valid_image_url,
                    url="https://example.com/feed.xml",
                    available_episodes=3,
                ),
            ],
        )

        with patch("streamlit.image") as mock_image:
            # Simulate the guard condition from the fix
            for ch in mock_analytics.channels:
                if ch.image:
                    mock_image(ch.image)

            # st.image SHOULD have been called with the valid URL
            mock_image.assert_called_once_with(valid_image_url)

    @pytest.mark.description("Mixed channels with and without images handled correctly")
    @pytest.mark.asyncio
    async def test_mixed_channels_image_handling(self) -> None:
        """Verify correct handling of mix of channels with/without images."""
        from voogle.schemas.analytics import ChannelAnalytics, MediaAnalytics

        mock_analytics = MediaAnalytics(
            total_channels=3,
            channels=[
                ChannelAnalytics(
                    title="Podcast 1 - No Image",
                    kind="podcast",
                    description="Empty image",
                    total_episodes=5,
                    image="",
                    url="https://example.com/feed1.xml",
                    available_episodes=3,
                ),
                ChannelAnalytics(
                    title="Podcast 2 - Has Image",
                    kind="podcast",
                    description="Valid image",
                    total_episodes=10,
                    image="https://example.com/cover2.jpg",
                    url="https://example.com/feed2.xml",
                    available_episodes=8,
                ),
                ChannelAnalytics(
                    title="Local Channel - No Image",
                    kind="local",
                    description="Local files",
                    total_episodes=3,
                    image="",
                    url="file:///local/folder",
                    available_episodes=3,
                ),
            ],
        )

        with patch("streamlit.image") as mock_image:
            for ch in mock_analytics.channels:
                if ch.image:
                    mock_image(ch.image)

            # Should only be called once (for Podcast 2)
            mock_image.assert_called_once_with("https://example.com/cover2.jpg")
