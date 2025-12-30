# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""About page object for Voogle application."""

from e2e.pages.base.episode_locators import EpisodesLocators
from e2e.pages.base.voogle_locators import VoogleLocators
from playwright.sync_api import Page


class AboutLocators(VoogleLocators, EpisodesLocators):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.page = page

    def navigate(self) -> None:
        self.header.about_link.click()


class About(AboutLocators):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
