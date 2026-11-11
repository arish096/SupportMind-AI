from pathlib import Path
import os
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

key = os.getenv("MEKO_API_KEY")
datapack_id = "efd952a2-1b39-4276-8cb3-cd874b681537"

if not key:
    print("ERROR: MEKO_API_KEY not found in .env")
    raise SystemExit(1)

request = urllib.request.Request(
    f"https://api.mekodata.ai/api/v1/datapacks/{datapack_id}",
    headers={
        "Authorization": f"Bearer {key}",
        "User-Agent": "SupportMind-AI/1.0"
    }
)

try:
    with urllib.request.urlopen(request, timeout=20) as response:
        data = json.loads(response.read().decode())
        print("DATAPACK VERIFIED!")
        print(json.dumps(data, indent=2))
except Exception as error:
    print("VERIFICATION FAILED:", error)
