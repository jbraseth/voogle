# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Pytest-playwright fixture overrides for e2e tests."""

import os
from collections.abc import Generator
from typing import Any, Callable

import pytest
from e2e.shared.constants import (
    PLAYWRIGHT_ELEMENT_TIMEOUT_MS,
    PLAYWRIGHT_NAVIGATION_TIMEOUT_MS,
    TEST_ID_ATTRIBUTE,
    VIDEOS_DIR,
)
from playwright.sync_api import Browser, BrowserContext, Page, Playwright
from pytest import FixtureRequest


@pytest.fixture(scope="session", name="browser_context_args")
def fixture_browser_context_args(request: FixtureRequest) -> dict[str, Any]:
    video_option = request.config.getoption("--video")
    capture_video = video_option in ["on", "retain-on-failure"]

    context_args = {
        "ignore_https_errors": True,
        "viewport": {"width": 1280, "height": 720},
    }

    if capture_video:
        context_args.update({
            "record_video_dir": VIDEOS_DIR,
            "record_video_size": {"width": 1280, "height": 720},
        })

    return context_args


@pytest.fixture(scope="session", name="browser")
def fixture_browser(
    playwright: Playwright, launch_browser: Callable[..., Browser]
) -> Generator[Browser, None, None]:
    # Set custom test-id attribute for locators
    playwright.selectors.set_test_id_attribute(TEST_ID_ATTRIBUTE)

    browser = launch_browser()
    yield browser
    browser.close()


@pytest.fixture(name="context")
def fixture_context(
    request: FixtureRequest, browser: Browser, browser_context_args: dict[str, Any]
) -> Generator[BrowserContext, None, None]:
    tracing_option = request.config.getoption("--tracing")

    # Create context with configured args
    context = browser.new_context(**browser_context_args)

    # Set timeouts
    context.set_default_timeout(PLAYWRIGHT_ELEMENT_TIMEOUT_MS)
    context.set_default_navigation_timeout(PLAYWRIGHT_NAVIGATION_TIMEOUT_MS)

    # Grant permissions
    context.grant_permissions(["clipboard-read"])

    # Start tracing if enabled
    if tracing_option in ["on", "retain-on-failure"]:
        context.tracing.start(screenshots=True, snapshots=True, sources=True)

    yield context

    # Stop tracing and save if needed
    if tracing_option == "on" or (
        tracing_option == "retain-on-failure"
        and hasattr(request.node, "rep_call")
        and request.node.rep_call.failed
    ):
        trace_path = os.path.join(VIDEOS_DIR, f"{request.node.name}_trace.zip")
        context.tracing.stop(path=trace_path)
    elif tracing_option in ["on", "retain-on-failure"]:
        context.tracing.stop()

    context.close()


@pytest.fixture(name="page")
def fixture_page(context: BrowserContext) -> Generator[Page, None, None]:
    page = context.new_page()
    yield page
    page.close()
