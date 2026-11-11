from __future__ import annotations

import os
import re
import json
import base64
import hashlib
import traceback
from uuid import uuid4
from pathlib import Path

import httpx
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from .memory_store import (
    get_approved_ticket,
    claim_meko_sync,
    update_meko_sync,
)

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

MEKO_URL = "https://mcp.mekodata.ai/mcp"
DATAPACK_ID = "efd952a2-1b39-4276-8cb3-cd874b681537"


def sanitize(text: str) -> str:
    text = re.sub(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        "[REDACTED_EMAIL]", text
    )
    text = re.sub(
        r"(?i)(password|api[_ -]?key|secret|token)\s*[:=]\s*\S+",
        r"\1: [REDACTED]", text
    )
    text = re.sub(
        r"(?<!\w)\+?\d[\d\s().-]{8,}\d(?!\w)",
        "[REDACTED_NUMBER]", text
    )
    return text.strip()


def parse_tool_result(result):
    if getattr(result, "is_error", False):
        raise RuntimeError("Meko upload tool returned an error.")

    structured = getattr(result, "structuredContent", None)
    if structured is None:
        structured = getattr(result, "structured_content", None)

    value = structured

    if value is None:
        text_parts = [
            item.text for item in (result.content or [])
            if getattr(item, "text", None)
        ]
        value = "\n".join(text_parts)

    for _ in range(3):
        if isinstance(value, dict):
            if "result" in value:
                value = value["result"]
                continue
            return value

        if isinstance(value, str):
            try:
                value = json.loads(value)
                continue
            except json.JSONDecodeError:
                break

        break

    raise RuntimeError("Could not parse Meko upload response.")


async def publish_approved_ticket(ticket_id: int):
    ticket = get_approved_ticket(ticket_id)

    if not ticket:
        return {"status": "not_approved"}

    if not claim_meko_sync(ticket_id):
        return {"status": "already_processing_or_synced"}

    try:
        issue = sanitize(ticket["issue"])
        resolution = sanitize(ticket["resolution"])

        document = (
            f"# Verified Support Resolution\\n\\n"
            f"## Issue\\n{issue}\\n\\n"
            f"## Human-Approved Resolution\\n{resolution}\\n"
        )

        content = document.encode("utf-8")
        filename = f"support-ticket-{ticket_id}.md"
        content_hash = hashlib.sha256(content).hexdigest()

        # Check S3 reachability before requesting an upload URL.
        async with httpx.AsyncClient(timeout=10.0) as s3_client:
            await s3_client.get("https://s3.amazonaws.com")

        api_key = os.getenv("MEKO_API_KEY")
        if not api_key:
            raise RuntimeError("MEKO_API_KEY is missing.")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "SupportMind-AI/1.0",
        }

        async with httpx.AsyncClient(
            timeout=30.0, headers=headers
        ) as client:
            async with streamable_http_client(
                MEKO_URL, http_client=client
            ) as (read_stream, write_stream):
                async with ClientSession(
                    read_stream, write_stream
                ) as session:
                    await session.initialize()

                    upload = await session.call_tool(
                        "knowledgebase_upload_document",
                        arguments={
                            "filename": filename,
                            "size": len(content),
                            "content_hash": content_hash,
                            "conversation_id": str(uuid4()),
                            "content_head_base64": base64.b64encode(
                                content[:3072]
                            ).decode("ascii"),
                            "datapack_id": DATAPACK_ID,
                        },
                    )

                    payload = parse_tool_result(upload)

                    if payload.get("already_uploaded"):
                        update_meko_sync(
                            ticket_id, "already_uploaded",
                            document_key=payload.get("key")
                        )
                        return {"status": "already_uploaded"}

                    upload_url = payload.get("url")
                    fields = payload.get("fields")
                    document_key = payload.get("key")

                    if not upload_url or not isinstance(fields, dict):
                        raise RuntimeError(
                            "Meko did not return a valid upload URL and fields."
                        )

                    if not document_key:
                        raise RuntimeError(
                            "Meko upload response did not contain a document key."
                        )

                    # Multipart fields first, file bytes last.
                    multipart = [
                        (str(key), (None, str(value)))
                        for key, value in fields.items()
                    ]
                    multipart.append((
                        "file",
                        (filename, content, "text/markdown")
                    ))

                    async with httpx.AsyncClient(timeout=60.0) as s3_client:
                        response = await s3_client.post(
                            upload_url,
                            files=multipart,
                        )

                    if not response.is_success:
                        print("S3 STATUS:", response.status_code, flush=True)
                        print("S3 ERROR BODY:", response.text[:3000], flush=True)
                        raise RuntimeError(
                            f"S3 upload failed ({response.status_code}): "
                            f"{response.text[:2000]}"
                        )

        update_meko_sync(
            ticket_id,
            "uploaded",
            document_key=document_key,
        )

        return {
            "status": "uploaded",
            "document_key": document_key,
        }

    except Exception as exc:
        import traceback
        print("MEKO FULL ERROR:", repr(exc), flush=True)
        traceback.print_exception(type(exc), exc, exc.__traceback__)
        details = "".join(traceback.format_exception(exc))
        update_meko_sync(ticket_id, "failed", error=details[-3000:])
        return {"status": "failed", "error": details[-3000:]}
