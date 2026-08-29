"""Shared setup for Temporal tracing examples."""

from __future__ import annotations

import os
import re
from pathlib import Path

from dotenv import load_dotenv
from respan import Respan
from respan_instrumentation_temporal import TemporalInstrumentor

EXAMPLE_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXAMPLE_DIR.parents[2]


def marker() -> str:
    invocation = os.getenv("RESPAN_EXAMPLE_RUN_ID")
    load_dotenv(REPO_ROOT / ".env", override=False)
    if invocation:
        os.environ["RESPAN_EXAMPLE_RUN_ID"] = invocation
    return invocation or "temporal-local"


def temporal_id(case: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "-", f"{marker()}-{case}")[:200]


def create_respan(case: str) -> tuple[Respan, TemporalInstrumentor]:
    run_id = marker()
    instrumentor = TemporalInstrumentor(always_create_workflow_spans=True)
    respan = Respan(
        api_key=os.environ["RESPAN_API_KEY"],
        base_url=os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api"),
        app_name=f"temporal-{case}",
        instrumentations=[instrumentor],
        metadata={
            "run_id": run_id,
            "example_run_id": run_id,
            "example_set": "temporal",
            "case": case,
        },
        environment="examples",
    )
    return respan, instrumentor


def finish_respan(respan: Respan) -> None:
    try:
        respan.flush()
    finally:
        respan.shutdown()
