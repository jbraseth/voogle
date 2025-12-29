# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Manifest-based configuration fixtures for e2e tests."""

from pathlib import Path

import pytest
from e2e.shared.manifest import ManifestReader


@pytest.fixture(scope="session", name="manifest_reader")
def fixture_manifest_reader() -> ManifestReader:
    manifest_dir = Path(__file__).parent.parent / "e2e"
    return ManifestReader(manifest_dir)


@pytest.fixture(scope="session", name="streamlit_url")
def fixture_streamlit_url(manifest_reader: ManifestReader) -> str:
    return manifest_reader.get_if_exists_in_manifest("management_url")


@pytest.fixture(scope="session", name="voogle_url")
def fixture_voogle_url(manifest_reader: ManifestReader) -> str:
    return manifest_reader.get_if_exists_in_manifest("frontend_url")


@pytest.fixture(scope="session", name="voogle_credentials")
def fixture_voogle_credentials(manifest_reader: ManifestReader) -> tuple[str, str]:
    return (
        manifest_reader.get_if_exists_in_manifest("admin_username"),
        manifest_reader.get_if_exists_in_manifest("admin_password"),
    )
