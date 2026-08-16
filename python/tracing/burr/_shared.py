"""Shared helpers for Apache Burr tracing examples."""

from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Any

from respan import Respan
from respan_instrumentation_burr import BurrInstrumentor

EXAMPLE_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXAMPLE_DIR.parents[2]
ROOT_ENV = REPO_ROOT / ".env"
CUSTOMER_IDENTIFIER = "burr-example"


def load_repo_env() -> None:
    if not ROOT_ENV.exists():
        return
    for raw_line in ROOT_ENV.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ[key.strip()] = value.strip().strip("'").strip('"')


def new_run_id(example_name: str) -> str:
    return os.getenv("RESPAN_EXAMPLE_RUN_ID") or f"{example_name}-{uuid.uuid4().hex[:10]}"


def create_respan(*, workflow_name: str, run_id: str, example_name: str) -> Respan:
    load_repo_env()
    return Respan(
        api_key=os.getenv("RESPAN_API_KEY") or os.getenv("RESPAN_GATEWAY_API_KEY"),
        base_url=os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api"),
        app_name="burr-example",
        instrumentations=[BurrInstrumentor()],
        customer_identifier=CUSTOMER_IDENTIFIER,
        metadata={
            "example_set": "burr",
            "example_name": example_name,
            "workflow_name": workflow_name,
            "run_id": run_id,
        },
        environment="example",
        is_batching_enabled=False,
    )


def workflow_context(
    respan: Respan,
    *,
    workflow_name: str,
    run_id: str,
    example_name: str,
) -> Any:
    return respan.propagate_attributes(
        group_identifier=workflow_name,
        custom_identifier=run_id,
        metadata={
            "example_set": "burr",
            "example_name": example_name,
            "workflow_name": workflow_name,
            "run_id": run_id,
        },
    )


def print_trace_lookup(*, workflow_name: str, run_id: str) -> None:
    print(f"workflow_name={workflow_name}")
    print(f"RESPAN_EXAMPLE_RUN_ID={run_id}")
