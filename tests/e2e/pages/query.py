# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Query page object for search functionality."""

from e2e.pages.base.voogle_locators import VoogleLocators
from playwright.sync_api import Page


class QueryLocators(VoogleLocators):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.page = page

    def navigate(self) -> None:
        self.header.query_link.click()


class Query(QueryLocators):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.query_box = self.page.get_by_test_id("query-input")
        self.search_btn = self.page.get_by_test_id("search-button")
