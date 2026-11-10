
import os
from dotenv import load_dotenv
from litellm import completion

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError("OpenRouter API key missing in .env")

response = completion(
    model="openrouter/openrouter/free",
    messages=[
        {
            "role": "user",
            "content": "You are SupportMind AI. Introduce yourself in two sentences."
        }
    ],
    api_key=api_key
)

print("\nSupportMind AI Response:\n")
print(response.choices[0].message.content)
