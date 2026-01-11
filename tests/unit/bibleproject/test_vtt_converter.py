# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for VTT converter module."""

from pathlib import Path

import pytest

from voogle.bibleproject.vtt_converter import convert_vtt_to_csv, parse_vtt_timestamp

pytestmark = pytest.mark.unit


class TestParseVttTimestamp:
    """Tests for parse_vtt_timestamp function."""

    @pytest.mark.description("Parses HH:MM:SS.mmm format correctly")
    def test_full_format(self) -> None:
        assert parse_vtt_timestamp("00:01:23.456") == 83.456
        assert parse_vtt_timestamp("01:00:00.000") == 3600.0
        assert parse_vtt_timestamp("00:00:00.000") == 0.0

    @pytest.mark.description("Parses MM:SS.mmm format correctly")
    def test_short_format(self) -> None:
        assert parse_vtt_timestamp("01:23.456") == 83.456
        assert parse_vtt_timestamp("00:30.500") == 30.5

    @pytest.mark.description("Handles various hour values")
    def test_hours(self) -> None:
        assert parse_vtt_timestamp("02:30:45.123") == 2 * 3600 + 30 * 60 + 45.123
        assert parse_vtt_timestamp("10:00:00.000") == 36000.0

    @pytest.mark.description("Handles whitespace around timestamp")
    def test_whitespace(self) -> None:
        assert parse_vtt_timestamp("  00:01:23.456  ") == 83.456
        assert parse_vtt_timestamp("\t01:23.456\n") == 83.456

    @pytest.mark.description("Raises ValueError for invalid formats")
    def test_invalid_format(self) -> None:
        with pytest.raises(ValueError, match="Invalid VTT timestamp"):
            parse_vtt_timestamp("invalid")
        with pytest.raises(ValueError, match="Invalid VTT timestamp"):
            parse_vtt_timestamp("1:2:3")
        with pytest.raises(ValueError, match="Invalid VTT timestamp"):
            parse_vtt_timestamp("00:00:00")  # Missing milliseconds


