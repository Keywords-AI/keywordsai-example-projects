"""Shared helpers for Pinecone tracing examples."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from _loopback import loopback_host, shutdown_loopback
from dotenv import load_dotenv
from pinecone import Index
from pinecone.async_client.async_index import AsyncIndex
from respan import Respan
from respan_instrumentation_pinecone import PineconeInstrumentor

EXAMPLE_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXAMPLE_DIR.parents[2]
RESPAN_BASE_URL = "https://api.respan.ai/api"
EXAMPLE_SET = "pinecone"


def load_example_env() -> None:
    load_dotenv(REPO_ROOT / ".env", override=False)
    if not os.getenv("RESPAN_API_KEY"):
        raise RuntimeError(f"RESPAN_API_KEY is required in {REPO_ROOT / '.env'}")
    os.environ.setdefault("RESPAN_BASE_URL", RESPAN_BASE_URL)


def marker() -> str:
    return os.getenv("RESPAN_EXAMPLE_RUN_ID", "").strip() or (
        f"pinecone-{uuid4().hex[:10]}"
    )


def execution_id() -> str:
    return uuid4().hex[:10]


def live_configured() -> bool:
    return bool(os.getenv("PINECONE_API_KEY") and os.getenv("PINECONE_INDEX_NAME"))


def create_respan(workflow_name: str, run_marker: str) -> Respan:
    load_example_env()
    return Respan(
        api_key=os.environ["RESPAN_API_KEY"],
        base_url=os.getenv("RESPAN_BASE_URL", RESPAN_BASE_URL),
        app_name=workflow_name,
        metadata={
            "example_set": EXAMPLE_SET,
            "workflow_name": workflow_name,
            "example_run_id": run_marker,
            "run_id": run_marker,
        },
        instrumentations=[PineconeInstrumentor()],
        is_batching_enabled=False,
        log_level=os.getenv("RESPAN_LOG_LEVEL", "WARNING"),
    )


def create_pinecone_index() -> Index:
    if live_configured():
        host = os.getenv("PINECONE_INDEX_HOST")
        if host:
            return Index(host=host, api_key=os.environ["PINECONE_API_KEY"])
        from pinecone import Pinecone

        return Pinecone(api_key=os.environ["PINECONE_API_KEY"]).Index(
            os.environ["PINECONE_INDEX_NAME"]
        )
    return Index(host=loopback_host(), api_key="local-pinecone-key", ssl_verify=False)


def create_async_pinecone_index() -> AsyncIndex:
    if live_configured():
        host = os.getenv("PINECONE_INDEX_HOST")
        if not host:
            raise RuntimeError(
                "PINECONE_INDEX_HOST is required for the async live example"
            )
        return AsyncIndex(host=host, api_key=os.environ["PINECONE_API_KEY"])
    return AsyncIndex(
        host=loopback_host(), api_key="local-pinecone-key", ssl_verify=False
    )


def workflow_attributes(
    workflow_name: str, run_marker: str, execution: str
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
            "mode": "live" if live_configured() else "deterministic",
        },
    }


def response_field(response: Any, name: str, default: Any = None) -> Any:
    if isinstance(response, dict):
        return response.get(name, default)
    return getattr(response, name, default)


def to_jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(item) for item in value]
    if type(value).__module__.startswith("pinecone"):
        for method_name in ("to_dict", "model_dump"):
            method = getattr(value, method_name, None)
            if callable(method):
                return to_jsonable(method())
    return {"type": type(value).__name__}


def print_result(label: str, value: Any, run_marker: str) -> None:
    print(f"RESPAN_EXAMPLE_RUN_ID={run_marker}")
    print(f"\n== {label} ==")
    print(json.dumps(to_jsonable(value), allow_nan=False, indent=2, sort_keys=True))


def finish_respan(respan: Respan) -> None:
    try:
        respan.flush()
    finally:
        try:
            respan.shutdown()
        finally:
            shutdown_loopback()
