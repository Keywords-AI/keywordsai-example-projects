from __future__ import annotations

from respan import workflow

from _shared import (
    content_to_text,
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
    response = client.chat.complete(
        model=model_name(),
        messages=[
            {
                "role": "user",
                "content": "Reply with one concise sentence about tracing Mistral AI apps.",
            }
        ],
        temperature=0.1,
        max_tokens=80,
    )
    return content_to_text(response.choices[0].message.content)


def run_chat_completion() -> None:
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    text = ""

    try:
        with make_client() as client:
            with example_attributes(EXAMPLE_NAME, custom_identifier):
                print(f"custom_identifier={custom_identifier}", flush=True)
                print(f"workflow_name={workflow_name(EXAMPLE_NAME)}", flush=True)
                text = _chat_completion_workflow(client)
    finally:
        respan.flush()
        respan.shutdown()

    print_result(EXAMPLE_NAME, custom_identifier, text)


if __name__ == "__main__":
    run_chat_completion()
