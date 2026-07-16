"""Shared setup for Microsoft Agent Framework tracing examples."""

import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from respan import Respan
from respan_instrumentation_microsoft_agent_framework import (
    MicrosoftAgentFrameworkInstrumentor,
)


EXAMPLE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = EXAMPLE_ROOT.parents[2]
DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai/api"
DEFAULT_MODEL = "gpt-4.1-nano"
DEFAULT_RUN_ID = datetime.now(timezone.utc).strftime("microsoft-agent-framework-%Y%m%d-%H%M%S")


def load_gateway_env() -> tuple[str, str, str]:
    """Load the repo-root env file and configure OpenAI-compatible gateway env."""
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
    os.environ["OPENAI_MODEL"] = model
    os.environ["OPENAI_CHAT_MODEL"] = model
    os.environ["OPENAI_MODEL_ID"] = model
    os.environ["OPENAI_CHAT_MODEL_ID"] = model
    return respan_api_key, respan_base_url, model


def create_openai_chat_client():
    """Create a chat-completions Agent Framework OpenAI client."""
    from agent_framework.openai import OpenAIChatCompletionClient

    respan_api_key, respan_base_url, model = load_gateway_env()
    return OpenAIChatCompletionClient(
        api_key=respan_api_key,
        base_url=respan_base_url,
        model=model,
    )


def create_respan(app_name: str) -> Respan:
    respan_api_key, respan_base_url, _model = load_gateway_env()
    run_id = os.getenv("RESPAN_EXAMPLE_RUN_ID", DEFAULT_RUN_ID)
    return Respan(
        api_key=respan_api_key,
        base_url=respan_base_url,
        app_name=app_name,
        instrumentations=[
            MicrosoftAgentFrameworkInstrumentor(capture_content=True),
        ],
        metadata={
            "integration": "microsoft-agent-framework",
            "example": app_name,
            "run_id": run_id,
        },
        environment="examples",
    )