class TestConvertVttToCsv:
    """Tests for convert_vtt_to_csv function."""

    @pytest.mark.description("Converts simple VTT file to CSV")
    def test_simple_conversion(self, tmp_path: Path) -> None:
        vtt_content = """WEBVTT

00:00:01.000 --> 00:00:03.000
Hello world

00:00:05.000 --> 00:00:07.500
Second cue
"""
        vtt_path = tmp_path / "test.vtt"
        csv_path = tmp_path / "output.csv"
        vtt_path.write_text(vtt_content, encoding="utf-8")

        count = convert_vtt_to_csv(vtt_path, csv_path)

        assert count == 2
        lines = csv_path.read_text().splitlines()
        assert lines[0] == "1.0|3.0|Hello world"
        assert lines[1] == "5.0|7.5|Second cue"

    @pytest.mark.description("Handles BOM prefix in VTT file")
    def test_bom_handling(self, tmp_path: Path) -> None:
        vtt_content = "WEBVTT\n\n00:00:01.000 --> 00:00:02.000\nTest cue\n"
        vtt_path = tmp_path / "bom.vtt"
        csv_path = tmp_path / "output.csv"
        # Write with utf-8-sig encoding which adds BOM prefix
        vtt_path.write_bytes(vtt_content.encode("utf-8-sig"))

        count = convert_vtt_to_csv(vtt_path, csv_path)

        assert count == 1
        lines = csv_path.read_text().splitlines()
        assert lines[0] == "1.0|2.0|Test cue"

    @pytest.mark.description("Collapses multi-line cues to single line")
    def test_multiline_cues(self, tmp_path: Path) -> None:
        vtt_content = """WEBVTT

00:00:01.000 --> 00:00:05.000
This is line one
and this is line two
and line three
"""
        vtt_path = tmp_path / "multiline.vtt"
        csv_path = tmp_path / "output.csv"
        vtt_path.write_text(vtt_content, encoding="utf-8")

        count = convert_vtt_to_csv(vtt_path, csv_path)

        assert count == 1
        lines = csv_path.read_text().splitlines()
        assert lines[0] == "1.0|5.0|This is line one and this is line two and line three"

    @pytest.mark.description("Strips speaker voice tags")
    def test_speaker_tags(self, tmp_path: Path) -> None:
        vtt_content = """WEBVTT

00:00:01.000 --> 00:00:03.000
<v ->Hello from speaker</v>

00:00:04.000 --> 00:00:06.000
<v Speaker Name>This is the speaker</v>
"""
        vtt_path = tmp_path / "speakers.vtt"
        csv_path = tmp_path / "output.csv"
        vtt_path.write_text(vtt_content, encoding="utf-8")

        count = convert_vtt_to_csv(vtt_path, csv_path)

        assert count == 2
        lines = csv_path.read_text().splitlines()
        assert lines[0] == "1.0|3.0|Hello from speaker"
        assert lines[1] == "4.0|6.0|This is the speaker"

    @pytest.mark.description("Strips other HTML-like tags")
    def test_html_tags(self, tmp_path: Path) -> None:
        vtt_content = """WEBVTT

00:00:01.000 --> 00:00:03.000
<b>Bold</b> and <i>italic</i> text
"""
        vtt_path = tmp_path / "html.vtt"
        csv_path = tmp_path / "output.csv"
        vtt_path.write_text(vtt_content, encoding="utf-8")

        count = convert_vtt_to_csv(vtt_path, csv_path)

        assert count == 1
        lines = csv_path.read_text().splitlines()
        assert lines[0] == "1.0|3.0|Bold and italic text"

    @pytest.mark.description("Handles cue identifiers")
    def test_cue_identifiers(self, tmp_path: Path) -> None:
        vtt_content = """WEBVTT

1
00:00:01.000 --> 00:00:02.000
First cue

cue-2
00:00:03.000 --> 00:00:04.000
Second cue
"""
        vtt_path = tmp_path / "ids.vtt"
        csv_path = tmp_path / "output.csv"
        vtt_path.write_text(vtt_content, encoding="utf-8")

        count = convert_vtt_to_csv(vtt_path, csv_path)

        assert count == 2

    @pytest.mark.description("Handles positioning info after end timestamp")
    def test_positioning_info(self, tmp_path: Path) -> None:
        vtt_content = """WEBVTT

00:00:01.000 --> 00:00:03.000 align:start position:10%
Positioned text
"""
        vtt_path = tmp_path / "positioned.vtt"
        csv_path = tmp_path / "output.csv"
        vtt_path.write_text(vtt_content, encoding="utf-8")

        count = convert_vtt_to_csv(vtt_path, csv_path)

        assert count == 1
        lines = csv_path.read_text().splitlines()
        assert lines[0] == "1.0|3.0|Positioned text"

    @pytest.mark.description("Escapes pipe characters in text")
    def test_pipe_escaping(self, tmp_path: Path) -> None:
        vtt_content = """WEBVTT

00:00:01.000 --> 00:00:03.000
Text with | pipe character
"""
        vtt_path = tmp_path / "pipe.vtt"
        csv_path = tmp_path / "output.csv"
        vtt_path.write_text(vtt_content, encoding="utf-8")

        count = convert_vtt_to_csv(vtt_path, csv_path)

        assert count == 1
        lines = csv_path.read_text().splitlines()
        assert lines[0] == r"1.0|3.0|Text with \| pipe character"

    @pytest.mark.description("Creates output directory if needed")
    def test_creates_output_dir(self, tmp_path: Path) -> None:
        vtt_content = "WEBVTT\n\n00:00:01.000 --> 00:00:02.000\nTest\n"
        vtt_path = tmp_path / "test.vtt"
        csv_path = tmp_path / "subdir" / "deep" / "output.csv"
        vtt_path.write_text(vtt_content, encoding="utf-8")

        count = convert_vtt_to_csv(vtt_path, csv_path)

        assert count == 1
        assert csv_path.exists()

    @pytest.mark.description("Raises ValueError for missing WEBVTT header")
    def test_invalid_header(self, tmp_path: Path) -> None:
        vtt_path = tmp_path / "invalid.vtt"
        csv_path = tmp_path / "output.csv"
        vtt_path.write_text("Not a VTT file\n00:00:01.000 --> 00:00:02.000\nText\n")

        with pytest.raises(ValueError, match="missing WEBVTT header"):
            convert_vtt_to_csv(vtt_path, csv_path)

    @pytest.mark.description("Handles empty VTT file with only header")
    def test_empty_vtt(self, tmp_path: Path) -> None:
        vtt_path = tmp_path / "empty.vtt"
        csv_path = tmp_path / "output.csv"
        vtt_path.write_text("WEBVTT\n\n")

        count = convert_vtt_to_csv(vtt_path, csv_path)

        assert count == 0
        assert csv_path.read_text() == ""

    @pytest.mark.description("Handles NOTE comments in VTT")
    def test_note_comments(self, tmp_path: Path) -> None:
        vtt_content = """WEBVTT

NOTE This is a comment

00:00:01.000 --> 00:00:02.000
Actual cue
"""
        vtt_path = tmp_path / "notes.vtt"
        csv_path = tmp_path / "output.csv"
        vtt_path.write_text(vtt_content, encoding="utf-8")

        count = convert_vtt_to_csv(vtt_path, csv_path)

        assert count == 1
        lines = csv_path.read_text().splitlines()
        assert lines[0] == "1.0|2.0|Actual cue"
