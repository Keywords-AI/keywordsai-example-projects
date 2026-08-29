"""Shared setup for the Marqo tracing example."""

from __future__ import annotations

import json
import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from uuid import uuid4

from _loopback import loopback_marqo_url
from dotenv import load_dotenv
from respan import Respan
from respan_instrumentation_marqo import MarqoInstrumentor

EXAMPLE_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXAMPLE_DIR.parents[2]
RESPAN_BASE_URL = "https://api.respan.ai/api"
EXAMPLE_SET = "marqo"
_RUN_ID: str | None = None


def load_example_env() -> str:
    global _RUN_ID

    env_path = REPO_ROOT / ".env"
    invocation_run_id = os.getenv("RESPAN_EXAMPLE_RUN_ID", "").strip()
    load_dotenv(env_path, override=True)
    if invocation_run_id:
        os.environ["RESPAN_EXAMPLE_RUN_ID"] = invocation_run_id
    if not os.getenv("RESPAN_API_KEY"):
        raise RuntimeError(f"RESPAN_API_KEY is required in {env_path}")
    if _RUN_ID is None:
        configured_run_id = os.getenv("RESPAN_EXAMPLE_RUN_ID", "").strip()
        _RUN_ID = configured_run_id or f"marqo-{uuid4().hex[:8]}"
    return _RUN_ID


def create_respan(workflow_name: str) -> Respan:
    run_id = load_example_env()
    return Respan(
        api_key=os.environ["RESPAN_API_KEY"],
        base_url=os.getenv("RESPAN_BASE_URL", RESPAN_BASE_URL),
        app_name=workflow_name,
        metadata={
            "example_run_id": run_id,
            "example_set": EXAMPLE_SET,
            "workflow_name": workflow_name,
        },
        instrumentations=[MarqoInstrumentor()],
        is_batching_enabled=False,
        log_level=os.getenv("RESPAN_LOG_LEVEL", "WARNING"),
    )


@contextmanager
def marqo_client(*, force_loopback: bool = False) -> Iterator[Any]:
    import marqo

    configured_url = os.getenv("MARQO_URL", "").strip()
    if configured_url and not force_loopback:
        options = {"url": configured_url}
        if api_key := os.getenv("MARQO_API_KEY"):
            options["api_key"] = api_key
        yield marqo.Client(**options)
        return

    with loopback_marqo_url() as url:
        yield marqo.Client(url=url)


def workflow_attributes(workflow_name: str) -> dict[str, object]:
    run_id = load_example_env()
    return {
        "trace_group_identifier": workflow_name,
        "custom_identifier": f"{workflow_name}-{run_id}",
        "metadata": {
            "example_set": EXAMPLE_SET,
            "workflow_name": workflow_name,
            "example_run_id": run_id,
        },
    }


def unique_index_name() -> str:
    return f"respan-marqo-{uuid4().hex[:8]}"


def print_result(workflow_name: str, result: Any) -> None:
    print(f"\n== {workflow_name} ==")
    print(json.dumps(result, default=str, indent=2, sort_keys=True))


def finish_respan(respan: Respan) -> None:
    try:
        respan.flush()
    finally:
        respan.shutdown()
