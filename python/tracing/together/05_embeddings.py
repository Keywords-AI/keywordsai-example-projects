from __future__ import annotations

from respan import workflow

from _shared import (
    embedding_model_name,
    example_attributes,
    make_client,
    make_custom_identifier,
    make_respan,
    print_result,
    print_start,
    SDK_UNAVAILABLE_ERRORS,
    unavailable_text,
    workflow_name,
)

EXAMPLE_NAME = "embeddings"


@workflow(name=workflow_name(EXAMPLE_NAME))
def _embeddings_workflow(client) -> str:
    try:
        response = client.embeddings.create(
            model=embedding_model_name(),
            input=[
                "Respan traces Together AI chat calls.",
                "Embeddings should not export vector payloads.",
            ],
        )
        data = getattr(response, "data", None) or []
        first_embedding = getattr(data[0], "embedding", []) if data else []
        return f"embedding_count={len(data)} embedding_dimensions={len(first_embedding)}"
    except SDK_UNAVAILABLE_ERRORS as exc:
        return unavailable_text("embeddings", exc)


def run_embeddings() -> None:
    respan = make_respan(EXAMPLE_NAME)
    client = make_client()
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    text = ""

    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print_start(EXAMPLE_NAME, custom_identifier)
            text = _embeddings_workflow(client)
    finally:
        respan.flush()
        respan.shutdown()

    print_result(EXAMPLE_NAME, custom_identifier, text)


if __name__ == "__main__":
    run_embeddings()
