from __future__ import annotations

import os
from uuid import uuid4

import weaviate
from _shared import (
    example_attributes,
    load_root_env,
    make_custom_identifier,
    make_respan,
    workflow_name,
)
from respan import workflow
from weaviate.classes.config import Configure
from weaviate.classes.init import Auth

EXAMPLE_NAME = "live-service"
_CLIENT = None


@workflow(name=workflow_name(EXAMPLE_NAME))
def _live_roundtrip(collection_name: str, query_vector: list[float]) -> dict:
    collection = _CLIENT.collections.create(
        collection_name,
        vector_config=Configure.Vectors.self_provided(),
    )
    try:
        object_id = collection.data.insert(
            {"text": "Respan live Weaviate verification"},
            vector=query_vector,
        )
        result = collection.query.near_vector(
            near_vector=query_vector,
            limit=1,
        )
        return {
            "collection": collection_name,
            "inserted": str(object_id),
            "result_count": len(result.objects),
        }
    finally:
        _CLIENT.collections.delete(collection_name)


def run() -> dict | None:
    global _CLIENT
    load_root_env()
    cluster_url = os.getenv("WEAVIATE_URL")
    api_key = os.getenv("WEAVIATE_API_KEY")
    if not cluster_url or not api_key:
        print("skipped=WEAVIATE_URL/WEAVIATE_API_KEY not configured")
        return None

    respan = make_respan(EXAMPLE_NAME, deterministic=False)
    client = None
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    try:
        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=cluster_url,
            auth_credentials=Auth.api_key(api_key),
        )
        _CLIENT = client
        with example_attributes(
            EXAMPLE_NAME,
            custom_identifier,
            client_mode="live-weaviate-service",
        ):
            result = _live_roundtrip(
                f"RespanOtel{uuid4().hex[:12]}",
                [0.1, 0.2, 0.3],
            )
        print(result)
        return result
    finally:
        try:
            if client is not None:
                client.close()
        finally:
            respan.shutdown()


if __name__ == "__main__":
    run()
