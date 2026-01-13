# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Content fixtures for integration testing.

Provides pytest fixtures for sample content files used in testing:
- Audio transcriptions
- PDF-like documents
- HTML web content
- Python code files
"""

from pathlib import Path
from typing import NamedTuple

import pytest


class ContentSample(NamedTuple):
    """Sample content with metadata for testing."""

    path: Path
    content_type: str
    description: str


@pytest.fixture(scope="session", name="content_fixtures_dir")
def fixture_content_fixtures_dir() -> Path:
    """Return path to the content fixtures directory."""
    return Path("tests/fixtures/content")


@pytest.fixture(scope="session", name="sample_audio_transcription")
def fixture_sample_audio_transcription(content_fixtures_dir: Path) -> ContentSample:
    """Return sample audio transcription file (pipe-delimited CSV format)."""
    return ContentSample(
        path=content_fixtures_dir / "sample_audio.txt",
        content_type="audio/transcription",
        description="Technology podcast transcription about AI and semantic search",
    )


@pytest.fixture(scope="session", name="sample_document")
def fixture_sample_document(content_fixtures_dir: Path) -> ContentSample:
    """Return sample document file (plain text, PDF-like content)."""
    return ContentSample(
        path=content_fixtures_dir / "sample_document.txt",
        content_type="text/plain",
        description="Introduction to vector databases document",
    )


@pytest.fixture(scope="session", name="sample_webpage")
def fixture_sample_webpage(content_fixtures_dir: Path) -> ContentSample:
    """Return sample HTML webpage file."""
    return ContentSample(
        path=content_fixtures_dir / "sample_webpage.html",
        content_type="text/html",
        description="Tutorial page about semantic search",
    )


@pytest.fixture(scope="session", name="sample_code")
def fixture_sample_code(content_fixtures_dir: Path) -> ContentSample:
    """Return sample Python code file."""
    return ContentSample(
        path=content_fixtures_dir / "sample_code.py",
        content_type="text/x-python",
        description="Example semantic search implementation",
    )


@pytest.fixture(scope="session", name="all_content_samples")
def fixture_all_content_samples(
    sample_audio_transcription: ContentSample,
    sample_document: ContentSample,
    sample_webpage: ContentSample,
    sample_code: ContentSample,
) -> list[ContentSample]:
    """Return all sample content files for batch testing."""
    return [
        sample_audio_transcription,
        sample_document,
        sample_webpage,
        sample_code,
    ]


@pytest.fixture(scope="session", name="audio_fragments")
def fixture_audio_fragments(sample_audio_transcription: ContentSample) -> list[tuple[float, float, str]]:
    """Parse sample audio transcription into fragments.

    Returns list of (start_secs, end_secs, text) tuples.
    """
    fragments = []
    content = sample_audio_transcription.path.read_text()

    for line in content.strip().split("\n"):
        parts = line.split("|")
        if len(parts) >= 3:
            start = float(parts[0])
            end = float(parts[1])
            text = parts[2]
            fragments.append((start, end, text))

    return fragments
