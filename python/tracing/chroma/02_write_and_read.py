from respan import Respan, workflow

from _shared import (
    collection_name,
    create_chroma_client,
    create_respan,
    finish_respan,
    print_result,
    sample_records,
    workflow_attributes,
)

WORKFLOW_NAME = "chroma_write_and_read_workflow"


@workflow(name=WORKFLOW_NAME)
def run_write_and_read() -> dict:
    client = create_chroma_client()
    collection = client.get_or_create_collection(
        collection_name(WORKFLOW_NAME),
        metadata={"purpose": "write-read"},
    )
    records = sample_records()

    collection.add(**records)
    count = collection.count()
    peek = collection.peek(limit=2)
    by_ids = collection.get(ids=["doc-python", "doc-rust"], include=["documents", "metadatas"])
    by_filter = collection.get(
        where={"topic": "programming"},
        limit=2,
        include=["documents", "metadatas"],
    )

    return {
        "count": count,
        "peek": peek,
        "by_ids": by_ids,
        "by_filter": by_filter,
    }


def main() -> None:
    respan = create_respan(WORKFLOW_NAME)
    try:
        with Respan.propagate_attributes(**workflow_attributes(WORKFLOW_NAME)):
            result = run_write_and_read()
        print_result(WORKFLOW_NAME, result)
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    main()
