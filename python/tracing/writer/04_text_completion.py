from __future__ import annotations

from _shared import (
    close_client,
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
from respan import workflow

EXAMPLE_NAME = "text-completion"
_CLIENT = None


@workflow(name=workflow_name(EXAMPLE_NAME))
def _completion_workflow(prompt: str) -> dict[str, str]:
    response = _CLIENT.completions.create(
        model=model_name(),
        prompt=prompt,
        max_tokens=80,
        temperature=0,
    )
    stream_parts = []
    for chunk in _CLIENT.completions.create(
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
    global _CLIENT
    respan = make_respan(EXAMPLE_NAME)
    client = make_client()
    _CLIENT = client
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    result: dict[str, str] = {}
    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print_start(EXAMPLE_NAME, custom_identifier)
            result = _completion_workflow(
                "Write a short completion about trace context."
            )
    finally:
        try:
            close_client(client)
        finally:
            finish_respan(respan)
    print_result("text completion", result)
    return result


if __name__ == "__main__":
    run()
