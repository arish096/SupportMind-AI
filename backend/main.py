
import time
from uuid import uuid4
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / ".env")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from google.genai import types

from support_agents import root_agent
from support_agents.memory_store import (
    create_support_ticket,
    get_support_tickets,
    review_support_ticket,
    get_performance_metrics,
)


def clean_review_response(response: str) -> str:
    marker = "Review Status:"
    position = response.rfind(marker)

    if position != -1:
        return response[position:].strip()

    return (
        "Review Status: Needs Improvement\n\n"
        "Accuracy: The response could not be reviewed reliably.\n"
        "Completeness: Further review is required.\n"
        "Safety: No unverified claims should be made.\n"
        "Clarity: The response needs further review.\n"
        "Professionalism: A human review is recommended.\n\n"
        "Suggested Improvements:\n"
        "- Review the proposed resolution.\n\n"
        "Final Customer Response:\n"
        "We are reviewing your request. Please provide the "
        "required information so we can assist you."
    )


app = FastAPI(
    title="SupportMind AI",
    description="Multi-Agent Customer Support System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

adk_app = App(name="supportmind_ai", root_agent=root_agent)
runner = InMemoryRunner(app=adk_app)


class ChatRequest(BaseModel):
    customer_id: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=5000)


class ReviewRequest(BaseModel):
    approved: bool
    reviewer: str = Field(default="Human Reviewer", max_length=100)


@app.get("/")
async def home():
    return {
        "message": "Welcome to SupportMind AI",
        "status": "running",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "agents": [
            "customer_agent",
            "memory_agent",
            "resolution_agent",
            "review_agent",
        ],
    }


@app.post("/chat")
async def chat(request: ChatRequest):
    start_time = time.perf_counter()

    user_id = request.customer_id
    session_id = str(uuid4())

    await runner.session_service.create_session(
        app_name=adk_app.name,
        user_id=user_id,
        session_id=session_id,
    )

    customer_message = (
        f"Customer ID: {request.customer_id}\n"
        f"Customer Query: {request.message}"
    )

    message = types.Content(
        role="user",
        parts=[types.Part.from_text(text=customer_message)],
    )

    final_response = ""

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=message,
    ):
        if (
            event.author == "review_agent"
            and event.is_final_response()
            and event.content
            and event.content.parts
        ):
            final_response = "".join(
                part.text or "" for part in event.content.parts
            )

    if not final_response:
        raise HTTPException(
            status_code=500,
            detail="AI workflow did not return a final response.",
        )

    # Remove internal analysis before saving or returning.
    final_response = clean_review_response(final_response)

    response_time_ms = (time.perf_counter() - start_time) * 1000

    ticket_id = create_support_ticket(
        request.customer_id,
        request.message,
        final_response,
        response_time_ms,
    )

    return {
        "status": "success",
        "customer_id": request.customer_id,
        "ticket_id": ticket_id,
        "session_id": session_id,
        "review_status": "pending_review",
        "response": final_response,
    }


@app.get("/tickets")
async def tickets():
    return {
        "status": "success",
        "tickets": get_support_tickets(),
    }


@app.post("/tickets/{ticket_id}/review")
async def review_ticket(ticket_id: int, request: ReviewRequest):
    result = review_support_ticket(
        ticket_id,
        request.approved,
        request.reviewer,
    )

    return {
        "status": "success",
        "ticket_id": ticket_id,
        "review_result": result,
    }


@app.get("/analytics")
async def analytics():
    return {
        "status": "success",
        "analytics": get_performance_metrics(),
    }
