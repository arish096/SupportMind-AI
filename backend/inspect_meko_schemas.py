import asyncio
import os
import json
from pathlib import Path
import httpx
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

load_dotenv(Path(__file__).resolve().parent / ".env")

async def main():
    key = os.getenv("MEKO_API_KEY")
    if not key:
        print("ERROR: MEKO_API_KEY missing")
        return

    async with httpx.AsyncClient(
        headers={
            "Authorization": f"Bearer {key}",
            "User-Agent": "SupportMind-AI/1.0"
        },
        timeout=20
    ) as client:

        async with streamable_http_client(
            "https://mcp.mekodata.ai/mcp",
            http_client=client
        ) as (read_stream, write_stream):

            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.list_tools()

                targets = {
                    "context_search",
                    "knowledgebase_upload_document",
                    "knowledgebase_document_status"
                }

                for tool in result.tools:
                    if tool.name in targets:
                        print(f"\n--- {tool.name} ---")
                        print(json.dumps(tool.input_schema, indent=2))

                print("\nSCHEMA INSPECTION COMPLETE")

asyncio.run(main())
