from __future__ import annotations

from respan import workflow

from _shared import (
    example_attributes,
    finish_respan,
    make_client,
    make_custom_identifier,
    make_respan,
    model_name,
    print_result,
    print_start,
    workflow_name,
)

EXAMPLE_NAME = "text-completion"


@workflow(name=workflow_name(EXAMPLE_NAME))
def _completion_workflow(client) -> dict[str, str]:
    response = client.completions.create(
        model=model_name(),
        prompt="Write a short completion about trace context.",
        max_tokens=80,
        temperature=0,
    )
    stream_parts = []
    for chunk in client.completions.create(
        model=model_name(),
        prompt="Stream a short completion about spans.",
        stream=True,
        max_tokens=80,
        temperature=0,
    ):
        stream_parts.append(chunk.value)
    return {
        "completion": response.choices[0].text,
        "streamed_completion": "".join(stream_parts),
    }


def run() -> dict[str, str]:
    respan = make_respan(EXAMPLE_NAME)
    client = make_client()
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    result: dict[str, str] = {}
    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print_start(EXAMPLE_NAME, custom_identifier)
            result = _completion_workflow(client)
    finally:
        finish_respan(respan)
    print_result("text completion", result)
    return result


if __name__ == "__main__":
    run()
