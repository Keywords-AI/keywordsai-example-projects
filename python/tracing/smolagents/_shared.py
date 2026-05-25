"""Shared setup for smolagents Respan examples."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from respan import Respan
from respan_instrumentation_smolagents import SmolagentsInstrumentor
from smolagents import LiteLLMModel

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env", override=True)

DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai/api"
DEFAULT_CUSTOMER_IDENTIFIER = "smolagents-example-user"
DEFAULT_RUN_ID = datetime.now(timezone.utc).strftime("smolagents-%Y%m%d-%H%M%S")


def _required_env(name: str, fallback_name: str | None = None) -> str:
    value = os.getenv(name)
    if value:
        return value
    if fallback_name:
        fallback_value = os.getenv(fallback_name)
        if fallback_value:
            return fallback_value
    raise RuntimeError(
        f"Missing {name} in {REPO_ROOT / '.env'}"
        + (f" or {fallback_name}" if fallback_name else "")
    )


def _gateway_model_id() -> str:
    model = os.getenv("RESPAN_MODEL", "gpt-4o-mini")
    if "/" in model:
        return model
    return f"openai/{model}"


def build_model() -> LiteLLMModel:
    gateway_api_key = _required_env("RESPAN_GATEWAY_API_KEY", "RESPAN_API_KEY")
    gateway_base_url = os.getenv(
        "RESPAN_GATEWAY_BASE_URL",
        os.getenv("RESPAN_BASE_URL", DEFAULT_RESPAN_BASE_URL),
    )

    os.environ["OPENAI_API_KEY"] = gateway_api_key
    os.environ["OPENAI_BASE_URL"] = gateway_base_url

    return LiteLLMModel(
        model_id=_gateway_model_id(),
        api_key=gateway_api_key,
        api_base=gateway_base_url,
    )


def build_respan(example_name: str, workflow_name: str) -> Respan:
    trace_api_key = _required_env("RESPAN_API_KEY", "RESPAN_GATEWAY_API_KEY")
    respan_base_url = os.getenv("RESPAN_BASE_URL", DEFAULT_RESPAN_BASE_URL)
    run_id = os.getenv("RESPAN_EXAMPLE_RUN_ID", DEFAULT_RUN_ID)

    return Respan(
        api_key=trace_api_key,
        base_url=respan_base_url,
        app_name=f"smolagents-{example_name}",
        instrumentations=[SmolagentsInstrumentor()],
        customer_identifier=os.getenv(
            "RESPAN_EXAMPLE_CUSTOMER_IDENTIFIER",
            DEFAULT_CUSTOMER_IDENTIFIER,
        ),
        metadata={
            "example": example_name,
            "run_id": run_id,
            "workflow_name": workflow_name,
        },
        environment="examples",
    )
