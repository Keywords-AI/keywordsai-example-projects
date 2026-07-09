from __future__ import annotations

from respan import workflow

from _shared import (
    example_attributes,
    make_client,
    make_custom_identifier,
    make_respan,
    model_name,
    print_result,
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
                "content": "Reply with one concise sentence about AI gateways.",
            }
        ],
    )
    return response.choices[0].message.content or ""


def run_chat_completion() -> None:
    respan = make_respan(EXAMPLE_NAME)
    client = make_client()
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    text = ""

    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print(f"custom_identifier={custom_identifier}", flush=True)
            print(f"workflow_name={workflow_name(EXAMPLE_NAME)}", flush=True)
            text = _chat_completion_workflow(client)
    finally:
        respan.shutdown()

    print_result(EXAMPLE_NAME, custom_identifier, text)


if __name__ == "__main__":
    run_chat_completion()
