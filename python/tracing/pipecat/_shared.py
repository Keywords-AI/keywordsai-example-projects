"""Shared setup for Pipecat Respan examples."""

from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from respan import Respan
from respan_instrumentation_pipecat import PipecatInstrumentor

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_BASE_URL = "https://api.respan.ai/api"
DEFAULT_MODEL = "gpt-4.1-nano"


def load_example_env() -> dict[str, str]:
    """Load the example repo-root .env and return normalized settings."""
    load_dotenv(REPO_ROOT / ".env", override=True)

    respan_api_key = os.getenv("RESPAN_API_KEY")
    gateway_api_key = os.getenv("RESPAN_GATEWAY_API_KEY") or respan_api_key
    respan_base_url = os.getenv("RESPAN_BASE_URL", DEFAULT_BASE_URL)
    gateway_base_url = os.getenv("RESPAN_GATEWAY_BASE_URL") or respan_base_url
    model = os.getenv("RESPAN_MODEL", DEFAULT_MODEL)

    if not respan_api_key:
        raise RuntimeError("RESPAN_API_KEY must be set in respan-example-projects/.env")

    if gateway_api_key:
        os.environ["OPENAI_API_KEY"] = gateway_api_key
    os.environ["OPENAI_BASE_URL"] = gateway_base_url

    return {
        "respan_api_key": respan_api_key,
        "respan_base_url": respan_base_url,
        "gateway_api_key": gateway_api_key or "",
        "gateway_base_url": gateway_base_url,
        "model": model,
    }


def create_respan(example_name: str, **metadata: Any) -> tuple[Respan, str]:
    """Create Respan with Pipecat instrumentation and searchable metadata."""
    env = load_example_env()
    run_id = metadata.pop("run_id", uuid.uuid4().hex[:12])

    respan = Respan(
        api_key=env["respan_api_key"],
        base_url=env["respan_base_url"],
        app_name=f"pipecat-{example_name}",
        instrumentations=[PipecatInstrumentor()],
        is_batching_enabled=False,
        customer_identifier="pipecat-example",
        thread_identifier=f"pipecat-{run_id}",
        metadata={
            "example": "pipecat",
            "script": example_name,
            "run_id": run_id,
            **metadata,
        },
        environment="example",
    )
    return respan, run_id
