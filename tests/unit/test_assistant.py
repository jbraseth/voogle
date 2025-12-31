# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for local assistant functionality."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from voogle.routers import assistant
from voogle.schemas.assistant import SourceCitation

pytestmark = pytest.mark.unit


class TestRequireLocalAssistantEnabled:
    """Tests for the feature flag guard layer."""

    @pytest.mark.description("Feature disabled raises 503")
    def test_feature_disabled_raises_503(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """When LOCAL_ASSISTANT_ENABLED=false, raises HTTPException 503."""
        from voogle import settings as settings_module

        monkeypatch.setattr(settings_module.settings, "local_assistant_enabled", False)

        with pytest.raises(HTTPException) as exc_info:
            assistant.require_local_assistant_enabled()

        assert exc_info.value.status_code == 503
        assert "not enabled" in exc_info.value.detail

    @pytest.mark.description("Feature enabled passes")
    def test_feature_enabled_passes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """When LOCAL_ASSISTANT_ENABLED=true, no exception raised."""
        from voogle import settings as settings_module

        monkeypatch.setattr(settings_module.settings, "local_assistant_enabled", True)

        # Should not raise
        assistant.require_local_assistant_enabled()


class TestRequireLocalhostOrAllowlist:
    """Tests for the network origin guard layer."""

    @pytest.mark.description("Localhost IPv4 is allowed")
    def test_localhost_ipv4_allowed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Request from 127.0.0.1 is allowed."""
        from voogle import settings as settings_module

        monkeypatch.setattr(settings_module.settings, "local_assistant_allowlist", "")

        request = MagicMock()
        request.client.host = "127.0.0.1"

        # Should not raise
        assistant.require_localhost_or_allowlist(request)

    @pytest.mark.description("Localhost IPv6 is allowed")
    def test_localhost_ipv6_allowed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Request from ::1 is allowed."""
        from voogle import settings as settings_module

        monkeypatch.setattr(settings_module.settings, "local_assistant_allowlist", "")

        request = MagicMock()
        request.client.host = "::1"

        # Should not raise
        assistant.require_localhost_or_allowlist(request)

    @pytest.mark.description("Non-localhost without allowlist raises 403")
    def test_non_localhost_raises_403(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Request from non-localhost IP (not in allowlist) raises 403."""
        from voogle import settings as settings_module

        monkeypatch.setattr(settings_module.settings, "local_assistant_allowlist", "")

        request = MagicMock()
        request.client.host = "192.168.1.100"

        with pytest.raises(HTTPException) as exc_info:
            assistant.require_localhost_or_allowlist(request)

        assert exc_info.value.status_code == 403
        assert "192.168.1.100" in exc_info.value.detail

    @pytest.mark.description("Allowlisted IP is permitted")
    def test_allowlisted_ip_permitted(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Request from allowlisted IP is allowed."""
        from voogle import settings as settings_module

        monkeypatch.setattr(
            settings_module.settings,
            "local_assistant_allowlist",
            "192.168.1.100, 10.0.0.5",
        )

        request = MagicMock()
        request.client.host = "192.168.1.100"

        # Should not raise
        assistant.require_localhost_or_allowlist(request)

    @pytest.mark.description("IP not in allowlist raises 403")
    def test_ip_not_in_allowlist_raises_403(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Request from IP not in allowlist raises 403."""
        from voogle import settings as settings_module

        monkeypatch.setattr(
            settings_module.settings,
            "local_assistant_allowlist",
            "192.168.1.100, 10.0.0.5",
        )

        request = MagicMock()
        request.client.host = "192.168.1.200"  # Not in allowlist

        with pytest.raises(HTTPException) as exc_info:
            assistant.require_localhost_or_allowlist(request)

        assert exc_info.value.status_code == 403

    @pytest.mark.description("Missing client raises 403")
    def test_missing_client_raises_403(self) -> None:
        """Request with no client info raises 403."""
        request = MagicMock()
        request.client = None

        with pytest.raises(HTTPException) as exc_info:
            assistant.require_localhost_or_allowlist(request)

        assert exc_info.value.status_code == 403
        assert "Cannot determine client IP" in exc_info.value.detail


class TestFindCliTool:
    """Tests for CLI tool detection."""

    @pytest.mark.description("CLI not found raises 503")
    def test_cli_not_found_raises_503(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """When neither claude nor codex is in PATH, raises 503."""
        from voogle import settings as settings_module

        monkeypatch.setattr(
            settings_module.settings, "local_assistant_cli_preference", "claude"
        )

        with patch("voogle.routers.assistant.shutil.which", return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                assistant.find_cli_tool()

            assert exc_info.value.status_code == 503
            assert "CLI" in exc_info.value.detail
            assert "PATH" in exc_info.value.detail

    @pytest.mark.description("Preferred CLI is used when available")
    def test_preferred_cli_used(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Uses LOCAL_ASSISTANT_CLI_PREFERENCE when available."""
        from voogle import settings as settings_module

        monkeypatch.setattr(
            settings_module.settings, "local_assistant_cli_preference", "claude"
        )

        def mock_which(cmd: str) -> str | None:
            return "/usr/bin/claude" if cmd == "claude" else None

        with patch("voogle.routers.assistant.shutil.which", side_effect=mock_which):
            result = assistant.find_cli_tool()

        assert result == "claude"

    @pytest.mark.description("Falls back to alternative CLI")
    def test_fallback_to_alternative(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Falls back to alternative CLI when preferred not available."""
        from voogle import settings as settings_module

        monkeypatch.setattr(
            settings_module.settings, "local_assistant_cli_preference", "claude"
        )

        def mock_which(cmd: str) -> str | None:
            return "/usr/bin/codex" if cmd == "codex" else None

        with patch("voogle.routers.assistant.shutil.which", side_effect=mock_which):
            result = assistant.find_cli_tool()

        assert result == "codex"

    @pytest.mark.description("Codex preference honored")
    def test_codex_preference_honored(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """When codex is preferred and available, it is used."""
        from voogle import settings as settings_module

        monkeypatch.setattr(
            settings_module.settings, "local_assistant_cli_preference", "codex"
        )

        def mock_which(cmd: str) -> str | None:
            return f"/usr/bin/{cmd}"  # Both available

        with patch("voogle.routers.assistant.shutil.which", side_effect=mock_which):
            result = assistant.find_cli_tool()

        assert result == "codex"


class TestExecuteCli:
    """Tests for CLI execution."""

    @pytest.mark.description("Successful CLI execution returns stdout")
    def test_successful_execution(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Successful CLI execution returns stdout."""
        from voogle import settings as settings_module

        monkeypatch.setattr(settings_module.settings, "local_assistant_cli_timeout", 60)

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "This is the answer."
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            result = assistant.execute_cli("claude", "test prompt")

        assert result == "This is the answer."

    @pytest.mark.description("CLI failure raises 500")
    def test_cli_failure_raises_500(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """CLI exit code != 0 raises HTTPException 500."""
        from voogle import settings as settings_module

        monkeypatch.setattr(settings_module.settings, "local_assistant_cli_timeout", 60)

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error: something went wrong"

        with patch("subprocess.run", return_value=mock_result):
            with pytest.raises(HTTPException) as exc_info:
                assistant.execute_cli("claude", "test prompt")

            assert exc_info.value.status_code == 500
            assert "exit code 1" in exc_info.value.detail

    @pytest.mark.description("CLI timeout raises 500")
    def test_cli_timeout_raises_500(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """CLI timeout raises HTTPException 500."""
        import subprocess

        from voogle import settings as settings_module

        monkeypatch.setattr(settings_module.settings, "local_assistant_cli_timeout", 60)

        with patch(
            "subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="claude", timeout=60)
        ):
            with pytest.raises(HTTPException) as exc_info:
                assistant.execute_cli("claude", "test prompt")

            assert exc_info.value.status_code == 500
            assert "timed out" in exc_info.value.detail


class TestBuildPrompt:
    """Tests for prompt building."""

    @pytest.mark.description("Prompt includes all sources with citations")
    def test_prompt_includes_citations(self) -> None:
        """Built prompt contains [1], [2] citations with episode/channel info."""
        sources = [
            SourceCitation(
                index=1,
                episode_title="Episode 1",
                channel_title="Channel A",
                start_secs=10.0,
                end_secs=50.0,
                text="This is the first fragment.",
                media_url="http://example.com/ep1.mp3",
            ),
            SourceCitation(
                index=2,
                episode_title="Episode 2",
                channel_title="Channel B",
                start_secs=100.0,
                end_secs=150.0,
                text="This is the second fragment.",
                media_url="http://example.com/ep2.mp3",
            ),
        ]

        prompt = assistant.build_prompt("What is the topic?", sources)

        assert "[1]" in prompt
        assert "[2]" in prompt
        assert "Episode 1" in prompt
        assert "Episode 2" in prompt
        assert "Channel A" in prompt
        assert "Channel B" in prompt
        assert "10s-50s" in prompt
        assert "100s-150s" in prompt
        assert "This is the first fragment." in prompt
        assert "This is the second fragment." in prompt
        assert "What is the topic?" in prompt

    @pytest.mark.description("Prompt handles empty search results")
    def test_empty_results_prompt(self) -> None:
        """When search returns no results, prompt explains this."""
        prompt = assistant.build_prompt("What is the topic?", [])

        assert "no relevant sources" in prompt.lower()
        assert "What is the topic?" in prompt
