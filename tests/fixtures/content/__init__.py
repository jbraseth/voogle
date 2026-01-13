# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Sample content fixtures for integration testing.

This module provides sample files for testing different content types:
- Audio files (transcription testing)
- PDF files (document extraction)
- HTML files (web content parsing)
- Code files (code analysis)

These fixtures are used by integration tests to verify the indexing
and embedding pipeline works correctly with various content types.
"""

from pathlib import Path

# Directory containing sample content files
CONTENT_DIR = Path(__file__).parent


def get_sample_audio_path() -> Path:
    """Return path to sample audio file."""
    return CONTENT_DIR / "sample_audio.txt"


def get_sample_pdf_path() -> Path:
    """Return path to sample PDF text file."""
    return CONTENT_DIR / "sample_document.txt"


def get_sample_html_path() -> Path:
    """Return path to sample HTML file."""
    return CONTENT_DIR / "sample_webpage.html"


def get_sample_code_path() -> Path:
    """Return path to sample code file."""
    return CONTENT_DIR / "sample_code.py"
