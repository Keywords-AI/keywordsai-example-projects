from __future__ import annotations

from _shared import finish_respan, make_respan
from qdrant_client import QdrantClient, models
from respan import workflow


@workflow(name="qdrant_sync_operations")
def run_sync_operations(query_vector: list[float], limit: int) -> dict[str, object]:
    client = QdrantClient(":memory:")
    try:
        client.create_collection(
            "documents",
            vectors_config=models.VectorParams(
                size=3,
                distance=models.Distance.COSINE,
            ),
        )
        client.upsert(
            "documents",
            points=[
                models.PointStruct(
                    id=1,
                    vector=[1.0, 0.0, 0.0],
                    payload={"topic": "otel"},
                ),
                models.PointStruct(
                    id=2,
                    vector=[0.0, 1.0, 0.0],
                    payload={"topic": "tracing"},
                ),
            ],
        )
        query = client.query_points("documents", query=query_vector, limit=limit)
        retrieved = client.retrieve("documents", ids=[1, 2])
        scrolled, _ = client.scroll("documents", limit=limit)
        return {
            "query_ids": [point.id for point in query.points],
            "retrieved_ids": [point.id for point in retrieved],
            "scroll_ids": [point.id for point in scrolled],
        }
    finally:
        client.close()


def main() -> None:
    respan = None
    try:
        respan = make_respan("sync-operations")
        print(run_sync_operations([1.0, 0.0, 0.0], 2))
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    main()
