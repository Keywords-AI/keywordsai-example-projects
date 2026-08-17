from __future__ import annotations

from _shared import (
    create_pinecone_index,
    create_respan,
    execution_id,
    finish_respan,
    marker,
    print_result,
    workflow_attributes,
)
from pinecone.exceptions import PineconeApiException
from respan import Respan, workflow

WORKFLOW_NAME = "pinecone_expected_error_workflow"


@workflow(name=WORKFLOW_NAME)
def run_expected_error(namespace: str) -> None:
    create_pinecone_index().delete(ids=["missing-vector"], namespace=namespace)


def main() -> None:
    run_marker = marker()
    execution = execution_id()
    respan = create_respan(WORKFLOW_NAME, run_marker)
    try:
        try:
            with Respan.propagate_attributes(
                **workflow_attributes(WORKFLOW_NAME, run_marker, execution)
            ):
                run_expected_error("error")
        except PineconeApiException as exc:
            result = {
                "expected_error": type(exc).__name__,
                "message": "deterministic Pinecone outage",
            }
        else:
            raise AssertionError("the deterministic Pinecone failure did not occur")
        print_result(WORKFLOW_NAME, result, run_marker)
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    main()
