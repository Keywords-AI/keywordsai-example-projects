"""Shared setup for Superagent tracing examples."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import find_dotenv, load_dotenv


@dataclass(frozen=True)
class ExampleConfig:
    respan_api_key: str
    respan_base_url: str
    model: str


def configure_environment() -> ExampleConfig:
    """Load repo-root `.env` and configure Superagent's provider env vars."""
    invocation_marker = os.getenv("RESPAN_EXAMPLE_RUN_ID")
    load_dotenv(find_dotenv(), override=False)
    if invocation_marker:
        os.environ["RESPAN_EXAMPLE_RUN_ID"] = invocation_marker

    respan_api_key = os.environ["RESPAN_API_KEY"]
    respan_base_url = os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api")
    gateway_api_key = os.getenv("RESPAN_GATEWAY_API_KEY", respan_api_key)
    gateway_base_url = os.getenv("RESPAN_GATEWAY_BASE_URL", respan_base_url)

    os.environ.setdefault("SUPERAGENT_API_KEY", "respan-superagent-example")
    os.environ.setdefault("OPENAI_COMPATIBLE_API_KEY", gateway_api_key)
    os.environ.setdefault("OPENAI_COMPATIBLE_BASE_URL", gateway_base_url)
    os.environ.setdefault("OPENAI_COMPATIBLE_SUPPORTS_STRUCTURED_OUTPUT", "true")

    raw_model = os.getenv("SUPERAGENT_MODEL") or os.getenv(
        "RESPAN_MODEL", "gpt-4o-mini"
    )
    model = raw_model if "/" in raw_model else f"openai-compatible/{raw_model}"

    return ExampleConfig(
        respan_api_key=respan_api_key,
        respan_base_url=respan_base_url,
        model=model,
    )


def create_respan(app_name: str = "superagent-example"):
    """Create a Respan client with Superagent instrumentation activated."""
    config = configure_environment()

    from respan import Respan
    from respan_instrumentation_superagent import SuperagentInstrumentor

    marker = os.getenv("RESPAN_EXAMPLE_RUN_ID", "superagent-local")
    return Respan(
        api_key=config.respan_api_key,
        base_url=config.respan_base_url,
        app_name=app_name,
        instrumentations=[SuperagentInstrumentor()],
        metadata={
            "run_id": marker,
            "example_run_id": marker,
            "example_set": "superagent",
            "script": app_name,
        },
        is_batching_enabled=False,
    )


def create_superagent_client():
    """Create the safety-agent client after provider env vars are configured."""
    configure_environment()

    from safety_agent import create_client

    return create_client()


def example_marker() -> str:
    configure_environment()
    return os.getenv("RESPAN_EXAMPLE_RUN_ID", "superagent-local")


def finish_respan(respan) -> None:
    try:
        respan.flush()
    finally:
        respan.shutdown()
