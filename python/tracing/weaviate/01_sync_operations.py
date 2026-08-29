from __future__ import annotations

from _shared import (
    example_attributes,
    make_collections,
    make_custom_identifier,
    make_data,
    make_query,
    make_respan,
    workflow_name,
)
from respan import workflow

EXAMPLE_NAME = "sync-operations"


@workflow(name=workflow_name(EXAMPLE_NAME))
def sync_operations(vector: list[float], limit: int) -> dict[str, object]:
    created = make_collections().create("Docs", vector_config={"vectorizer": "none"})
    object_id = make_data().insert(
        {"text": "Respan traces Weaviate"},
        vector=vector,
    )
    result = make_query().near_vector(vector, limit=limit)
    return {"created": created, "object_id": object_id, "query": result}


def run() -> dict[str, object]:
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    result = {}
    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            result = sync_operations([0.1, 0.2, 0.3], 1)
    finally:
        respan.shutdown()
    print(result)
    return result


if __name__ == "__main__":
    run()
