# Copyright (c) 2022 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Pytest configuration, hooks, and plugin registration."""

# Import playwright shim FIRST - registers mocks if playwright not installed
import compat.playwright  # noqa: I001

import pytest
from pytest import Config, Parser

pytest_plugins = [
    "fixtures.database",
    "fixtures.net",
    "fixtures.models",
    "fixtures.test_files",
    "fixtures.manifest",
    "fixtures.playwright",
    "fixtures.voogle",
    "fixtures.vector",
]


def pytest_addoption(parser: Parser) -> None:
    """Add custom command line options."""
    parser.addoption(
        "--keep",
        action="store_true",
        help="Keep test data after run (skip teardown cleanup)",
    )
    parser.addoption(
        "--openai",
        action="store_true",
        help="Use OpenAI embeddings instead of local (requires OPENAI_API_KEY)",
    )


def pytest_configure(config: Config) -> None:
    """Store options in pytest namespace for global access."""
    pytest.keep_fixtures = config.getoption("--keep")
    pytest.use_openai = config.getoption("--openai")


@pytest.fixture(autouse=True)
def configure_embeddings_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    """Configure embeddings provider based on --openai flag.

    Default: local embeddings (fast, free, deterministic)
    With --openai: OpenAI embeddings (requires OPENAI_API_KEY in env)
    """
    from voogle import settings as settings_module

    expected_provider = "openai" if pytest.use_openai else "local"

    if pytest.use_openai:
        # Use OpenAI - requires OPENAI_API_KEY to be set in environment
        monkeypatch.setattr(settings_module.settings, "embeddings_provider_override", "openai")
    else:
        # Force local embeddings regardless of OPENAI_API_KEY presence
        monkeypatch.setattr(settings_module.settings, "embeddings_provider_override", "local")

    # Verify the setting took effect
    assert settings_module.settings.embeddings_provider == expected_provider, (
        f"Expected embeddings_provider={expected_provider}, "
        f"got {settings_module.settings.embeddings_provider}"
    )


# Provide mock fixtures for pytest-playwright when playwright is not installed
if not compat.playwright.PLAYWRIGHT_AVAILABLE:

    @pytest.fixture(scope="session")
    def playwright() -> None:
        """Mock playwright fixture - skips E2E tests when playwright unavailable."""
        pytest.skip("Playwright is not installed")

    @pytest.fixture(scope="session")
    def launch_browser() -> None:
        """Mock launch_browser fixture - skips E2E tests when playwright unavailable."""
        pytest.skip("Playwright is not installed")
