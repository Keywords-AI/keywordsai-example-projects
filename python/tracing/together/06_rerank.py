from __future__ import annotations

from respan import workflow

from _shared import (
    example_attributes,
    make_client,
    make_custom_identifier,
    make_respan,
    print_result,
    print_start,
    rerank_model_name,
    SDK_UNAVAILABLE_ERRORS,
    unavailable_text,
    workflow_name,
)

EXAMPLE_NAME = "rerank"


@workflow(name=workflow_name(EXAMPLE_NAME))
def _rerank_workflow(client) -> str:
    try:
        response = client.rerank.create(
            model=rerank_model_name(),
            query="Which document is about observability?",
            documents=[
                "Distributed tracing shows how requests move through services.",
                "Sourdough bread needs flour, water, salt, and patience.",
                "A beach umbrella blocks sunlight.",
            ],
            top_n=1,
            return_documents=True,
        )
        results = getattr(response, "results", None) or []
        if not results:
            return "no rerank results"
        top = results[0]
        return f"top_index={top.index} relevance_score={top.relevance_score}"
    except SDK_UNAVAILABLE_ERRORS as exc:
        return unavailable_text("rerank", exc)


def run_rerank() -> None:
    respan = make_respan(EXAMPLE_NAME)
    client = make_client()
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    text = ""

    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print_start(EXAMPLE_NAME, custom_identifier)
            text = _rerank_workflow(client)
    finally:
        respan.shutdown()

    print_result(EXAMPLE_NAME, custom_identifier, text)


if __name__ == "__main__":
    run_rerank()
