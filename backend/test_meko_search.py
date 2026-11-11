import asyncio
import os
import json
from uuid import uuid4
from pathlib import Path
from datetime import timedelta
import httpx
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

load_dotenv(Path(__file__).resolve().parent / ".env")

DATAPACK_ID = "efd952a2-1b39-4276-8cb3-cd874b681537"

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
        timeout=30.0
    ) as client:
        async with streamable_http_client(
            "https://mcp.mekodata.ai/mcp",
            http_client=client
        ) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()

                result = await session.call_tool(
                    "context_search",
                    arguments={
                        "query": "Payment deducted but order status is still pending",
                        "conversation_id": str(uuid4()),
                        "datapack_id": DATAPACK_ID,
                        "limit": 5,
                        "force_source": "knowledge_base"
                    }
                )

                print("MEKO SEARCH EXECUTED")
                for item in result.content:
                    if hasattr(item, "text"):
                        print(item.text)
                if result.is_error:
                    print("MEKO SEARCH RETURNED AN ERROR")

asyncio.run(main())
