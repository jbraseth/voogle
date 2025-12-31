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


def pytest_configure(config: Config) -> None:
    """Store options in pytest namespace for global access."""
    pytest.keep_fixtures = config.getoption("--keep")


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
