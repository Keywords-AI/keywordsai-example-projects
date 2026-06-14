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

EXAMPLE_NAME = "streaming-chat"


@workflow(name=workflow_name(EXAMPLE_NAME))
def _streaming_chat_workflow(client) -> str:
    parts: list[str] = []
    with client.chat.stream(
        model=model_name(),
        messages=[{"role": "user", "content": "Stream one short tracing sentence."}],
        max_tokens=80,
        temperature=0,
    ) as stream:
        for event in stream:
            if event.type == "content.delta":
                parts.append(event.delta)
    return "".join(parts)


def run() -> str:
    respan = make_respan(EXAMPLE_NAME)
    client = make_client()
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    text = ""
    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print_start(EXAMPLE_NAME, custom_identifier)
            text = _streaming_chat_workflow(client)
    finally:
        finish_respan(respan)
    print_result("streaming chat", text)
    return text


if __name__ == "__main__":
    run()
