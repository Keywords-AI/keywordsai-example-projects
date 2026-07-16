from respan import Respan, workflow

from _shared import (
    collection_name,
    create_chroma_client,
    create_respan,
    finish_respan,
    print_result,
    workflow_attributes,
)

WORKFLOW_NAME = "chroma_collection_lifecycle_workflow"


@workflow(name=WORKFLOW_NAME)
def run_collection_lifecycle() -> dict:
    client = create_chroma_client()
    name = collection_name(WORKFLOW_NAME)

    created = client.create_collection(
        name,
        metadata={"purpose": "lifecycle", "example": WORKFLOW_NAME},
    )
    fetched = client.get_collection(name)
    listed = client.list_collections()
    collection_count = client.count_collections()
    heartbeat = client.heartbeat()
    version = client.get_version()
    client.delete_collection(name)

    return {
        "created": created.name,
        "fetched": fetched.name,
        "listed_count": len(listed),
        "collection_count": collection_count,
        "heartbeat": heartbeat,
        "version": version,
    }


def main() -> None:
    respan = create_respan(WORKFLOW_NAME)
    try:
        with Respan.propagate_attributes(**workflow_attributes(WORKFLOW_NAME)):
            result = run_collection_lifecycle()
        print_result(WORKFLOW_NAME, result)
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    main()
