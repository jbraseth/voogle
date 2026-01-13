# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""MCP server implementation using FastMCP.

This module provides:
- MCP server creation with FastMCP
- HTTP/SSE transport support
- STDIO transport support
- Health endpoint
- Version reporting
- Environment-based configuration
"""

import enum
import os
from typing import Any

from fastmcp import FastMCP

import voogle


class MCPTransport(enum.Enum):
    """Supported MCP transport protocols."""

    STDIO = "stdio"
    HTTP = "http"
    SSE = "sse"


class MCPSettings:
    """MCP server configuration from environment variables."""

    def __init__(self) -> None:
        self.host: str = os.environ.get("MCP_HOST", "0.0.0.0")
        self.port: int = int(os.environ.get("MCP_PORT", "8000"))
        self.transport: str = os.environ.get("MCP_TRANSPORT", MCPTransport.STDIO.value)
        self.path: str = os.environ.get("MCP_PATH", "/mcp")


def create_mcp_server(name: str = "Voogle MCP Server") -> FastMCP:
    """Create and configure an MCP server instance.

    The server exposes Voogle's semantic search capabilities through
    the Model Context Protocol, enabling AI assistants to search
    podcast transcriptions.

    Args:
        name: Display name for the MCP server.

    Returns:
        Configured FastMCP server instance.
    """
    mcp = FastMCP(name)

    @mcp.tool
    def health() -> dict[str, Any]:
        """Check MCP server health status.

        Returns server health information including version,
        status, and basic diagnostics.
        """
        return {
            "status": "healthy",
            "version": voogle.__version__,
            "server": name,
        }

    @mcp.tool
    def version() -> str:
        """Get the Voogle MCP server version.

        Returns the current version string from the voogle package.
        """
        return voogle.__version__

    return mcp


def run_server(
    server: FastMCP | None = None,
    transport: str | None = None,
    host: str | None = None,
    port: int | None = None,
    path: str | None = None,
) -> None:
    """Run the MCP server with the specified transport.

    Supports STDIO, HTTP, and SSE transports. Configuration can be
    provided via arguments or environment variables.

    Args:
        server: FastMCP server instance. Creates default if None.
        transport: Transport protocol (stdio, http, sse).
        host: Host address for HTTP/SSE transports.
        port: Port number for HTTP/SSE transports.
        path: URL path for HTTP transport.
    """
    settings = MCPSettings()

    mcp_server = server if server is not None else create_mcp_server()

    resolved_transport = transport or settings.transport
    resolved_host = host or settings.host
    resolved_port = port or settings.port
    resolved_path = path or settings.path

    if resolved_transport == MCPTransport.STDIO.value:
        mcp_server.run(transport="stdio")
    elif resolved_transport == MCPTransport.HTTP.value:
        mcp_server.run(transport="http", host=resolved_host, port=resolved_port, path=resolved_path)
    elif resolved_transport == MCPTransport.SSE.value:
        mcp_server.run(transport="sse", host=resolved_host, port=resolved_port)
    else:
        raise ValueError(f"Unsupported transport: {resolved_transport}")


if __name__ == "__main__":
    run_server()
