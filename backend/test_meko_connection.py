import asyncio
import os
from dotenv import load_dotenv
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

load_dotenv()

async def main():
    api_key = os.getenv("MEKO_API_KEY")

    if not api_key:
        print("ERROR: MEKO_API_KEY not found")
        return

    toolset = McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            url="https://mcp.mekodata.ai/mcp",
            headers={
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "SupportMind-AI/1.0"
            },
            timeout=20
        )
    )

    try:
        tools = await toolset.get_tools()
        print("MEKO CONNECTION SUCCESS!")
        print("Available tools:")
        for tool in tools:
            print("-", tool.name)
    except Exception as e:
        print("CONNECTION FAILED:", type(e).__name__, str(e))
    finally:
        await toolset.close()

asyncio.run(main())
