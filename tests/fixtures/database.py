# Copyright (c) 2022 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Database fixtures for testing."""

import os
import shutil
from collections.abc import Generator
from typing import Any

import pytest
import sqlalchemy
from voogle import db
from voogle.settings import settings


@pytest.fixture(autouse=True, name="create_test_database")
def fixture_create_test_database() -> Generator[None, Any, Any]:
    """Automatically create a fresh test database for each test."""
    assert os.environ["ENVIRONMENT"] == "test"
    engine = sqlalchemy.create_engine(
        db.get_db_url(), connect_args={"check_same_thread": False}
    )
    # Drop first to ensure clean slate (handles --keep from previous run)
    db.metadata.drop_all(engine)
    db.metadata.create_all(engine)
    yield
    if not pytest.keep_fixtures:
        db.metadata.drop_all(engine)


@pytest.fixture(autouse=True, scope="session", name="clean_environment")
def fixture_clean_environment() -> Generator[None, Any, Any]:
    yield
    if pytest.keep_fixtures:
        return
    data = settings.data_dir
    if "test" in str(data):
        shutil.rmtree(data, ignore_errors=True)
    else:
        raise AssertionError("Not using test folder as data dir")
