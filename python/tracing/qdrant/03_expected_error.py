from __future__ import annotations

from _shared import finish_respan, make_respan
from qdrant_client import QdrantClient
from respan import workflow


@workflow(name="qdrant_expected_error")
def read_missing_collection(collection_name: str) -> None:
    client = QdrantClient(":memory:")
    try:
        client.get_collection(collection_name)
    finally:
        client.close()


def main() -> None:
    respan = None
    try:
        respan = make_respan("expected-error")
        try:
            read_missing_collection("missing_collection")
        except ValueError as exc:
            print({"expected_error": type(exc).__name__})
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    main()
