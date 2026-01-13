# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""MCP (Model Context Protocol) server for Voogle.

This module provides an MCP server implementation using FastMCP,
enabling AI assistants to interact with Voogle's semantic search
capabilities through a standardized protocol.
"""

from voogle.mcp.server import create_mcp_server

__all__ = ["create_mcp_server"]
