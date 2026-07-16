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

WORKFLOW_NAME = "chroma_update_upsert_delete_workflow"


@workflow(name=WORKFLOW_NAME)
def run_update_upsert_delete() -> dict:
    client = create_chroma_client()
    collection = client.create_collection(
        collection_name(WORKFLOW_NAME),
        metadata={"purpose": "mutations"},
    )
    records = sample_records()

    collection.add(**records)
    collection.update(
        ids=["doc-python"],
        documents=["Python is a widely used programming language."],
        metadatas=[{"topic": "programming", "source": "python", "rank": 10}],
        embeddings=[[0.85, 0.15, 0.0, 0.0]],
    )
    collection.upsert(
        ids=["doc-rust", "doc-observability"],
        documents=[
            "Rust emphasizes memory safety without garbage collection.",
            "Respan traces vector database work alongside LLM workflows.",
        ],
        metadatas=[
            {"topic": "programming", "source": "rust", "rank": 20},
            {"topic": "observability", "source": "respan", "rank": 4},
        ],
        embeddings=[
            [0.75, 0.25, 0.0, 0.0],
            [0.3, 0.2, 0.5, 0.0],
        ],
    )
    collection.modify(metadata={"purpose": "mutations", "updated": True})
    after_upsert = collection.get(include=["documents", "metadatas"])
    collection.delete(where={"topic": "cooking"})
    after_delete_count = collection.count()

    return {
        "after_upsert": after_upsert,
        "after_delete_count": after_delete_count,
    }


def main() -> None:
    respan = create_respan(WORKFLOW_NAME)
    try:
        with Respan.propagate_attributes(**workflow_attributes(WORKFLOW_NAME)):
            result = run_update_upsert_delete()
        print_result(WORKFLOW_NAME, result)
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    main()
