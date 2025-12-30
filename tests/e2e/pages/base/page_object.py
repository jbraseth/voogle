# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Base page object class for Playwright tests."""

from playwright.sync_api import Page


class PlaywrightPageObject:
    def __init__(self, page: Page, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.page = page
