import os

from respan import Respan, workflow

from _shared import (
    collection_name,
    create_chroma_client,
    create_respan,
    finish_respan,
    print_result,
    sample_records,
)

WORKFLOW_NAME = "chroma_propagated_attributes_workflow"


@workflow(name=WORKFLOW_NAME)
def run_propagated_attributes() -> dict:
    client = create_chroma_client()
    collection = client.create_collection(
        collection_name(WORKFLOW_NAME),
        metadata={"purpose": "propagated-attributes"},
    )
    records = sample_records()
    collection.add(**records)
    result = collection.query(
        query_embeddings=[[0.9, 0.1, 0.0, 0.0]],
        n_results=1,
        include=["documents", "metadatas", "distances"],
    )
    return {"query": result, "count": collection.count()}


def main() -> None:
    respan = create_respan(WORKFLOW_NAME)
    try:
        with Respan.propagate_attributes(
            trace_group_identifier=WORKFLOW_NAME,
            custom_identifier=f"{WORKFLOW_NAME}-manual-attributes",
            customer_identifier="chroma-example-customer",
            customer_email="chroma@example.com",
            thread_identifier="chroma-example-thread",
            metadata={
                "example_set": "chroma",
                "workflow_name": WORKFLOW_NAME,
                "example_run_id": os.getenv("RESPAN_EXAMPLE_RUN_ID", "manual"),
                "attribute_case": "customer-and-thread",
            },
        ):
            result = run_propagated_attributes()
        print_result(WORKFLOW_NAME, result)
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    main()
