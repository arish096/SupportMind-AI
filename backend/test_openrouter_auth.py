import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from litellm import acompletion

load_dotenv(Path(__file__).resolve().parent / ".env")

async def main():
    api_key = os.getenv("OPENROUTER_API_KEY")

    try:
        response = await acompletion(
            model="openrouter/openrouter/free",
            api_key=api_key,
            messages=[
                {"role": "user", "content": "Reply with: OpenRouter connected"}
            ],
        )

        print("SUCCESS!")
        print(response.choices[0].message.content)

    except Exception as e:
        print("FAILED:", type(e).__name__)
        print(str(e))

if __name__ == "__main__":
    asyncio.run(main())