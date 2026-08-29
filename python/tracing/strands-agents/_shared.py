"""Shared helpers for Strands Agents tracing examples."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from respan import Respan
from respan_instrumentation_strands_agents import StrandsAgentsInstrumentor
from strands.models.openai import OpenAIModel

EXAMPLE_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXAMPLE_DIR.parents[2]


def load_example_environment() -> tuple[str, str, str]:
    invocation_marker = os.getenv("RESPAN_EXAMPLE_RUN_ID")
    load_dotenv(REPO_ROOT / ".env", override=False)
    if invocation_marker:
        os.environ["RESPAN_EXAMPLE_RUN_ID"] = invocation_marker
    respan_api_key = os.environ["RESPAN_API_KEY"]
    respan_base_url = os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api").rstrip(
        "/"
    )
    model_id = os.getenv("RESPAN_STRANDS_MODEL", "gpt-4o-mini")
    return respan_api_key, respan_base_url, model_id


def create_gateway_model(
    *, model_id: str | None = None, base_url: str | None = None
) -> OpenAIModel:
    respan_api_key, respan_base_url, default_model_id = load_example_environment()
    return OpenAIModel(
        model_id=model_id or default_model_id,
        client_args={
            "api_key": respan_api_key,
            "base_url": base_url or respan_base_url,
            "max_retries": 0,
            "timeout": 15,
        },
    )


def create_respan(example_name: str, run_id: str) -> Respan:
    respan_api_key, respan_base_url, _ = load_example_environment()
    return Respan(
        api_key=respan_api_key,
        base_url=respan_base_url,
        app_name=f"strands-agents-{example_name}",
        instrumentations=[StrandsAgentsInstrumentor()],
        metadata={
            "example": example_name,
            "run_id": run_id,
            "example_run_id": run_id,
            "example_set": "strands-agents",
            "framework": "strands-agents",
        },
        environment="examples",
    )


def new_run_id(example_name: str) -> str:
    return os.getenv("RESPAN_EXAMPLE_RUN_ID", f"strands-{example_name}-local")


def finish_respan(respan: Respan) -> None:
    try:
        respan.flush()
    finally:
        respan.shutdown()
