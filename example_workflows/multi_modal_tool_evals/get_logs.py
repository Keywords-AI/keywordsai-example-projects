import os
import json
import requests
from dotenv import load_dotenv
from constants import EVALUATION_IDENTIFIER

load_dotenv(override=True)

KEYWORDSAI_BASE_URL = os.getenv("KEYWORDSAI_BASE_URL")
KEYWORDSAI_API_KEY = os.getenv("KEYWORDSAI_API_KEY")


def get_logs():
    url = KEYWORDSAI_BASE_URL + "/request-logs/list"
    headers = {
        "Authorization": f"Bearer {KEYWORDSAI_API_KEY}",
        "Content-Type": "application/json",
    }
    response = requests.post(
        url,
        headers=headers,
        json={"filters": {"evaluation_identifier": {"value": EVALUATION_IDENTIFIER}}},
    )
    response_data = response.json()
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        print(f"Response: {response_data}")
        return None
    return json.dumps(response_data, indent=4)


if __name__ == "__main__":
    logs = get_logs()
    with open("logs.json", "w") as f:
        f.write(logs)
