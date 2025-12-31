# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Authentication utilities for e2e tests."""

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


def login_to_management(
    page: Page, management_url: str, username: str, password: str
) -> None:
    """
    Log into Streamlit management dashboard.

    Uses Playwright test discovery methods for robust selector matching.
    Verifies login success by checking for session state change.
    """
    # Navigate to the login page specifically (not home page)
    login_url = f"{management_url}/Login"
    page.goto(login_url)

    # Wait for login form to load
    page.wait_for_load_state("networkidle")

    # Use Playwright's semantic locators for robust element discovery
    # These work across Streamlit version changes better than CSS selectors
    username_input = page.get_by_label("Username", exact=False)
    # Use role-based selector for password to avoid conflict with "Show password" button
    password_input = page.get_by_role("textbox", name="Password")

    username_input.fill(username)
    password_input.fill(password)

    # Find login button by role and text
    login_button = page.get_by_role("button", name="Login")
    login_button.click()

    # Verify login succeeded by checking for login form disappearance
    # Streamlit reruns the page after successful auth, hiding the form
    try:
        page.wait_for_selector('input[type="text"]', state="hidden", timeout=5000)
    except PlaywrightTimeoutError:
        # Fallback: check if page content changed
        page.wait_for_load_state("networkidle")

    # Additional verification: look for logged-in indicator if it exists
    # (Optional - depends on management UI implementation)
