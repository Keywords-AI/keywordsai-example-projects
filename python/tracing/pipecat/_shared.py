"""Shared helpers for Pipecat tracing examples."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from dotenv import load_dotenv
from respan import Respan
from respan_instrumentation_pipecat import PipecatInstrumentor

EXAMPLE_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXAMPLE_DIR.parents[2]
DEFAULT_BASE_URL = "https://api.respan.ai/api"
DEFAULT_MODEL = "gpt-4.1-nano"
EXAMPLE_SET = "pipecat"


def load_example_env() -> None:
    load_dotenv(REPO_ROOT / ".env", override=False)
    if not os.getenv("RESPAN_API_KEY"):
        raise RuntimeError(f"RESPAN_API_KEY is required in {REPO_ROOT / '.env'}")
    os.environ.setdefault("RESPAN_BASE_URL", DEFAULT_BASE_URL)


def marker() -> str:
    return os.getenv("RESPAN_EXAMPLE_RUN_ID", "").strip() or (
        f"pipecat-{uuid4().hex[:10]}"
    )


def execution_id() -> str:
    return uuid4().hex[:10]


def gateway_config() -> dict[str, str] | None:
    api_key = os.getenv("RESPAN_GATEWAY_API_KEY") or os.getenv("RESPAN_API_KEY")
    base_url = os.getenv("RESPAN_GATEWAY_BASE_URL") or os.getenv("RESPAN_BASE_URL")
    if not api_key or not base_url:
        return None
    return {
        "api_key": api_key,
        "base_url": base_url,
        "model": os.getenv("RESPAN_MODEL", DEFAULT_MODEL),
    }


def create_respan(workflow_name: str, run_marker: str) -> Respan:
    load_example_env()
    return Respan(
        api_key=os.environ["RESPAN_API_KEY"],
        base_url=os.getenv("RESPAN_BASE_URL", DEFAULT_BASE_URL),
        app_name=workflow_name,
        metadata={
            "example_set": EXAMPLE_SET,
            "workflow_name": workflow_name,
            "example_run_id": run_marker,
            "run_id": run_marker,
        },
        instrumentations=[PipecatInstrumentor()],
        is_batching_enabled=False,
        log_level=os.getenv("RESPAN_LOG_LEVEL", "WARNING"),
    )


def workflow_attributes(
    workflow_name: str,
    run_marker: str,
    execution: str,
    *,
    mode: str,
) -> dict[str, object]:
    return {
        "trace_group_identifier": workflow_name,
        "custom_identifier": f"{workflow_name}-{execution}",
        "metadata": {
            "example_set": EXAMPLE_SET,
            "workflow_name": workflow_name,
            "example_run_id": run_marker,
            "run_id": run_marker,
            "execution_id": execution,
            "mode": mode,
        },
    }


def print_result(label: str, value: Any, run_marker: str) -> None:
    print(f"RESPAN_EXAMPLE_RUN_ID={run_marker}")
    print(f"\n== {label} ==")
    print(json.dumps(value, allow_nan=False, indent=2, sort_keys=True))


def finish_respan(respan: Respan) -> None:
    try:
        respan.flush()
    finally:
        respan.shutdown()
