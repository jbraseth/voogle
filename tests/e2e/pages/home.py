# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Home page object for Voogle application."""

from e2e.pages.base.episode_locators import EpisodesLocators
from e2e.pages.base.voogle_locators import VoogleLocators
from playwright.sync_api import Page


class HomeLocators(VoogleLocators, EpisodesLocators):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.page = page

    def navigate(self) -> None:
        self.header.home_link.click()


class Home(HomeLocators):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.query_box = self.page.get_by_test_id("home-query-input")
        self.search_btn = self.page.get_by_test_id("home-search-button")
