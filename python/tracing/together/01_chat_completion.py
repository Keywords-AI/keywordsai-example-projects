from __future__ import annotations

from respan import workflow

from _shared import (
    example_attributes,
    first_message_text,
    make_client,
    make_custom_identifier,
    make_respan,
    model_name,
    print_result,
    print_start,
    workflow_name,
)

EXAMPLE_NAME = "chat-completion"


@workflow(name=workflow_name(EXAMPLE_NAME))
def _chat_completion_workflow(client) -> str:
    response = client.chat.completions.create(
        model=model_name(),
        messages=[
            {
                "role": "user",
                "content": "Reply with one concise sentence about tracing Together AI apps.",
            }
        ],
        max_tokens=80,
        temperature=0,
    )
    return first_message_text(response)


def run_chat_completion() -> None:
    respan = make_respan(EXAMPLE_NAME)
    client = make_client()
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    text = ""

    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print_start(EXAMPLE_NAME, custom_identifier)
            text = _chat_completion_workflow(client)
    finally:
        respan.flush()
        respan.shutdown()

    print_result(EXAMPLE_NAME, custom_identifier, text)


if __name__ == "__main__":
    run_chat_completion()
