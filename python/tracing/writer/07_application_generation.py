from __future__ import annotations

from respan import workflow

from _shared import (
    application_id,
    example_attributes,
    finish_respan,
    make_client,
    make_custom_identifier,
    make_respan,
    print_result,
    print_start,
    workflow_name,
)

EXAMPLE_NAME = "application-generation"


@workflow(name=workflow_name(EXAMPLE_NAME))
def _application_generation_workflow(client) -> dict[str, str]:
    response = client.applications.generate_content(
        application_id(),
        inputs=[{"id": "topic", "value": ["observability"]}],
    )
    stream_parts = []
    for chunk in client.applications.generate_content(
        application_id(),
        inputs=[{"id": "topic", "value": ["streaming observability"]}],
        stream=True,
    ):
        if chunk.delta.content:
            stream_parts.append(chunk.delta.content)
    return {
        "suggestion": response.suggestion,
        "streamed_suggestion": "".join(stream_parts),
    }


def run() -> dict[str, str]:
    respan = make_respan(EXAMPLE_NAME)
    client = make_client()
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    result: dict[str, str] = {}
    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print_start(EXAMPLE_NAME, custom_identifier)
            result = _application_generation_workflow(client)
    finally:
        finish_respan(respan)
    print_result("application generation", result)
    return result


if __name__ == "__main__":
    run()
