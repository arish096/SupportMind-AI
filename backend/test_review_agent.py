import asyncio
from dotenv import load_dotenv

load_dotenv()

from google.adk.runners import InMemoryRunner
from support_agents.review_agent import review_agent


async def main():
    runner = InMemoryRunner(agent=review_agent)

    print("\n--- SupportMind AI Review Agent ---\n")

    await runner.run_debug(
        """
        Review this customer support resolution.

        Customer Issue:
        Payment was deducted but order status is pending.

        Proposed Resolution:
        Ask the customer for their order ID and
        transaction ID. Verify payment status with
        the payment provider and update the order
        status after confirmation.
        """
    )


if __name__ == "__main__":
    asyncio.run(main())