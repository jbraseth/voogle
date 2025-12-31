# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Playwright compatibility shim.

Allows code to import from playwright without failing when it's not installed.
Import this module early (before any playwright imports) to register the shim.
"""

from compat.playwright.playwright_mock import PlaywrightMock
from compat.playwright.playwright_wrapper import PlaywrightWrapper

# Flag indicating whether real playwright is available
PLAYWRIGHT_AVAILABLE = False

# Attempt to initialize real playwright, fall back to mock
try:
    PlaywrightWrapper()
    PLAYWRIGHT_AVAILABLE = True
except ModuleNotFoundError:
    PlaywrightMock()
    PLAYWRIGHT_AVAILABLE = False
