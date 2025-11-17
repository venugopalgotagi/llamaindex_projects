import logging
import os

import dotenv
from llama_index.tools.mcp import (
    aget_tools_from_mcp_url
)

logger = logging.getLogger()

dotenv.load_dotenv()

async def get_tools_from_mcp_server():
    tools =  await aget_tools_from_mcp_url(command_or_url=os.environ.get("MCP_URL"))
    for tool in tools:
        print(f"tool:::{tool.metadata.name}")
    return tools

