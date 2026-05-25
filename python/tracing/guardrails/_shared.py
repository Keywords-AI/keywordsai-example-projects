"""Shared setup for Guardrails AI tracing examples."""

import os
from pathlib import Path

from dotenv import load_dotenv


def load_guardrails_example_environment() -> tuple[str, str, str]:
    env_path = Path(__file__).resolve().parents[3] / ".env"
    load_dotenv(env_path, override=True)

    respan_api_key = os.environ["RESPAN_API_KEY"]
    respan_base_url = os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api")
    model = os.getenv("RESPAN_MODEL", "gpt-4o-mini")

    os.environ["OPENAI_API_KEY"] = respan_api_key
    os.environ["OPENAI_BASE_URL"] = respan_base_url
    os.environ["OPENAI_API_BASE"] = respan_base_url

    return respan_api_key, respan_base_url, model
