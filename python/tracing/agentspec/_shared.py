"""Shared setup for AgentSpec tracing examples."""

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


EXAMPLE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = EXAMPLE_ROOT.parents[2]
DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai/api"
DEFAULT_MODEL = "gpt-4.1-nano"


def configure_gateway() -> tuple[str, str, str]:
    """Load the repo-root env file and point OpenAI-compatible calls at Respan."""
    load_dotenv(REPO_ROOT / ".env", override=True)

    respan_api_key = os.getenv("RESPAN_GATEWAY_API_KEY") or os.getenv("RESPAN_API_KEY")
    if not respan_api_key:
        raise RuntimeError("RESPAN_GATEWAY_API_KEY or RESPAN_API_KEY is required")

    respan_base_url = (
        os.getenv("RESPAN_GATEWAY_BASE_URL")
        or os.getenv("RESPAN_BASE_URL")
        or DEFAULT_RESPAN_BASE_URL
    )
    model = os.getenv("RESPAN_MODEL", DEFAULT_MODEL)

    os.environ["OPENAI_API_KEY"] = respan_api_key
    os.environ["OPENAI_BASE_URL"] = respan_base_url
    return respan_api_key, respan_base_url, model


def latest_message_content(result: dict[str, Any]) -> str:
    """Extract the final assistant message text from a LangGraph AgentSpec run."""
    messages = result.get("messages", [])
    if not messages:
        return ""

    latest_message = messages[-1]
    content = getattr(latest_message, "content", None)
    if content is None and isinstance(latest_message, dict):
        content = latest_message.get("content")
    return str(content or "")
