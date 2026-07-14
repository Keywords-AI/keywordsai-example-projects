"""Shared helpers for Pinecone tracing examples."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from dotenv import load_dotenv
from pinecone import Pinecone
from respan import Respan
from respan_instrumentation_pinecone import PineconeInstrumentor

EXAMPLE_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXAMPLE_DIR.parents[2]
RESPAN_BASE_URL = "https://api.respan.ai/api"
EXAMPLE_SET = "pinecone"


def load_example_env() -> None:
    env_path = REPO_ROOT / ".env"
    load_dotenv(env_path, override=True)
    required = ["RESPAN_API_KEY", "PINECONE_API_KEY", "PINECONE_INDEX_NAME"]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError(f"Missing {', '.join(missing)} in {env_path}")
    os.environ.setdefault("RESPAN_BASE_URL", RESPAN_BASE_URL)


def create_respan(workflow_name: str) -> Respan:
    load_example_env()
    return Respan(
        api_key=os.environ["RESPAN_API_KEY"],
        base_url=os.getenv("RESPAN_BASE_URL", RESPAN_BASE_URL),
        app_name=workflow_name,
        metadata={"example_set": EXAMPLE_SET, "workflow_name": workflow_name},
        instrumentations=[PineconeInstrumentor()],
        is_batching_enabled=False,
        log_level=os.getenv("RESPAN_LOG_LEVEL", "WARNING"),
    )


def create_pinecone_index():
    client = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    host = os.getenv("PINECONE_INDEX_HOST")
    return client.Index(host=host) if host else client.Index(os.environ["PINECONE_INDEX_NAME"])


def execution_id() -> str:
    prefix = os.getenv("RESPAN_EXAMPLE_RUN_ID", "run")
    safe_prefix = "".join(char if char.isalnum() else "-" for char in prefix)
    return f"{safe_prefix[:24]}-{uuid4().hex[:8]}"


def workflow_attributes(workflow_name: str, run_id: str) -> dict[str, object]:
    return {
        "trace_group_identifier": workflow_name,
        "custom_identifier": f"{workflow_name}-{run_id}",
        "metadata": {
            "example_set": EXAMPLE_SET,
            "workflow_name": workflow_name,
            "example_run_id": run_id,
        },
    }


def response_field(response: Any, name: str, default: Any = None) -> Any:
    if isinstance(response, dict):
        return response.get(name, default)
    return getattr(response, name, default)


def print_result(label: str, value: Any) -> None:
    print(f"\n== {label} ==")
    print(json.dumps(value, default=str, indent=2, sort_keys=True))


def finish_respan(respan: Respan) -> None:
    try:
        respan.flush()
    finally:
        respan.shutdown()
