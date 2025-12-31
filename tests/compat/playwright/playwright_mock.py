# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Playwright mock for environments without the real Playwright installed.

Provides MagicMock versions of typical Playwright objects so that imports
don't fail when playwright isn't installed.
"""

from unittest import mock


class PlaywrightMock:
    """Fallback for environments without the real Playwright installed.

    Provides MagicMock versions of typical Playwright objects. This allows
    test modules to import playwright types without crashing.
    """

    # MagicMock placeholders for common Playwright objects
    Browser = mock.MagicMock()
    BrowserContext = mock.MagicMock()
    expect = mock.MagicMock()
    Locator = mock.MagicMock()
    Page = mock.MagicMock()
    playwright = mock.MagicMock()

    class PlaywrightTimeoutError(Exception):
        """Mock for playwright timeout error."""
