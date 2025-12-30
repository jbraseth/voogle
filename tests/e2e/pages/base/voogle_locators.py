# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Common Voogle locators shared across page objects."""

from e2e.pages.base.page_object import PlaywrightPageObject
from e2e.pages.base.voogle_utils import VoogleUtils
from playwright.sync_api import Page


class VoogleLocators(PlaywrightPageObject, VoogleUtils):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.page = page
        self.header = PageHeader(page)


class PageHeader(PlaywrightPageObject):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.page = page
        self.locator = page.get_by_test_id("page-header")
        self.home_link = page.get_by_test_id("header-home-link")
        self.query_link = page.get_by_test_id("header-query-link")
        self.about_link = page.get_by_test_id("header-about-link")
        self.github_link = page.get_by_test_id("header-github-link")
