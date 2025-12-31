# Copyright (c) 2022 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Test data fixtures."""

import pathlib

import pytest
from voogle import transcription


@pytest.fixture(scope="session", name="tests_data_dir")
def fixture_tests_data_dir() -> pathlib.Path:
    # Use relative path that works locally and in Docker
    return pathlib.Path("tests/test_files")


@pytest.fixture(scope="session", name="golf_csv_path")
def fixture_golf_csv_path(tests_data_dir: pathlib.Path) -> pathlib.Path:
    return tests_data_dir / "golf.csv"


@pytest.fixture(scope="session", name="jobs_csv_path")
def fixture_jobs_csv_path(tests_data_dir: pathlib.Path) -> pathlib.Path:
    return tests_data_dir / "jobs.csv"


@pytest.fixture(scope="session", name="jobs_mp3_path")
def fixture_jobs_mp3_path(tests_data_dir: pathlib.Path) -> pathlib.Path:
    return tests_data_dir / "jobs.mp3"


@pytest.fixture(name="jobs_transcription")
def fixture_jobs_transcription() -> transcription.Transcription:
    return [
        (0.0, 3.2, " It was their farewell message as they signed off."),
        (3.2, 6.26, " Stay hungry, stay foolish."),
        (6.26, 9.78, " And I have always wished that for myself."),
        (9.78, 13.3, " And now, as you graduate to begin anew,"),
        (13.3, 15.1, " I wish that for you."),
        (15.1, 17.5, " Stay hungry, stay foolish."),
    ]
