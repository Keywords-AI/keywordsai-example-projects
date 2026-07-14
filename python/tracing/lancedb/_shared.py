"""Shared setup for the LanceDB tracing example."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from dotenv import load_dotenv
from respan import Respan
from respan_instrumentation_lancedb import LanceDBInstrumentor

EXAMPLE_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXAMPLE_DIR.parents[2]
RESPAN_BASE_URL = "https://api.respan.ai/api"
EXAMPLE_SET = "lancedb"


def create_respan(workflow_name: str) -> Respan:
    env_path = REPO_ROOT / ".env"
    load_dotenv(env_path, override=True)
    if not os.getenv("RESPAN_API_KEY"):
        raise RuntimeError(f"RESPAN_API_KEY is required in {env_path}")

    return Respan(
        api_key=os.environ["RESPAN_API_KEY"],
        base_url=os.getenv("RESPAN_BASE_URL", RESPAN_BASE_URL),
        app_name=workflow_name,
        metadata={"example_set": EXAMPLE_SET, "workflow_name": workflow_name},
        instrumentations=[LanceDBInstrumentor()],
        is_batching_enabled=False,
        log_level=os.getenv("RESPAN_LOG_LEVEL", "WARNING"),
    )


def workflow_attributes(workflow_name: str) -> dict[str, object]:
    run_id = os.getenv("RESPAN_EXAMPLE_RUN_ID") or uuid4().hex[:8]
    return {
        "trace_group_identifier": workflow_name,
        "custom_identifier": f"{workflow_name}-{run_id}",
        "metadata": {
            "example_set": EXAMPLE_SET,
            "workflow_name": workflow_name,
            "example_run_id": run_id,
        },
    }


def print_result(workflow_name: str, result: Any) -> None:
    print(f"\n== {workflow_name} ==")
    print(json.dumps(result, default=str, indent=2, sort_keys=True))


def finish_respan(respan: Respan) -> None:
    try:
        respan.flush()
    finally:
        respan.shutdown()
