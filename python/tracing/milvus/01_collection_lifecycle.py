from respan import Respan, workflow

from _shared import (
    collection_name,
    create_respan,
    finish_respan,
    local_milvus_client,
    print_result,
    workflow_attributes,
)

WORKFLOW_NAME = "milvus_collection_lifecycle_workflow"


@workflow(name=WORKFLOW_NAME)
def run_collection_lifecycle() -> dict:
    with local_milvus_client() as client:
        name = collection_name(WORKFLOW_NAME)
        client.create_collection(collection_name=name, dimension=4)
        before_drop = {
            "exists": client.has_collection(collection_name=name),
            "collections": client.list_collections(),
            "description": client.describe_collection(collection_name=name),
        }
        client.drop_collection(collection_name=name)
        return {
            "before_drop": before_drop,
            "exists_after_drop": client.has_collection(collection_name=name),
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
