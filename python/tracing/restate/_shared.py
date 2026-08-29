"""Shared deterministic Restate handler and Respan lifecycle helpers."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator, Iterator
from contextlib import AsyncExitStack, contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from dotenv import load_dotenv
from respan import Respan, propagate_attributes
from respan_instrumentation_restate import RestateInstrumentor
from restate import server_context

EXAMPLE_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXAMPLE_DIR.parents[2]
EXAMPLE_SET = "restate"
DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai/api"


def load_env() -> None:
    load_dotenv(REPO_ROOT / ".env", override=False)
    if not os.getenv("RESPAN_API_KEY"):
        raise RuntimeError("RESPAN_API_KEY must be set in the repository .env")


def run_id() -> str:
    marker = os.getenv("RESPAN_EXAMPLE_RUN_ID")
    if not marker:
        raise RuntimeError("RESPAN_EXAMPLE_RUN_ID must be supplied by run_all.py")
    return marker


def create_respan() -> Respan:
    load_env()
    marker = run_id()
    return Respan(
        api_key=os.environ["RESPAN_API_KEY"],
        base_url=os.getenv("RESPAN_BASE_URL", DEFAULT_RESPAN_BASE_URL),
        app_name="restate-examples",
        metadata={
            "example_set": EXAMPLE_SET,
            "example_run_id": marker,
            "run_id": marker,
        },
        instrumentations=[RestateInstrumentor()],
        is_batching_enabled=False,
        log_level=os.getenv("RESPAN_LOG_LEVEL", "WARNING"),
    )


@contextmanager
def example_context(case: str) -> Iterator[None]:
    marker = run_id()
    with propagate_attributes(
        custom_identifier=f"{EXAMPLE_SET}-{case}-{marker}",
        trace_group_identifier=f"restate_{case}",
        metadata={
            "example_set": EXAMPLE_SET,
            "example_case": case,
            "example_run_id": marker,
            "run_id": marker,
        },
    ):
        yield


async def invoke_registered_handler(
    component: Any,
    handler_name: str,
    payload: Any,
    *,
    invocation_id: str,
    key: str | None = None,
) -> Any:
    """Exercise a real registered handler without requiring a Restate deployment."""
    handler = component.handlers[handler_name]
    encoded = handler.handler_io.input_serde.serialize(payload)
    context = SimpleNamespace(
        handler=handler,
        invocation=SimpleNamespace(
            invocation_id=invocation_id,
            input_buffer=encoded,
            key=key,
            scope=None,
            limit_key=None,
            idempotency_key=None,
        ),
    )
    original_current_context = server_context.current_context
    original_replaying = server_context.restate_context_is_replaying
    server_context.current_context = lambda: context
    server_context.restate_context_is_replaying = SimpleNamespace(get=lambda: False)
    try:
        async with AsyncExitStack() as stack:
            managers: list[AsyncIterator[None]] = list(handler.context_managers or ())
            for manager in managers:
                await stack.enter_async_context(manager())
            return await handler.fn(None, payload)
    finally:
        server_context.current_context = original_current_context
        server_context.restate_context_is_replaying = original_replaying


def finish_respan(respan: Respan) -> None:
    try:
        respan.flush()
    finally:
        respan.shutdown()
