from __future__ import annotations

from respan import workflow

from _shared import (
    example_attributes,
    finish_respan,
    graph_ids,
    make_client,
    make_custom_identifier,
    make_respan,
    print_result,
    print_start,
    workflow_name,
)

EXAMPLE_NAME = "graph-question"


@workflow(name=workflow_name(EXAMPLE_NAME))
def _graph_question_workflow(client) -> str:
    response = client.graphs.question(
        graph_ids=graph_ids(),
        question="What context is relevant to this tracing example?",
        subqueries=False,
    )
    return response.answer


def run() -> str:
    respan = make_respan(EXAMPLE_NAME)
    client = make_client()
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    text = ""
    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print_start(EXAMPLE_NAME, custom_identifier)
            text = _graph_question_workflow(client)
    finally:
        finish_respan(respan)
    print_result("graph question", text)
    return text


if __name__ == "__main__":
    run()
