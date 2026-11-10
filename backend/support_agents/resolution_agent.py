
import os
from pathlib import Path
from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

load_dotenv(
    Path(__file__).resolve().parents[1] / ".env"
)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in .env")


resolution_agent = Agent(
    name="resolution_agent",

    model=LiteLlm(
        model="openrouter/openrouter/free",
        api_key=OPENROUTER_API_KEY
    ),

    description=(
        "Resolves customer support issues using "
        "customer history and verified shared knowledge."
    ),

    instruction="""
You are the Resolution Agent of SupportMind AI.

CUSTOMER ANALYSIS:
{customer_analysis}

CUSTOMER HISTORY AND SHARED KNOWLEDGE:
{customer_memory}

Your responsibilities:

1. Understand the customer's issue.
2. Review previous customer history.
3. Check matching approved shared solutions.
4. Reuse a verified solution when it genuinely matches.
5. Adapt previous solutions to the current customer's situation.
6. If no relevant solution exists, suggest a new practical resolution.
7. Never treat unapproved suggestions as verified solutions.
8. Never invent transaction details or customer information.
9. Ask for missing information when necessary.
10. Never claim that payment or order verification happened
    without actual verification.

Response Format:

Issue:
Likely Cause:
Previous Solution Used:
Recommended Resolution:
Required Information:
Customer Response:

Keep the response concise and professional.
""",

    output_key="resolution_result"
)
