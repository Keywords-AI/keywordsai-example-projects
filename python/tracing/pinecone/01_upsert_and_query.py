from __future__ import annotations

import os
import time
from typing import Any

from respan import Respan, workflow

from _shared import (
    create_pinecone_index,
    create_respan,
    execution_id,
    finish_respan,
    print_result,
    response_field,
    workflow_attributes,
)

WORKFLOW_NAME = "pinecone_upsert_and_query_workflow"


def basis_vector(dimension: int, position: int) -> list[float]:
    vector = [0.0] * dimension
    vector[position % dimension] = 1.0
    return vector


def wait_until_fetchable(index: Any, namespace: str, vector_id: str) -> Any:
    timeout = float(os.getenv("PINECONE_INGEST_TIMEOUT_SECONDS", "30"))
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        fetched = index.fetch(ids=[vector_id], namespace=namespace)
        if vector_id in (response_field(fetched, "vectors", {}) or {}):
            return fetched
        time.sleep(1)
    raise TimeoutError(f"Pinecone did not expose {vector_id!r} within {timeout:g}s")


@workflow(name=WORKFLOW_NAME)
def run_upsert_and_query(run_id: str) -> dict:
    index = create_pinecone_index()
    namespace = f"respan-example-{run_id}"
    stats = index.describe_index_stats()
    dimension = int(response_field(stats, "dimension", 0) or 0)
    if dimension < 1:
        raise RuntimeError("PINECONE_INDEX_NAME must reference a dense-vector index")

    vector_ids = [f"{run_id}-python", f"{run_id}-rust", f"{run_id}-pasta"]
    vectors = [
        {
            "id": vector_ids[0],
            "values": basis_vector(dimension, 0),
            "metadata": {"topic": "programming", "text": "Python is approachable."},
        },
        {
            "id": vector_ids[1],
            "values": basis_vector(dimension, 1),
            "metadata": {"topic": "programming", "text": "Rust emphasizes safety."},
        },
        {
            "id": vector_ids[2],
            "values": basis_vector(dimension, 2),
            "metadata": {"topic": "cooking", "text": "Salt pasta water."},
        },
    ]

    try:
        upserted = index.upsert(vectors=vectors, namespace=namespace)
        fetched = wait_until_fetchable(index, namespace, vector_ids[0])
        queried = index.query(
            namespace=namespace,
            vector=basis_vector(dimension, 0),
            top_k=2,
            include_metadata=True,
        )
        return {
            "index": os.environ["PINECONE_INDEX_NAME"],
            "namespace": namespace,
            "dimension": dimension,
            "upsert": upserted,
            "fetch": fetched,
            "query": queried,
        }
    finally:
        # Only remove IDs created by this run; the existing index is never modified.
        index.delete(ids=vector_ids, namespace=namespace)


def main() -> None:
    run_id = execution_id()
    respan = create_respan(WORKFLOW_NAME)
    try:
        with Respan.propagate_attributes(**workflow_attributes(WORKFLOW_NAME, run_id)):
            result = run_upsert_and_query(run_id)
        print_result(WORKFLOW_NAME, result)
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    main()
