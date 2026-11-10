import asyncio
from dotenv import load_dotenv

# Load .env before importing agents
load_dotenv()

from google.adk.runners import InMemoryRunner
from support_agents.resolution_agent import resolution_agent


async def main():
    runner = InMemoryRunner(agent=resolution_agent)

    print("\n--- SupportMind AI Resolution Agent ---\n")

    await runner.run_debug(
        "Analyze this customer support case:\n"
        "Customer ID: CUST-1001\n"
        "Category: Billing Issue\n"
        "Urgency: Medium\n"
        "Issue: Payment was deducted but the order status is still pending.\n"
        "Missing Information: Order ID, transaction ID, transaction timestamp.\n"
        "Suggest a suitable resolution."
    )


if __name__ == "__main__":
    asyncio.run(main())