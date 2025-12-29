# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Authentication utilities for e2e tests."""

from playwright.sync_api import Page


def login_to_management(page: Page, management_url: str, username: str, password: str) -> None:
    page.goto(management_url)

    # Streamlit apps typically use input fields for authentication
    # Adjust selectors based on actual Streamlit auth implementation
    username_input = page.locator('input[type="text"]').first
    password_input = page.locator('input[type="password"]').first

    username_input.fill(username)
    password_input.fill(password)

    # Submit form - adjust selector based on actual button
    login_button = page.locator('button:has-text("Login")').or_(
        page.locator('button[type="submit"]')
    )
    login_button.click()

    # Wait for successful login (adjust based on post-login indicator)
    page.wait_for_load_state("networkidle")
