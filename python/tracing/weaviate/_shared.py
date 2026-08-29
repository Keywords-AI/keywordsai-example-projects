from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from respan import Respan, propagate_attributes
from respan_instrumentation_weaviate import WeaviateInstrumentor

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai/api"


def load_root_env() -> None:
    load_dotenv(PROJECT_ROOT / ".env", override=False)


def example_run_id() -> str:
    return os.getenv("RESPAN_EXAMPLE_RUN_ID") or f"weaviate-{uuid4().hex[:12]}"


def _api_key() -> str:
    load_root_env()
    value = os.getenv("RESPAN_API_KEY") or os.getenv("RESPAN_GATEWAY_API_KEY")
    if not value:
        raise RuntimeError("RESPAN_API_KEY or RESPAN_GATEWAY_API_KEY is required")
    return value


def workflow_name(example_name: str) -> str:
    return f"weaviate_{example_name.replace('-', '_')}"


def make_custom_identifier(example_name: str) -> str:
    return f"weaviate-{example_name}-{uuid4().hex[:8]}"


def install_deterministic_backend() -> None:
    from weaviate.collections.collections.sync import _Collections
    from weaviate.collections.data.async_ import _DataCollectionAsync
    from weaviate.collections.data.sync import _DataCollection
    from weaviate.collections.query import _QueryCollection

    if getattr(_Collections, "_respan_deterministic_backend", False):
        return

    def create(self, name, vector_config=None, **kwargs):
        return {"name": name, "created": True, "vector_config": vector_config}

    def delete(self, name, **kwargs):
        if name == "missing-collection":
            raise RuntimeError("local collection missing")

    def insert(self, properties, uuid=None, vector=None, **kwargs):
        return uuid or "deterministic-object-id"

    async def async_insert(self, properties, uuid=None, vector=None, **kwargs):
        return uuid or "deterministic-async-object-id"

    def near_vector(self, near_vector, limit=10, **kwargs):
        return {
            "objects": [
                {
                    "uuid": "deterministic-object-id",
                    "distance": 0.01,
                    "vector": near_vector,
                }
            ][:limit]
        }

    _Collections.create = create
    _Collections.delete = delete
    _Collections._respan_deterministic_backend = True
    _DataCollection.insert = insert
    _DataCollectionAsync.insert = async_insert
    _QueryCollection.near_vector = near_vector


def make_respan(example_name: str, *, deterministic: bool = True) -> Respan:
    if deterministic:
        install_deterministic_backend()
    return Respan(
        api_key=_api_key(),
        base_url=os.getenv("RESPAN_BASE_URL", DEFAULT_RESPAN_BASE_URL).rstrip("/"),
        app_name="weaviate-examples",
        instrumentations=[WeaviateInstrumentor()],
        environment=os.getenv("RESPAN_ENVIRONMENT", "example"),
        metadata={
            "integration": "weaviate",
            "example": example_name,
            "example_set": "weaviate",
            "example_run_id": example_run_id(),
            "run_id": example_run_id(),
        },
        is_batching_enabled=False,
    )


@contextmanager
def example_attributes(
    example_name: str,
    custom_identifier: str,
    *,
    client_mode: str = "deterministic-real-types",
):
    group = workflow_name(example_name)
    with propagate_attributes(
        custom_identifier=custom_identifier,
        trace_group_identifier=group,
        metadata={
            "integration": "weaviate",
            "example": example_name,
            "example_set": "weaviate",
            "example_run_id": example_run_id(),
            "run_id": example_run_id(),
            "workflow_name": group,
            "client_mode": client_mode,
        },
    ):
        yield


def make_collections():
    from weaviate.collections.collections.sync import _Collections

    return object.__new__(_Collections)


def make_data(*, async_: bool = False):
    if async_:
        from weaviate.collections.data.async_ import _DataCollectionAsync as Data
    else:
        from weaviate.collections.data.sync import _DataCollection as Data
    value = object.__new__(Data)
    value._name = "Docs"
    value._tenant = "tenant-a"
    return value


def make_query():
    from weaviate.collections.query import _QueryCollection

    value = object.__new__(_QueryCollection)
    value._name = "Docs"
    value._tenant = "tenant-a"
    return value
