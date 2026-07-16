from __future__ import annotations

from respan import workflow

from _shared import (
    example_attributes,
    make_client,
    make_custom_identifier,
    make_respan,
    model_name,
    print_result,
    workflow_name,
)

EXAMPLE_NAME = "embeddings"


@workflow(name=workflow_name(EXAMPLE_NAME))
def _embeddings_workflow(client) -> str:
    response = client.embed(
        model=model_name(),
        input="Trace local model calls with Respan.",
    )
    embeddings = response["embeddings"]
    vector_count = len(embeddings or [])
    return f"embedding_vectors={vector_count}"


def run_embeddings() -> None:
    respan = make_respan(EXAMPLE_NAME)
    client = make_client()
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    text = ""

    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print(f"custom_identifier={custom_identifier}", flush=True)
            print(f"workflow_name={workflow_name(EXAMPLE_NAME)}", flush=True)
            text = _embeddings_workflow(client)
    finally:
        respan.flush()
        respan.shutdown()

    print_result(EXAMPLE_NAME, custom_identifier, text)


if __name__ == "__main__":
    run_embeddings()
