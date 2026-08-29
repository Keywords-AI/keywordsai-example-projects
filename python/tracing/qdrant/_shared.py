from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv
from respan import Respan
from respan_instrumentation_qdrant import QdrantInstrumentor

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[2]
load_dotenv(REPO_ROOT / ".env", override=False)


def example_run_id() -> str:
    marker = os.getenv("RESPAN_EXAMPLE_RUN_ID")
    if marker:
        return marker
    marker = "otel2-qdrant-" + datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    os.environ["RESPAN_EXAMPLE_RUN_ID"] = marker
    return marker


def make_respan(example_name: str, *, capture_content: bool = True) -> Respan:
    marker = example_run_id()
    return Respan(
        app_name=f"qdrant-{example_name}",
        api_key=os.environ["RESPAN_API_KEY"],
        base_url=os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api"),
        instrumentations=[QdrantInstrumentor(capture_content=capture_content)],
        metadata={
            "example_run_id": marker,
            "run_id": marker,
            "example_set": "qdrant",
            "example_name": example_name,
        },
    )


def finish_respan(respan: Respan | None) -> None:
    if respan is None:
        return
    try:
        respan.flush()
    finally:
        respan.shutdown()
