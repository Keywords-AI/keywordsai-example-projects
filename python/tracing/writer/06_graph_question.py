from __future__ import annotations

from _shared import (
    close_client,
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
from respan import workflow

EXAMPLE_NAME = "graph-question"
_CLIENT = None


@workflow(name=workflow_name(EXAMPLE_NAME))
def _graph_question_workflow(question: str) -> str:
    response = _CLIENT.graphs.question(
        graph_ids=graph_ids(),
        question=question,
        subqueries=False,
    )
    return response.answer


def run() -> str:
    global _CLIENT
    respan = make_respan(EXAMPLE_NAME)
    client = make_client()
    _CLIENT = client
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    text = ""
    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print_start(EXAMPLE_NAME, custom_identifier)
            text = _graph_question_workflow(
                "What context is relevant to this tracing example?"
            )
    finally:
        try:
            close_client(client)
        finally:
            finish_respan(respan)
    print_result("graph question", text)
    return text


if __name__ == "__main__":
    run()
