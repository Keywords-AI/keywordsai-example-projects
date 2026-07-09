from __future__ import annotations

from respan import workflow

from _shared import (
    example_attributes,
    make_client,
    make_custom_identifier,
    make_respan,
    model_name,
    print_result,
    print_start,
    workflow_name,
)

EXAMPLE_NAME = "stream-chat"


@workflow(name=workflow_name(EXAMPLE_NAME))
def _stream_chat_workflow(client) -> str:
    stream = client.chat.completions.create(
        model=model_name(),
        messages=[
            {
                "role": "user",
                "content": "Stream a seven-word sentence about observability.",
            }
        ],
        max_tokens=80,
        temperature=0,
        stream=True,
    )
    parts: list[str] = []
    for chunk in stream:
        choices = getattr(chunk, "choices", None) or []
        if not choices:
            continue
        delta = getattr(choices[0], "delta", None)
        content = getattr(delta, "content", None)
        if content:
            parts.append(content)
    return "".join(parts)


def run_stream_chat() -> None:
    respan = make_respan(EXAMPLE_NAME)
    client = make_client()
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    text = ""

    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print_start(EXAMPLE_NAME, custom_identifier)
            text = _stream_chat_workflow(client)
    finally:
        respan.shutdown()

    print_result(EXAMPLE_NAME, custom_identifier, text)


if __name__ == "__main__":
    run_stream_chat()
