# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""VTT to CSV conversion utilities for BibleProject transcripts.

Converts WebVTT subtitle files to CSV format with start|end|text columns.
Handles BOM prefix, multi-line cues, and speaker tags like `<v ->text</v>`.
"""

from __future__ import annotations

import re
from pathlib import Path


def parse_vtt_timestamp(ts: str) -> float:
    """Parse a VTT timestamp string into seconds.

    Handles formats like:
    - '00:01:23.456' (HH:MM:SS.mmm)
    - '01:23.456' (MM:SS.mmm)

    Args:
        ts: Timestamp string in VTT format

    Returns:
        Time in seconds as a float

    Raises:
        ValueError: If timestamp format is invalid
    """
    ts = ts.strip()

    # Try HH:MM:SS.mmm format
    match = re.match(r"(\d{1,2}):(\d{2}):(\d{2})\.(\d{3})", ts)
    if match:
        hours, minutes, seconds, millis = match.groups()
        return int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(millis) / 1000

    # Try MM:SS.mmm format
    match = re.match(r"(\d{1,2}):(\d{2})\.(\d{3})", ts)
    if match:
        minutes, seconds, millis = match.groups()
        return int(minutes) * 60 + int(seconds) + int(millis) / 1000

    raise ValueError(f"Invalid VTT timestamp format: {ts}")


def _strip_speaker_tags(text: str) -> str:
    """Remove speaker voice tags from VTT cue text.

    Handles tags like <v ->text</v>, <v Speaker>text</v>.

    Args:
        text: Raw cue text with possible voice tags

    Returns:
        Clean text with voice tags removed
    """
    # Remove opening <v ...> tags
    text = re.sub(r"<v\s+[^>]*>", "", text)
    # Remove closing </v> tags
    text = re.sub(r"</v>", "", text)
    return text.strip()


def _strip_html_tags(text: str) -> str:
    """Remove any remaining HTML-like tags from text.

    Args:
        text: Text that may contain HTML tags

    Returns:
        Text with HTML tags removed
    """
    return re.sub(r"<[^>]+>", "", text)


def convert_vtt_to_csv(vtt_path: Path, csv_path: Path) -> int:
    """Convert a VTT subtitle file to CSV format.

    Output CSV format: start|end|text (pipe-separated)
    - start: Start time in seconds
    - end: End time in seconds
    - text: Cleaned cue text (multi-line collapsed, tags stripped)

    Handles:
    - UTF-8 BOM prefix
    - Multi-line cues (collapsed to single line)
    - Speaker tags like <v ->text</v>
    - Other HTML-like tags

    Args:
        vtt_path: Path to input VTT file
        csv_path: Path to output CSV file

    Returns:
        Number of cues converted

    Raises:
        FileNotFoundError: If VTT file doesn't exist
        ValueError: If VTT file format is invalid
    """
    # Read VTT file, handling BOM
    content = vtt_path.read_text(encoding="utf-8-sig")
    lines = content.splitlines()

    # Validate VTT header
    if not lines or not lines[0].strip().startswith("WEBVTT"):
        raise ValueError(f"Invalid VTT file: missing WEBVTT header in {vtt_path}")

    cues: list[tuple[float, float, str]] = []
    i = 1  # Skip header line

    while i < len(lines):
        line = lines[i].strip()

        # Skip empty lines and NOTE comments
        if not line or line.startswith("NOTE"):
            i += 1
            continue

        # Look for timestamp line (contains " --> ")
        if " --> " in line:
            # Parse timestamps
            parts = line.split(" --> ")
            if len(parts) != 2:
                i += 1
                continue

            try:
                start_time = parse_vtt_timestamp(parts[0].strip())
                # End time might have positioning info after it
                end_part = parts[1].split()[0]
                end_time = parse_vtt_timestamp(end_part)
            except ValueError:
                i += 1
                continue

            # Collect cue text (may be multi-line)
            i += 1
            text_lines = []
            while i < len(lines) and lines[i].strip():
                text_lines.append(lines[i].strip())
                i += 1

            if text_lines:
                # Join multi-line cues with space
                text = " ".join(text_lines)
                # Clean up tags
                text = _strip_speaker_tags(text)
                text = _strip_html_tags(text)
                # Normalize whitespace
                text = " ".join(text.split())

                if text:
                    cues.append((start_time, end_time, text))
        else:
            # Skip cue identifier lines or other content
            i += 1

    # Write CSV output
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "w", encoding="utf-8") as f:
        for start, end, text in cues:
            # Escape pipe characters in text
            text = text.replace("|", "\\|")
            f.write(f"{start}|{end}|{text}\n")

    return len(cues)
