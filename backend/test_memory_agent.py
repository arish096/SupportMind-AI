
import asyncio
from dotenv import load_dotenv

load_dotenv()

from google.adk.runners import InMemoryRunner
from support_agents.memory_agent import memory_agent


async def main():
    runner = InMemoryRunner(agent=memory_agent)

    print("\n--- SupportMind AI Memory Agent ---\n")

    await runner.run_debug(
        """
        Customer ID: CUST-1001

        Save this support history:
        Issue: Customer could not access their account.
        Resolution: Account access was restored after
        the customer completed the standard verification.

        Confirm that the memory was saved.
        """
    )

    print("\n--- Searching Customer History ---\n")

    await runner.run_debug(
        """
        Search previous support history for CUST-1001.
        Summarize the previous issue and resolution.
        """
    )


if __name__ == "__main__":
    asyncio.run(main())
