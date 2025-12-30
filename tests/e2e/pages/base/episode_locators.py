# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Episode-related locators for page objects."""

from e2e.pages.base.page_object import PlaywrightPageObject
from playwright.sync_api import Page


class EpisodesLocators(PlaywrightPageObject):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.page = page
        self.episodes = EpisodesLink(page)


class EpisodesLink(PlaywrightPageObject):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.page = page
        self.locator = page.get_by_role("link", name="episodes")

    def navigate(self) -> None:
        self.locator.click()
