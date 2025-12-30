# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Main Voogle page object aggregating all page components."""

from e2e.pages.about import About
from e2e.pages.base.voogle_locators import VoogleLocators
from e2e.pages.home import Home
from e2e.pages.query import Query
from playwright.sync_api import Page


class Voogle(VoogleLocators):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.about = About(page)
        self.home = Home(page)
        self.query = Query(page)
