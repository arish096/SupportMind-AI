import os
from pathlib import Path
from dotenv import load_dotenv

from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StreamableHTTPConnectionParams
)

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

MEKO_API_KEY = os.getenv("MEKO_API_KEY")

if not MEKO_API_KEY:
    raise RuntimeError("MEKO_API_KEY is missing from backend/.env")

MEKO_DATAPACK_ID = "efd952a2-1b39-4276-8cb3-cd874b681537"

meko_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://mcp.mekodata.ai/mcp",
        headers={
            "Authorization": f"Bearer {MEKO_API_KEY}",
            "User-Agent": "SupportMind-AI/1.0"
        },
        timeout=20
    ),
    tool_filter=["context_search"],
    tool_list_cache_ttl_seconds=300
)
