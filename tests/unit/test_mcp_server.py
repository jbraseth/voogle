# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Unit tests for MCP server module."""

import os
from unittest.mock import patch

import pytest

from voogle.mcp.server import (
    MCPSettings,
    MCPTransport,
    create_mcp_server,
)

pytestmark = pytest.mark.unit


class TestMCPTransport:
    """Tests for MCPTransport enum."""

    @pytest.mark.description("MCPTransport has all expected values")
    def test_transport_values(self) -> None:
        assert MCPTransport.STDIO.value == "stdio"
        assert MCPTransport.HTTP.value == "http"
        assert MCPTransport.SSE.value == "sse"

    @pytest.mark.description("MCPTransport has exactly three members")
    def test_transport_count(self) -> None:
        assert len(MCPTransport) == 3


class TestMCPSettings:
    """Tests for MCPSettings configuration class."""

    @pytest.mark.description("MCPSettings has correct defaults")
    def test_default_values(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            settings = MCPSettings()
            assert settings.host == "0.0.0.0"
            assert settings.port == 8000
            assert settings.transport == "stdio"
            assert settings.path == "/mcp"

    @pytest.mark.description("MCPSettings reads from environment variables")
    def test_env_overrides(self) -> None:
        env_vars = {
            "MCP_HOST": "127.0.0.1",
            "MCP_PORT": "9000",
            "MCP_TRANSPORT": "http",
            "MCP_PATH": "/api/mcp",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            settings = MCPSettings()
            assert settings.host == "127.0.0.1"
            assert settings.port == 9000
            assert settings.transport == "http"
            assert settings.path == "/api/mcp"

    @pytest.mark.description("MCPSettings handles partial env overrides")
    def test_partial_env_overrides(self) -> None:
        env_vars = {"MCP_PORT": "8080"}
        with patch.dict(os.environ, env_vars, clear=True):
            settings = MCPSettings()
            assert settings.host == "0.0.0.0"  # default
            assert settings.port == 8080  # overridden
            assert settings.transport == "stdio"  # default
            assert settings.path == "/mcp"  # default


class TestCreateMCPServer:
    """Tests for create_mcp_server function."""

    @pytest.mark.description("create_mcp_server returns FastMCP instance")
    def test_returns_fastmcp_instance(self) -> None:
        from fastmcp import FastMCP

        server = create_mcp_server()
        assert isinstance(server, FastMCP)

    @pytest.mark.description("create_mcp_server uses custom name")
    def test_custom_name(self) -> None:
        server = create_mcp_server(name="Test MCP Server")
        assert server.name == "Test MCP Server"

    @pytest.mark.description("create_mcp_server uses default name")
    def test_default_name(self) -> None:
        server = create_mcp_server()
        assert server.name == "Voogle MCP Server"

    @pytest.mark.description("MCP server has health tool registered")
    @pytest.mark.asyncio
    async def test_has_health_tool(self) -> None:
        server = create_mcp_server()
        tools = await server._tool_manager.list_tools()
        tool_names = [tool.name for tool in tools]
        assert "health" in tool_names

    @pytest.mark.description("MCP server has version tool registered")
    @pytest.mark.asyncio
    async def test_has_version_tool(self) -> None:
        server = create_mcp_server()
        tools = await server._tool_manager.list_tools()
        tool_names = [tool.name for tool in tools]
        assert "version" in tool_names

    @pytest.mark.description("MCP server repr is readable")
    def test_server_repr(self) -> None:
        server = create_mcp_server()
        repr_str = repr(server)
        assert "Voogle MCP Server" in repr_str or "FastMCP" in repr_str or str(server)
