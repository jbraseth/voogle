# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for git commit pinning functionality."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from voogle.adapters.code import (
    check_ref_staleness,
    resolve_git_ref_to_sha,
)
from voogle.core.location import CodeLocation

pytestmark = pytest.mark.unit


class TestCodeLocationWithGitRef:
    """Tests for CodeLocation with git_ref support."""

    @pytest.mark.description("Creates valid code location with git_ref")
    def test_with_git_ref(self) -> None:
        loc = CodeLocation(
            file_path="src/main.py",
            start_line=10,
            end_line=20,
            git_ref="abc123def456",
        )
        assert loc.file_path == "src/main.py"
        assert loc.start_line == 10
        assert loc.end_line == 20
        assert loc.git_ref == "abc123def456"

    @pytest.mark.description("Creates code location without git_ref (backwards compatible)")
    def test_without_git_ref(self) -> None:
        loc = CodeLocation(
            file_path="src/main.py",
            start_line=10,
        )
        assert loc.git_ref is None

    @pytest.mark.description("Generates deep link with git ref using blob path")
    def test_deep_link_with_git_ref(self) -> None:
        loc = CodeLocation(
            file_path="test.py",
            start_line=1,
            end_line=10,
            git_ref="abc123",
        )
        url = loc.to_deep_link("https://github.com/org/repo")
        assert url == "https://github.com/org/repo/blob/abc123/test.py#L1-L10"

    @pytest.mark.description("Generates deep link without git ref (original behavior)")
    def test_deep_link_without_git_ref(self) -> None:
        loc = CodeLocation(
            file_path="test.py",
            start_line=1,
            end_line=10,
        )
        url = loc.to_deep_link("https://github.com/org/repo")
        assert url == "https://github.com/org/repo/test.py#L1-L10"

    @pytest.mark.description("Generates deep link with git ref and single line")
    def test_deep_link_single_line_with_git_ref(self) -> None:
        loc = CodeLocation(
            file_path="src/utils.py",
            start_line=42,
            git_ref="def789",
        )
        url = loc.to_deep_link("https://github.com/org/repo")
        assert url == "https://github.com/org/repo/blob/def789/src/utils.py#L42"

    @pytest.mark.description("Git ref is frozen (immutable)")
    def test_git_ref_immutable(self) -> None:
        loc = CodeLocation(
            file_path="test.py",
            start_line=1,
            git_ref="abc123",
        )
        with pytest.raises(Exception):
            loc.git_ref = "new_ref"  # type: ignore[misc]


class TestResolveGitRefToSha:
    """Tests for resolve_git_ref_to_sha function."""

    @pytest.mark.description("Resolves branch name to SHA")
    def test_resolve_branch(self, tmp_path: Path) -> None:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "abc123def456789\n"

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            result = resolve_git_ref_to_sha(tmp_path, "main")

        assert result == "abc123def456"
        mock_run.assert_called_once()
        args = mock_run.call_args
        assert args[0][0] == ["git", "rev-parse", "main"]

    @pytest.mark.description("Resolves tag to SHA")
    def test_resolve_tag(self, tmp_path: Path) -> None:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "fedcba987654321\n"

        with patch("subprocess.run", return_value=mock_result):
            result = resolve_git_ref_to_sha(tmp_path, "v1.0.0")

        assert result == "fedcba987654"

    @pytest.mark.description("Returns None for invalid ref")
    def test_invalid_ref(self, tmp_path: Path) -> None:
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""

        with patch("subprocess.run", return_value=mock_result):
            result = resolve_git_ref_to_sha(tmp_path, "nonexistent-branch")

        assert result is None

    @pytest.mark.description("Returns None on subprocess error")
    def test_subprocess_error(self, tmp_path: Path) -> None:
        with patch("subprocess.run", side_effect=subprocess.SubprocessError("error")):
            result = resolve_git_ref_to_sha(tmp_path, "main")

        assert result is None


class TestCheckRefStaleness:
    """Tests for check_ref_staleness function."""

    @pytest.mark.description("Returns not stale when refs match")
    def test_not_stale(self, tmp_path: Path) -> None:
        with patch("voogle.adapters.code._get_git_ref", return_value="abc123def456"):
            result = check_ref_staleness(tmp_path, "abc123def456")

        assert result["is_stale"] is False
        assert result["current_ref"] == "abc123def456"
        assert result["commits_behind"] is None

    @pytest.mark.description("Returns stale when refs differ")
    def test_stale_ref(self, tmp_path: Path) -> None:
        mock_count = MagicMock()
        mock_count.returncode = 0
        mock_count.stdout = "5\n"

        with patch("voogle.adapters.code._get_git_ref", return_value="def456abc123"):
            with patch("subprocess.run", return_value=mock_count):
                result = check_ref_staleness(tmp_path, "abc123def456")

        assert result["is_stale"] is True
        assert result["current_ref"] == "def456abc123"
        assert result["commits_behind"] == 5

    @pytest.mark.description("Checks file changes when file_path provided")
    def test_file_changed(self, tmp_path: Path) -> None:
        mock_count = MagicMock()
        mock_count.returncode = 0
        mock_count.stdout = "3\n"

        mock_diff = MagicMock()
        mock_diff.returncode = 0
        mock_diff.stdout = "src/main.py\n"

        with patch("voogle.adapters.code._get_git_ref", return_value="def456abc123"):
            with patch("subprocess.run", side_effect=[mock_count, mock_diff]):
                result = check_ref_staleness(
                    tmp_path, "abc123def456", file_path="src/main.py"
                )

        assert result["is_stale"] is True
        assert result["file_changed"] is True

    @pytest.mark.description("File unchanged when not in diff")
    def test_file_unchanged(self, tmp_path: Path) -> None:
        mock_count = MagicMock()
        mock_count.returncode = 0
        mock_count.stdout = "3\n"

        mock_diff = MagicMock()
        mock_diff.returncode = 0
        mock_diff.stdout = ""

        with patch("voogle.adapters.code._get_git_ref", return_value="def456abc123"):
            with patch("subprocess.run", side_effect=[mock_count, mock_diff]):
                result = check_ref_staleness(
                    tmp_path, "abc123def456", file_path="src/other.py"
                )

        assert result["is_stale"] is True
        assert result["file_changed"] is False

    @pytest.mark.description("Returns default result when not in git repo")
    def test_not_git_repo(self, tmp_path: Path) -> None:
        with patch("voogle.adapters.code._get_git_ref", return_value=None):
            result = check_ref_staleness(tmp_path, "abc123def456")

        assert result["is_stale"] is False
        assert result["current_ref"] is None
        assert result["commits_behind"] is None
        assert result["file_changed"] is None
