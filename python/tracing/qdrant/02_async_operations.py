from __future__ import annotations

import asyncio

from _shared import finish_respan, make_respan
from qdrant_client import AsyncQdrantClient, models
from respan import workflow


@workflow(name="qdrant_async_operations")
async def run_async_operations(
    query_vector: list[float], limit: int
) -> dict[str, object]:
    client = AsyncQdrantClient(":memory:")
    try:
        await client.create_collection(
            "async_documents",
            vectors_config=models.VectorParams(size=3, distance=models.Distance.DOT),
        )
        await client.upsert(
            "async_documents",
            points=[
                models.PointStruct(
                    id=3,
                    vector=[0.4, 0.5, 0.6],
                    payload={"mode": "async"},
                )
            ],
        )
        query = await client.query_points(
            "async_documents", query=query_vector, limit=limit
        )
        scrolled, _ = await client.scroll("async_documents", limit=limit)
        return {
            "query_ids": [point.id for point in query.points],
            "scroll_ids": [point.id for point in scrolled],
        }
    finally:
        await client.close()


async def run() -> None:
    respan = None
    try:
        respan = make_respan("async-operations")
        print(await run_async_operations([0.4, 0.5, 0.6], 1))
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    asyncio.run(run())
