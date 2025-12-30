# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Query page object for search functionality."""

import re

from e2e.pages.base.voogle_locators import VoogleLocators
from playwright.sync_api import Locator, Page


class QueryLocators(VoogleLocators):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.page = page

    def navigate(self) -> None:
        self.header.query_link.click()


class Query(QueryLocators):
    """Page object for the search/query page with methods for E2E testing."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.query_box = self.page.get_by_test_id("query-input")
        self.search_btn = self.page.get_by_test_id("search-button")

    def fill_query(self, text: str) -> None:
        """Enter search text into the query input box."""
        self.query_box.fill(text)

    def submit_search(self) -> None:
        """Submit the search by clicking the search button."""
        self.search_btn.click()

    def search(self, text: str) -> None:
        """Convenience method: fill query and submit search."""
        self.fill_query(text)
        self.submit_search()

    def wait_for_results(self, timeout: int = 30000) -> None:
        """Wait for search results to appear on the page."""
        # Wait for at least one result card to be visible
        self.page.locator('[data-testid^="query-result-"]').first.wait_for(
            state="visible", timeout=timeout
        )
        self.page.wait_for_load_state("networkidle")

    def get_result_cards(self) -> list[Locator]:
        """Get all result card locators."""
        return self.page.locator('[data-testid^="query-result-"]').all()

    def get_unique_channel_ids(self) -> list[str]:
        """Extract unique channel IDs from the result cards.

        Returns list of channel IDs (extracted from data-testid="query-result-{id}").
        """
        unique_channels: list[str] = []
        seen: set[str] = set()

        for card in self.get_result_cards():
            testid = card.get_attribute("data-testid")
            if testid:
                # Extract channel ID from "query-result-{channel_id}"
                match = re.search(r"query-result-(.+)$", testid)
                if match:
                    channel_id = match.group(1)
                    if channel_id not in seen:
                        seen.add(channel_id)
                        unique_channels.append(channel_id)

        return unique_channels

    def get_play_button(self, channel_id: str) -> Locator:
        """Get the first play button for a specific channel.

        Note: Multiple results from the same channel have the same test ID.
        We only need to click one to verify playback works for that channel.
        """
        return self.page.get_by_test_id(f"play-button-{channel_id}").first

    def click_play(self, channel_id: str) -> None:
        """Click the play button for a specific channel."""
        self.get_play_button(channel_id).click()

    def get_audio_player(self) -> Locator:
        """Get the audio player element."""
        return self.page.get_by_test_id("audio-player-active")

    def wait_for_player(self, timeout: int = 10000) -> None:
        """Wait for the audio player to appear."""
        self.get_audio_player().wait_for(state="visible", timeout=timeout)

    def is_player_visible(self) -> bool:
        """Check if the audio player is currently visible."""
        return self.get_audio_player().is_visible()
