"""Shared helpers for Milvus tracing examples."""

from __future__ import annotations

import json
import os
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Iterator
from uuid import uuid4

from dotenv import load_dotenv
from pymilvus import MilvusClient
from respan import Respan
from respan_instrumentation_milvus import MilvusInstrumentor

EXAMPLE_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXAMPLE_DIR.parents[2]
RESPAN_BASE_URL = "https://api.respan.ai/api"
EXAMPLE_SET = "milvus"


def load_example_env() -> None:
    env_path = REPO_ROOT / ".env"
    load_dotenv(env_path, override=True)
    if not os.getenv("RESPAN_API_KEY"):
        raise RuntimeError(f"RESPAN_API_KEY is required in {env_path}")
    os.environ.setdefault("RESPAN_BASE_URL", RESPAN_BASE_URL)


def create_respan(workflow_name: str) -> Respan:
    load_example_env()
    return Respan(
        api_key=os.environ["RESPAN_API_KEY"],
        base_url=os.getenv("RESPAN_BASE_URL", RESPAN_BASE_URL),
        app_name=workflow_name,
        metadata={"example_set": EXAMPLE_SET, "workflow_name": workflow_name},
        instrumentations=[MilvusInstrumentor()],
        is_batching_enabled=False,
        log_level=os.getenv("RESPAN_LOG_LEVEL", "WARNING"),
    )


@contextmanager
def local_milvus_client() -> Iterator[MilvusClient]:
    """Create an isolated Milvus Lite database and remove it after the run."""
    with TemporaryDirectory(prefix="respan-milvus-") as directory:
        client = MilvusClient(uri=str(Path(directory) / "milvus.db"))
        try:
            yield client
        finally:
            client.close()


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


def collection_name(workflow_name: str) -> str:
    return f"respan_{workflow_name}_{uuid4().hex[:8]}".replace("-", "_")


def print_result(label: str, value: Any) -> None:
    print(f"\n== {label} ==")
    print(json.dumps(value, default=str, indent=2, sort_keys=True))


def finish_respan(respan: Respan) -> None:
    try:
        respan.flush()
    finally:
        respan.shutdown()
