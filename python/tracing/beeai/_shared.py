"""Shared setup for BeeAI tracing examples."""

import os
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from dotenv import load_dotenv
from respan import Respan, propagate_attributes
from respan_instrumentation_beeai import BeeAIInstrumentor

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai/api"
DEFAULT_BEEAI_MODEL = "openai:gpt-4.1-nano"


def configure_environment() -> tuple[str, str]:
    """Load repo-root env and route BeeAI OpenAI calls through Respan."""
    load_dotenv(REPO_ROOT / ".env", override=True)

    respan_api_key = os.environ["RESPAN_API_KEY"]
    respan_base_url = os.getenv("RESPAN_BASE_URL", DEFAULT_RESPAN_BASE_URL)

    os.environ["OPENAI_API_KEY"] = respan_api_key
    os.environ["OPENAI_API_BASE"] = respan_base_url
    os.environ["OPENAI_BASE_URL"] = respan_base_url

    return respan_api_key, respan_base_url


def create_respan(app_name: str) -> Respan:
    """Create Respan with BeeAI instrumentation activated."""
    respan_api_key, respan_base_url = configure_environment()
    return Respan(
        app_name=app_name,
        api_key=respan_api_key,
        base_url=respan_base_url,
        instrumentations=[BeeAIInstrumentor()],
    )


def get_default_model() -> str:
    """Return the BeeAI model after repo-root env vars have been loaded."""
    return os.getenv("BEEAI_MODEL", DEFAULT_BEEAI_MODEL)


@contextmanager
def example_attributes(workflow_name: str) -> Iterator[str]:
    """Attach searchable identifiers to all spans emitted by one example run."""
    run_id = os.getenv("RESPAN_EXAMPLE_RUN_ID", f"beeai-{uuid.uuid4().hex[:10]}")
    with propagate_attributes(
        group_identifier=workflow_name,
        custom_identifier=run_id,
        metadata={
            "framework": "beeai",
            "example": workflow_name,
            "run_id": run_id,
        },
    ):
        yield run_id
