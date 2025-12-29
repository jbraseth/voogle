# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Test constants for e2e tests."""

import os
from pathlib import Path

# Timeouts
PLAYWRIGHT_WAIT_DEFAULT_MS = 15000
PLAYWRIGHT_ELEMENT_TIMEOUT_MS = 30000  # 30 seconds for element operations
PLAYWRIGHT_NAVIGATION_TIMEOUT_MS = 60000  # 60 seconds for page navigation

# Test ID attribute (custom data-* attribute for locators)
TEST_ID_ATTRIBUTE = "data-testid"

# Paths
VIDEOS_DIR = os.getenv("PLAYWRIGHT_VIDEOS_DIR", str(Path(__file__).parent.parent.parent / "videos"))

# Authentication
ADMIN_USERNAME = "voogle-admin"
ADMIN_PASSWORD = "*audio*search*engine"
