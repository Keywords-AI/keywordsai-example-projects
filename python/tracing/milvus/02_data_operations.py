from respan import Respan, workflow

from _shared import (
    collection_name,
    create_respan,
    finish_respan,
    local_milvus_client,
    print_result,
    workflow_attributes,
)

WORKFLOW_NAME = "milvus_data_operations_workflow"


@workflow(name=WORKFLOW_NAME)
def run_data_operations() -> dict:
    with local_milvus_client() as client:
        name = collection_name(WORKFLOW_NAME)
        client.create_collection(collection_name=name, dimension=4)
        inserted = client.insert(
            collection_name=name,
            data=[
                {
                    "id": 1,
                    "vector": [1.0, 0.0, 0.0, 0.0],
                    "text": "Python is a programming language.",
                    "topic": "programming",
                },
                {
                    "id": 2,
                    "vector": [0.8, 0.2, 0.0, 0.0],
                    "text": "Rust emphasizes memory safety.",
                    "topic": "programming",
                },
                {
                    "id": 3,
                    "vector": [0.0, 1.0, 0.0, 0.0],
                    "text": "Pasta cooks in salted water.",
                    "topic": "cooking",
                },
            ],
        )
        client.flush(collection_name=name)

        searched = client.search(
            collection_name=name,
            data=[[1.0, 0.0, 0.0, 0.0]],
            filter="topic == 'programming'",
            limit=2,
            output_fields=["text", "topic"],
        )
        queried = client.query(
            collection_name=name,
            filter="topic == 'programming'",
            output_fields=["id", "text", "topic"],
        )
        fetched = client.get(
            collection_name=name,
            ids=[1, 2],
            output_fields=["text", "topic"],
        )

        upserted = client.upsert(
            collection_name=name,
            data=[
                {
                    "id": 2,
                    "vector": [0.9, 0.1, 0.0, 0.0],
                    "text": "Rust combines safety and performance.",
                    "topic": "programming",
                }
            ],
        )
        deleted = client.delete(collection_name=name, ids=[3])

        return {
            "inserted": inserted,
            "search": searched,
            "query": queried,
            "get": fetched,
            "upserted": upserted,
            "deleted": deleted,
            "stats": client.get_collection_stats(collection_name=name),
        }


def main() -> None:
    respan = create_respan(WORKFLOW_NAME)
    try:
        with Respan.propagate_attributes(**workflow_attributes(WORKFLOW_NAME)):
            result = run_data_operations()
        print_result(WORKFLOW_NAME, result)
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    main()
