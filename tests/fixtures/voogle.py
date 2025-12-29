# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Voogle-specific fixtures for e2e tests."""

from collections.abc import Generator

import pytest
from playwright.sync_api import BrowserContext, Page


@pytest.fixture(name="management_page")
def fixture_management_page(
    context: BrowserContext,
    streamlit_url: str,
    voogle_credentials: tuple[str, str],
) -> Generator[Page, None, None]:
    from e2e.shared.auth import login_to_management

    page = context.new_page()
    username, password = voogle_credentials

    # Navigate to management dashboard and login
    login_to_management(page, streamlit_url, username, password)

    yield page
    page.close()
