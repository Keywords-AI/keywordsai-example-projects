"""Trace synchronous Elasticsearch index, search, and error operations."""

from __future__ import annotations

from elasticsearch import Elasticsearch, NotFoundError
from respan import workflow

from _shared import example_attributes, local_elasticsearch, make_respan

EXAMPLE_NAME = "sync-client"


@workflow(name="elasticsearch_sync_client")
def run_sync_client(prompt: str, endpoint: str) -> dict[str, object]:
    client = Elasticsearch(endpoint)
    try:
        indexed = client.index(
            index="audit-index",
            id="doc-1",
            document={"title": prompt, "category": "observability"},
            refresh=True,
        )
        searched = client.search(
            index="audit-index",
            query={"match": {"title": "Tracing"}},
        )
        missing_status = 0
        try:
            client.get(index="audit-index", id="missing")
        except NotFoundError as exc:
            missing_status = exc.status_code
        return {
            "indexed": indexed["result"],
            "hits": searched["hits"]["total"]["value"],
            "missing_status": missing_status,
        }
    finally:
        client.close()


def main() -> None:
    respan = make_respan(EXAMPLE_NAME)
    try:
        with local_elasticsearch() as endpoint, example_attributes(EXAMPLE_NAME):
            result = run_sync_client("Tracing Elasticsearch", endpoint)
            print(result)
    finally:
        respan.shutdown()


if __name__ == "__main__":
    main()
