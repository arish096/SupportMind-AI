
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from .memory_store import (
    save_customer_memory,
    search_customer_memory,
    search_shared_knowledge
)

memory_agent = Agent(
    name="memory_agent",

    model=LiteLlm(
        model="openrouter/openrouter/free"
    ),

    description=(
        "Searches customer history and shared "
        "verified support knowledge."
    ),

    instruction="""
You are the Memory Agent of SupportMind AI.

CUSTOMER ANALYSIS:
{customer_analysis}

Your responsibilities:

1. Identify the customer ID and issue.
2. Search the customer's previous history using
   search_customer_memory.
3. Search approved shared solutions using
   search_shared_knowledge.
4. Clearly distinguish customer history from shared knowledge.
5. Never invent previous conversations or solutions.
6. Never treat unapproved resolutions as verified.
7. Never save passwords, API keys or payment credentials.
8. If no matching memory exists, say so clearly.

Call both search tools before returning your result.

Return ONLY this format:

Customer ID:
Previous Customer History:
Matching Shared Knowledge:
Relevant Verified Solutions:
Memory Status:
Additional Context for Resolution Agent:

Keep the response concise.
""",

    tools=[
        search_customer_memory,
        search_shared_knowledge,
        save_customer_memory
    ],

    output_key="customer_memory"
)
