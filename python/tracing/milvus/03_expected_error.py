from _shared import (
    collection_name,
    create_respan,
    finish_respan,
    json_native,
    local_milvus_client,
    print_result,
    workflow_attributes,
)
from pymilvus.exceptions import DescribeCollectionException
from respan import Respan, workflow

WORKFLOW_NAME = "milvus_expected_error_workflow"


@workflow(name=WORKFLOW_NAME)
def run_expected_error() -> None:
    with local_milvus_client() as client:
        client.describe_collection(
            collection_name=collection_name("missing_collection")
        )


def main() -> None:
    respan = create_respan(WORKFLOW_NAME)
    try:
        with Respan.propagate_attributes(**workflow_attributes(WORKFLOW_NAME)):
            try:
                run_expected_error()
            except DescribeCollectionException as exc:
                print_result(
                    WORKFLOW_NAME,
                    json_native(
                        {
                            "expected_error": type(exc).__name__,
                            "message": str(exc),
                        }
                    ),
                )
            else:
                raise RuntimeError("Expected the missing collection call to fail")
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    main()
