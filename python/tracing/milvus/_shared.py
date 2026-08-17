"""Shared helpers for Milvus tracing examples."""

from __future__ import annotations

import json
import os
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager, suppress
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from uuid import uuid4

from dotenv import load_dotenv
from pymilvus import DataType, MilvusClient
from respan import Respan
from respan_instrumentation_milvus import MilvusInstrumentor

EXAMPLE_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXAMPLE_DIR.parents[2]
RESPAN_BASE_URL = "https://api.respan.ai/api"
EXAMPLE_SET = "milvus"
_MAX_RESULT_ITEMS = 12
_MAX_RESULT_DEPTH = 6


def load_example_env() -> None:
    invocation_run_id = os.getenv("RESPAN_EXAMPLE_RUN_ID", "").strip()
    env_path = REPO_ROOT / ".env"
    load_dotenv(env_path, override=True)
    if invocation_run_id:
        os.environ["RESPAN_EXAMPLE_RUN_ID"] = invocation_run_id
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


def create_local_collection(
    client: MilvusClient,
    name: str,
    *,
    dimension: int = 4,
) -> None:
    """Create a Lite collection without the unsupported auto-index wait RPC."""

    schema = client.create_schema(auto_id=False, enable_dynamic_field=True)
    schema.add_field("id", DataType.INT64, is_primary=True)
    schema.add_field("vector", DataType.FLOAT_VECTOR, dim=dimension)
    client.create_collection(collection_name=name, schema=schema)


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


def json_native(value: Any, *, depth: int = 0) -> Any:
    """Return a bounded JSON-native value suitable for workflow output."""

    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, bytes):
        return {"type": "bytes", "length": len(value)}
    if depth > _MAX_RESULT_DEPTH:
        return {
            "type": f"{type(value).__module__}.{type(value).__qualname__}",
            "truncated": True,
        }
    if isinstance(value, Mapping):
        items = list(value.items())
        result = {
            str(key): json_native(item, depth=depth + 1)
            for key, item in items[:_MAX_RESULT_ITEMS]
        }
        if len(items) > _MAX_RESULT_ITEMS:
            result["__truncated__"] = len(items) - _MAX_RESULT_ITEMS
        return result
    if isinstance(value, Sequence) and not isinstance(
        value,
        (str, bytes, bytearray),
    ):
        items = [
            json_native(item, depth=depth + 1) for item in value[:_MAX_RESULT_ITEMS]
        ]
        if len(value) > _MAX_RESULT_ITEMS:
            return {"count": len(value), "items": items, "truncated": True}
        return items
    for method_name in ("to_dict", "to_pylist", "tolist", "item"):
        method = getattr(value, method_name, None)
        if callable(method):
            with suppress(AttributeError, TypeError, ValueError):
                return json_native(method(), depth=depth + 1)
    return {"type": f"{type(value).__module__}.{type(value).__qualname__}"}


def finish_respan(respan: Respan) -> None:
    try:
        respan.flush()
    finally:
        respan.shutdown()
