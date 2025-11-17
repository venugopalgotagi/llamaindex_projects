"""MCP client module for retrieving tools from MCP server.

This module provides functionality to connect to an MCP (Model Context Protocol)
server and retrieve available tools for use in PPE workflows.
"""

import logging
import os

import dotenv
from llama_index.tools.mcp import aget_tools_from_mcp_url

logger = logging.getLogger()

dotenv.load_dotenv()


async def get_tools_from_mcp_server():
    """Retrieve tools from the MCP server.

    Connects to the MCP server specified in the MCP_URL environment variable
    and retrieves all available tools. Logs each tool's name for debugging.

    Returns:
        List of tools retrieved from the MCP server.
    """
    tools = await aget_tools_from_mcp_url(
        command_or_url=os.environ.get("MCP_URL")
    )
    for tool in tools:
        print(f"tool:::{tool.metadata.name}")
    return tools
