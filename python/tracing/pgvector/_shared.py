"""Shared setup for PGVector tracing examples."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from dotenv import load_dotenv
from respan import Respan
from respan_instrumentation_pgvector import PGVectorInstrumentor

EXAMPLE_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXAMPLE_DIR.parents[2]
RESPAN_BASE_URL = "https://api.respan.ai/api"
EXAMPLE_SET = "pgvector"


def load_repo_env() -> None:
    env_path = REPO_ROOT / ".env"
    load_dotenv(env_path, override=False)


def load_example_env() -> None:
    env_path = REPO_ROOT / ".env"
    load_repo_env()
    if not os.getenv("RESPAN_API_KEY"):
        raise RuntimeError(f"RESPAN_API_KEY is required in {env_path}")
    os.environ.setdefault("RESPAN_BASE_URL", RESPAN_BASE_URL)


def run_id() -> str:
    configured = os.getenv("RESPAN_EXAMPLE_RUN_ID", "").strip()
    return configured or f"pgvector-{uuid4().hex[:10]}"


def create_respan(workflow_name: str, marker: str) -> Respan:
    load_example_env()
    return Respan(
        api_key=os.environ["RESPAN_API_KEY"],
        base_url=os.getenv("RESPAN_BASE_URL", RESPAN_BASE_URL),
        app_name=workflow_name,
        metadata={
            "example_run_id": marker,
            "run_id": marker,
            "example_set": EXAMPLE_SET,
            "workflow_name": workflow_name,
        },
        instrumentations=[PGVectorInstrumentor()],
        is_batching_enabled=False,
        log_level=os.getenv("RESPAN_LOG_LEVEL", "WARNING"),
    )


def workflow_attributes(workflow_name: str, marker: str) -> dict[str, object]:
    return {
        "trace_group_identifier": workflow_name,
        "custom_identifier": f"{workflow_name}-{marker}",
        "metadata": {
            "example_run_id": marker,
            "run_id": marker,
            "example_set": EXAMPLE_SET,
            "workflow_name": workflow_name,
        },
    }


def print_result(label: str, value: Any, marker: str) -> None:
    print(f"RESPAN_EXAMPLE_RUN_ID={marker}")
    print(f"\n== {label} ==")
    print(json.dumps(value, allow_nan=False, indent=2, sort_keys=True))


def finish_respan(respan: Respan) -> None:
    try:
        respan.flush()
    finally:
        respan.shutdown()
