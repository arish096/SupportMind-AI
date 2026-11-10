
import asyncio
from dotenv import load_dotenv

load_dotenv()

from google.adk.runners import InMemoryRunner
from support_agents import root_agent


async def main():
    runner = InMemoryRunner(agent=root_agent)

    print("\n--- SupportMind AI Customer Agent ---\n")

    await runner.run_debug(
        "My payment was deducted but my order "
        "still shows pending. Please help."
    )


if __name__ == "__main__":
    asyncio.run(main())
