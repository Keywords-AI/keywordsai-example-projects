"""Shared Portkey example setup with exact marker propagation."""

from __future__ import annotations

import json
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from uuid import uuid4

from _local_gateway import local_gateway_base_url, shutdown_local_gateway
from dotenv import load_dotenv
from portkey_ai import AsyncPortkey, Portkey
from respan import Respan, propagate_attributes
from respan_instrumentation_portkey import PortkeyInstrumentor

EXAMPLE_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXAMPLE_DIR.parents[2]
DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai/api"
DEFAULT_MODEL = "gpt-4.1-nano"
EXAMPLE_SET = "portkey"


def load_root_env() -> None:
    load_dotenv(REPO_ROOT / ".env", override=False)
    if not os.getenv("RESPAN_API_KEY"):
        raise RuntimeError(f"RESPAN_API_KEY is required in {REPO_ROOT / '.env'}")


def marker() -> str:
    return os.getenv("RESPAN_EXAMPLE_RUN_ID", "").strip() or (
        f"portkey-{uuid4().hex[:10]}"
    )


def execution_id() -> str:
    return uuid4().hex[:10]


def workflow_name(example_name: str) -> str:
    return f"portkey_{example_name.replace('-', '_')}"


def make_respan(example_name: str, run_marker: str) -> Respan:
    load_root_env()
    return Respan(
        api_key=os.environ["RESPAN_API_KEY"],
        base_url=os.getenv("RESPAN_BASE_URL", DEFAULT_RESPAN_BASE_URL),
        app_name=workflow_name(example_name),
        instrumentations=[PortkeyInstrumentor()],
        is_batching_enabled=False,
        metadata={
            "example_set": EXAMPLE_SET,
            "workflow_name": workflow_name(example_name),
            "example_run_id": run_marker,
            "run_id": run_marker,
        },
        log_level=os.getenv("RESPAN_LOG_LEVEL", "WARNING"),
    )


def live_configured() -> bool:
    return bool(os.getenv("PORTKEY_API_KEY"))


def _client_kwargs(*, live: bool) -> dict[str, object]:
    load_root_env()
    if live:
        if not live_configured():
            raise RuntimeError(
                "PORTKEY_API_KEY is required for the optional live example"
            )
        kwargs: dict[str, object] = {"api_key": os.environ["PORTKEY_API_KEY"]}
        if base_url := os.getenv("PORTKEY_BASE_URL"):
            kwargs["base_url"] = base_url.rstrip("/")
        if provider := os.getenv("PORTKEY_PROVIDER"):
            kwargs["provider"] = provider
        if config := os.getenv("PORTKEY_CONFIG"):
            kwargs["config"] = config
        return kwargs
    return {
        "api_key": "local-portkey-example-key",
        "base_url": local_gateway_base_url(),
    }


def make_client(*, live: bool = False) -> Portkey:
    return Portkey(**_client_kwargs(live=live))


def make_async_client(*, live: bool = False) -> AsyncPortkey:
    return AsyncPortkey(**_client_kwargs(live=live))


def model_name(*, live: bool = False) -> str:
    if live:
        return os.getenv("PORTKEY_MODEL") or os.getenv("RESPAN_MODEL", DEFAULT_MODEL)
    return "local-portkey-model"


@contextmanager
def example_attributes(
    example_name: str, run_marker: str, execution: str, *, mode: str
):
    current_workflow_name = workflow_name(example_name)
    with propagate_attributes(
        custom_identifier=f"{current_workflow_name}-{execution}",
        trace_group_identifier=current_workflow_name,
        metadata={
            "example_set": EXAMPLE_SET,
            "example": example_name,
            "workflow_name": current_workflow_name,
            "example_run_id": run_marker,
            "run_id": run_marker,
            "execution_id": execution,
            "mode": mode,
        },
    ):
        yield


def print_result(example_name: str, run_marker: str, result: Any) -> None:
    print(f"RESPAN_EXAMPLE_RUN_ID={run_marker}")
    print(f"\n== {example_name} ==")
    print(json.dumps(result, allow_nan=False, indent=2, sort_keys=True))


def finish_respan(respan: Respan) -> None:
    try:
        respan.flush()
    finally:
        try:
            respan.shutdown()
        finally:
            shutdown_local_gateway()
