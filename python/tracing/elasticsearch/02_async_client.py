"""Trace asynchronous Elasticsearch index and search operations."""

from __future__ import annotations

import asyncio

from elasticsearch import AsyncElasticsearch
from respan import workflow

from _shared import example_attributes, local_elasticsearch, make_respan

EXAMPLE_NAME = "async-client"


@workflow(name="elasticsearch_async_client")
async def run_async_client(prompt: str, endpoint: str) -> dict[str, object]:
    client = AsyncElasticsearch(endpoint)
    try:
        indexed = await client.index(
            index="audit-index",
            id="doc-1",
            document={"title": prompt, "category": "async-observability"},
            refresh=True,
        )
        searched = await client.search(
            index="audit-index",
            query={"match": {"title": "Async"}},
        )
        return {
            "indexed": indexed["result"],
            "hits": searched["hits"]["total"]["value"],
        }
    finally:
        await client.close()


def main() -> None:
    respan = make_respan(EXAMPLE_NAME)
    try:
        with local_elasticsearch() as endpoint, example_attributes(EXAMPLE_NAME):
            result = asyncio.run(run_async_client("Async Elasticsearch", endpoint))
            print(result)
    finally:
        respan.shutdown()


if __name__ == "__main__":
    main()
