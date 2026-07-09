"""Shared helpers for Watson Orchestrate ADK Respan examples."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from respan import Respan
DEFAULT_RUN_ID = datetime.now(timezone.utc).strftime("watson-orchestrate-adk-%Y%m%d-%H%M%S")

from respan_instrumentation_watson_orchestrate_adk import (
    WatsonOrchestrateADKInstrumentor,
)


def load_repo_env() -> None:
    """Load environment variables from respan-example-projects/.env."""
    repo_root = Path(__file__).resolve().parents[3]
    load_dotenv(repo_root / ".env", override=True)


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} must be set in respan-example-projects/.env")
    return value


def optional_env(name: str) -> str | None:
    value = os.getenv(name)
    return value if value else None


def create_respan(app_name: str) -> Respan:
    load_repo_env()
    run_id = os.getenv("RESPAN_EXAMPLE_RUN_ID", DEFAULT_RUN_ID)
    return Respan(
        app_name=app_name,
        api_key=require_env("RESPAN_API_KEY"),
        base_url=os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api"),
        instrumentations=[WatsonOrchestrateADKInstrumentor()],
        is_batching_enabled=False,
        metadata={
            "integration": "watson-orchestrate-adk",
            "example": app_name,
            "run_id": run_id,
        },
        environment="examples",
    )
