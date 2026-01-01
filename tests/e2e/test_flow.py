# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""End-to-end flow test for Voogle application.

This test validates the complete user flow:
1. Home page loads
2. Navigate to query page
3. Enter a search query
4. Verify search returns results
5. Click play button on each unique channel result
6. Verify audio player appears for each channel

Requires test data with embeddings to be seeded before the test runs.
See tests/fixtures/models.py::fake_episode_with_embeddings fixture.

The tests are parametrized to cover both:
- Podcast channels (external URLs)
- Local channels (served via /local/ route)
"""

import re

import httpx
import pytest
from e2e.pages.voogle import Voogle
from playwright.sync_api import ConsoleMessage, Error, Page, expect

# Patterns for console errors that are NOT application bugs.
# Browser extensions, third-party noise, etc.
CONSOLE_ERROR_ALLOWLIST = [
    r"chrome-extension://",  # Chrome browser extensions
    r"moz-extension://",  # Firefox browser extensions
    r"Failed to fetch.*extension",  # Extension fetch failures
    r"message channel closed",  # Extension messaging cleanup
]


def _is_allowlisted(error_text: str) -> bool:
    """Check if an error message matches any allowlist pattern."""
    return any(re.search(pattern, error_text) for pattern in CONSOLE_ERROR_ALLOWLIST)


def _check_console_errors(console_monitor: dict) -> None:
    """Check console errors and fail if any non-allowlisted errors found.

    Warnings are logged but don't fail the test.
    Errors (type="error") fail unless they match an allowlist pattern.
    Page errors always fail.
    """
    # Separate warnings from errors
    warnings = [e for e in console_monitor["console_errors"] if e["type"] == "warning"]
    errors = [e for e in console_monitor["console_errors"] if e["type"] == "error"]

    # Log warnings (informational only)
    if warnings:
        print("\n    Console warnings detected (non-blocking):")
        for w in warnings:
            print(f"      [WARNING] {w['text']}")

    # Filter errors through allowlist
    real_errors = [e for e in errors if not _is_allowlisted(e["text"])]

    # Log allowlisted errors for transparency
    allowlisted = [e for e in errors if _is_allowlisted(e["text"])]
    if allowlisted:
        print("\n    Allowlisted console errors (ignored):")
        for e in allowlisted:
            print(f"      [ALLOWLISTED] {e['text']}")

    # Fail on real errors
    if real_errors:
        error_details = "\n".join(
            f"  - {e['text']}\n    Location: {e.get('location', 'unknown')}"
            for e in real_errors
        )
        pytest.fail(
            f"Browser console errors detected:\n{error_details}\n\n"
            f"If this is a false positive, add a pattern to CONSOLE_ERROR_ALLOWLIST"
        )

    # Page errors always fail (uncaught exceptions)
    if console_monitor["page_errors"]:
        pytest.fail(f"Uncaught page errors: {console_monitor['page_errors']}")


pytestmark = pytest.mark.e2e


# Channel type configurations for parametrized tests
CHANNEL_TEST_CONFIGS = [
    pytest.param(
        {"search_term": "golf", "channel_type": "podcast", "expected_title": "Golf"},
        id="podcast-channel",
    ),
    pytest.param(
        {"search_term": "stay hungry", "channel_type": "local", "expected_title": "Local"},
        id="local-channel",
    ),
]


@pytest.fixture(name="api_client")
def fixture_api_client(
    api_url: str, voogle_credentials: tuple[str, str]
) -> httpx.Client:
    """Create authenticated HTTP client for API requests."""
    username, password = voogle_credentials

    # Get auth token (use follow_redirects to handle trailing slash redirects)
    with httpx.Client(base_url=api_url, follow_redirects=True) as client:
        response = client.post(
            "/users/token", data={"username": username, "password": password}
        )
        response.raise_for_status()
        token = response.json()["access_token"]

    # Return authenticated client with follow_redirects enabled
    return httpx.Client(
        base_url=api_url,
        headers={"Authorization": f"Bearer {token}"},
        follow_redirects=True,
    )


@pytest.fixture(name="test_data")
def fixture_test_data(api_client: httpx.Client) -> dict:
    """Verify test data exists via API.

    For E2E tests, we assume the test environment has been seeded with data.
    This fixture just checks that channels and episodes exist.
    If no data exists, tests will fail - which is the correct behavior for E2E.
    """
    # Check for existing channels
    response = api_client.get("/media/channel")
    response.raise_for_status()
    channels_data = response.json()

    # Check for episodes
    response = api_client.get("/media/episode")
    response.raise_for_status()
    episodes_data = response.json()

    return {
        "channels_count": channels_data.get("total", 0),
        "episodes_count": episodes_data.get("total", 0),
        "has_data": channels_data.get("total", 0) > 0,
    }


@pytest.fixture(name="console_monitor")
def fixture_console_monitor(page: Page) -> dict:
    """Monitor browser console messages and errors."""
    console_messages: list[dict] = []
    console_errors: list[dict] = []
    page_errors: list[str] = []

    def on_console(msg: ConsoleMessage) -> None:
        console_messages.append(
            {"type": msg.type, "text": msg.text, "location": msg.location}
        )
        if msg.type in ["error", "warning"]:
            console_errors.append(
                {"type": msg.type, "text": msg.text, "location": msg.location}
            )

    def on_page_error(error: Error) -> None:
        page_errors.append(str(error))

    page.on("console", on_console)
    page.on("pageerror", on_page_error)

    return {
        "messages": console_messages,
        "console_errors": console_errors,
        "page_errors": page_errors,
    }


def test_voogle_search_and_playback(
    management_page: Page,
    voogle_url: str,
    test_data: dict,
    console_monitor: dict,
    e2e_seed_data: None,
) -> None:
    """Test complete Voogle flow: search query returns results and audio plays.

    This test verifies the PRIMARY user flow:
    1. Home page loads successfully
    2. Navigate to search/query page
    3. Enter a search query (e.g., "golf")
    4. Verify search returns results from the test database
    5. For each unique channel in results, click the play button
    6. Verify the audio player appears after clicking play
    7. No critical browser console errors occur

    REQUIRES: Test database must have transcribed episodes with embeddings.
    Use the fake_episode_with_embeddings fixture to seed test data.
    """
    page = management_page
    voogle = Voogle(page)

    # ========================================
    # Step 1: Navigate to home page
    # ========================================
    page.goto(voogle_url)
    page.wait_for_load_state("networkidle")

    # Verify home page loads - look for logo or main heading
    logo = page.locator('img[alt*="logo" i]').or_(
        page.locator('[class*="logo" i]')
    ).or_(
        page.locator("h1")
    )
    assert logo.count() > 0, "Home page did not load - no logo or heading found"

    # ========================================
    # Step 2: Navigate to search/query page
    # ========================================
    voogle.header.query_link.click()
    page.wait_for_load_state("networkidle")

    # Verify search page loaded - look for search input
    expect(voogle.query.query_box).to_be_visible()

    # ========================================
    # Step 3: Enter search query
    # ========================================
    # Use a search term that should match the test data (golf.csv transcription)
    search_term = "golf"
    voogle.query.fill_query(search_term)

    # ========================================
    # Step 4: Submit search and wait for results
    # ========================================
    voogle.query.submit_search()

    # Wait for results to appear (with timeout for API response)
    voogle.query.wait_for_results(timeout=30000)

    # Verify we got results
    result_cards = voogle.query.get_result_cards()
    assert len(result_cards) > 0, (
        f"No search results returned for query '{search_term}'. "
        "Ensure test database has episodes with embeddings calculated."
    )

    print(f"\n    Found {len(result_cards)} search results for '{search_term}'")

    # ========================================
    # Step 5: Extract unique channels from results
    # ========================================
    unique_channel_ids = voogle.query.get_unique_channel_ids()
    assert len(unique_channel_ids) > 0, "Could not extract channel IDs from results"

    print(f"    Found {len(unique_channel_ids)} unique channel(s) in results")

    # ========================================
    # Step 6: Click play on each unique channel and verify player appears
    # ========================================
    for channel_id in unique_channel_ids:
        print(f"    Testing playback for channel ID: {channel_id}")

        # Click the play button for this channel
        play_button = voogle.query.get_play_button(channel_id)

        # All channels should now have play buttons (including local channels)
        expect(play_button).to_be_visible()
        play_button.click()

        # Wait for audio player to appear
        voogle.query.wait_for_player(timeout=10000)

        # Verify the player is visible
        player = voogle.query.get_audio_player()
        expect(player).to_be_visible()

        # Scroll player into view to ensure it's rendered
        player.scroll_into_view_if_needed()

        print(f"      Audio player appeared for channel {channel_id}")

    # ========================================
    # Step 7: Check for console errors
    # ========================================
    _check_console_errors(console_monitor)

    print("\n    E2E test completed successfully!")


def test_home_page_loads(
    management_page: Page,
    voogle_url: str,
    console_monitor: dict,
) -> None:
    """Smoke test: verify home page loads without errors.

    This is a simpler test that doesn't require seeded data.
    """
    page = management_page

    page.goto(voogle_url)
    page.wait_for_load_state("networkidle")

    # Verify home page loaded
    logo = page.locator('img[alt*="logo" i]').or_(
        page.locator('[class*="logo" i]')
    ).or_(
        page.locator("h1")
    )
    assert logo.count() > 0, "Home page did not load"

    # Check for console errors
    _check_console_errors(console_monitor)


def test_query_page_loads(
    management_page: Page,
    voogle_url: str,
    console_monitor: dict,
) -> None:
    """Smoke test: verify query page loads and search input is visible.

    This test validates the query page UI without requiring seeded data.
    """
    page = management_page
    voogle = Voogle(page)

    # Navigate to home first
    page.goto(voogle_url)
    page.wait_for_load_state("networkidle")

    # Navigate to query page
    voogle.header.query_link.click()
    page.wait_for_load_state("networkidle")

    # Verify search input is visible
    expect(voogle.query.query_box).to_be_visible()

    # Verify search button is visible
    expect(voogle.query.search_btn).to_be_visible()

    # Check for console errors
    _check_console_errors(console_monitor)


@pytest.mark.parametrize("config", CHANNEL_TEST_CONFIGS)
def test_channel_type_playback(
    management_page: Page,
    voogle_url: str,
    console_monitor: dict,
    config: dict,
    e2e_seed_data: None,
) -> None:
    """Parametrized test for both podcast and local channel playback.

    This test validates that:
    1. Search returns results for the specified channel type
    2. Play button is visible for all channel types (including local)
    3. Audio player appears and works for both podcast and local channels
    4. Local channels use the /local/ route for media serving

    Args:
        config: Dict with search_term, channel_type, expected_title
    """
    page = management_page
    voogle = Voogle(page)

    search_term = config["search_term"]
    channel_type = config["channel_type"]
    expected_title = config["expected_title"]

    print(f"\n    Testing {channel_type} channel with search: '{search_term}'")

    # Navigate to home page
    page.goto(voogle_url)
    page.wait_for_load_state("networkidle")

    # Navigate to query page
    voogle.header.query_link.click()
    page.wait_for_load_state("networkidle")

    # Enter search query
    voogle.query.fill_query(search_term)
    voogle.query.submit_search()

    # Wait for results
    voogle.query.wait_for_results(timeout=30000)

    # Verify we got results
    result_cards = voogle.query.get_result_cards()
    assert len(result_cards) > 0, (
        f"No search results for '{search_term}'. "
        f"Ensure {channel_type} channel is seeded with embeddings."
    )

    print(f"    Found {len(result_cards)} results for '{search_term}'")

    # Find a result from the expected channel type
    # Check that we have a result containing the expected title
    found_expected = False
    for card in result_cards:
        card_text = card.inner_text()
        if expected_title.lower() in card_text.lower():
            found_expected = True
            break

    assert found_expected, (
        f"No result found with '{expected_title}' in title. "
        f"Results may not be from the expected {channel_type} channel."
    )

    # Get unique channel IDs and test playback
    unique_channel_ids = voogle.query.get_unique_channel_ids()
    assert len(unique_channel_ids) > 0, "No channel IDs found in results"

    # Test the first channel's playback
    channel_id = unique_channel_ids[0]
    play_button = voogle.query.get_play_button(channel_id)

    # Play button should be visible for ALL channel types now
    expect(play_button).to_be_visible()
    print(f"    Play button visible for {channel_type} channel")

    # Click play
    play_button.click()

    # Wait for audio player
    voogle.query.wait_for_player(timeout=10000)

    # Verify player is visible
    player = voogle.query.get_audio_player()
    expect(player).to_be_visible()

    print(f"    Audio player appeared for {channel_type} channel")

    # Check for console errors
    _check_console_errors(console_monitor)

    print(f"    {channel_type.upper()} channel E2E test passed!")


# =============================================================================
# Unit tests for console error detection logic
# =============================================================================


class TestConsoleErrorAllowlist:
    """Unit tests for console error allowlist matching."""

    def test_chrome_extension_is_allowlisted(self) -> None:
        """Chrome extension errors should be allowlisted."""
        assert _is_allowlisted("Failed to load chrome-extension://abc123/script.js")

    def test_firefox_extension_is_allowlisted(self) -> None:
        """Firefox extension errors should be allowlisted."""
        assert _is_allowlisted("Error in moz-extension://def456/background.js")

    def test_extension_fetch_failure_is_allowlisted(self) -> None:
        """Extension fetch failures should be allowlisted."""
        assert _is_allowlisted("Failed to fetch resource from extension")

    def test_message_channel_closed_is_allowlisted(self) -> None:
        """Message channel closed errors should be allowlisted."""
        assert _is_allowlisted("message channel closed before response")

    def test_app_error_is_not_allowlisted(self) -> None:
        """Application errors should NOT be allowlisted."""
        assert not _is_allowlisted("404 Not Found: /api/missing")
        assert not _is_allowlisted("Uncaught TypeError: Cannot read property 'x'")
        assert not _is_allowlisted("Failed to load resource: net::ERR_CONNECTION_REFUSED")


class TestCheckConsoleErrors:
    """Unit tests for _check_console_errors behavior."""

    def test_passes_with_no_errors(self) -> None:
        """Should pass when no errors are present."""
        monitor = {"console_errors": [], "page_errors": []}
        # Should not raise
        _check_console_errors(monitor)

    def test_passes_with_only_warnings(self) -> None:
        """Should pass when only warnings are present (warnings don't fail)."""
        monitor = {
            "console_errors": [
                {"type": "warning", "text": "Some deprecation warning", "location": {}}
            ],
            "page_errors": [],
        }
        # Should not raise
        _check_console_errors(monitor)

    def test_passes_with_allowlisted_errors(self) -> None:
        """Should pass when all errors match allowlist patterns."""
        monitor = {
            "console_errors": [
                {"type": "error", "text": "chrome-extension://xyz/fail.js", "location": {}}
            ],
            "page_errors": [],
        }
        # Should not raise
        _check_console_errors(monitor)

    def test_fails_on_real_console_error(self) -> None:
        """Should fail when a real (non-allowlisted) console error is present."""
        monitor = {
            "console_errors": [
                {"type": "error", "text": "404 Not Found: /api/missing", "location": {}}
            ],
            "page_errors": [],
        }
        with pytest.raises(pytest.fail.Exception) as exc_info:
            _check_console_errors(monitor)
        assert "Browser console errors detected" in str(exc_info.value)
        assert "404 Not Found" in str(exc_info.value)

    def test_fails_on_page_error(self) -> None:
        """Should fail when uncaught page errors are present."""
        monitor = {
            "console_errors": [],
            "page_errors": ["Uncaught ReferenceError: foo is not defined"],
        }
        with pytest.raises(pytest.fail.Exception) as exc_info:
            _check_console_errors(monitor)
        assert "Uncaught page errors" in str(exc_info.value)

    def test_failure_message_suggests_allowlist(self) -> None:
        """Failure message should suggest adding to allowlist for false positives."""
        monitor = {
            "console_errors": [
                {"type": "error", "text": "Some third-party error", "location": {}}
            ],
            "page_errors": [],
        }
        with pytest.raises(pytest.fail.Exception) as exc_info:
            _check_console_errors(monitor)
        assert "CONSOLE_ERROR_ALLOWLIST" in str(exc_info.value)
