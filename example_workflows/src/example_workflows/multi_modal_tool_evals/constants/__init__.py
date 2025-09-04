import os
from dotenv import load_dotenv

load_dotenv(override=True)

KEYWORDSAI_BASE_URL = os.getenv("KEYWORDSAI_BASE_URL")
KEYWORDSAI_API_KEY = os.getenv("KEYWORDSAI_API_KEY")
KEYWORDSAI_BASE_HEADERS = {
    "Authorization": f"Bearer {KEYWORDSAI_API_KEY}",
    "Content-Type": "application/json",
}

EVALUATION_IDENTIFIER = "traveling_agent_eval"
