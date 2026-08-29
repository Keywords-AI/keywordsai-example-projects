"""Shared lifecycle and marker helpers for Ragas tracing examples."""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from respan import Respan, propagate_attributes
from respan_instrumentation_ragas import RagasInstrumentor

EXAMPLE_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXAMPLE_DIR.parents[2]
EXAMPLE_SET = "ragas"
DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai/api"


def load_env() -> None:
    load_dotenv(REPO_ROOT / ".env", override=False)
    if not os.getenv("RESPAN_API_KEY"):
        raise RuntimeError("RESPAN_API_KEY must be set in the repository .env")


def run_id() -> str:
    value = os.getenv("RESPAN_EXAMPLE_RUN_ID")
    if not value:
        raise RuntimeError("RESPAN_EXAMPLE_RUN_ID must be supplied by run_all.py")
    return value


def create_respan() -> Respan:
    load_env()
    marker = run_id()
    return Respan(
        api_key=os.environ["RESPAN_API_KEY"],
        base_url=os.getenv("RESPAN_BASE_URL", DEFAULT_RESPAN_BASE_URL),
        app_name="ragas-examples",
        metadata={
            "example_set": EXAMPLE_SET,
            "example_run_id": marker,
            "run_id": marker,
        },
        instrumentations=[RagasInstrumentor()],
        is_batching_enabled=False,
        log_level=os.getenv("RESPAN_LOG_LEVEL", "WARNING"),
    )


@contextmanager
def example_context(case: str) -> Iterator[None]:
    marker = run_id()
    with propagate_attributes(
        custom_identifier=f"{EXAMPLE_SET}-{case}-{marker}",
        trace_group_identifier=f"ragas_{case}",
        metadata={
            "example_set": EXAMPLE_SET,
            "example_case": case,
            "example_run_id": marker,
            "run_id": marker,
        },
    ):
        yield


def finish_respan(respan: Respan) -> None:
    try:
        respan.flush()
    finally:
        respan.shutdown()


def bounded_result(value: Any) -> Any:
    if hasattr(value, "to_pandas"):
        return {"rows": len(value)}
    return value
