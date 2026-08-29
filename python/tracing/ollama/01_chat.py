from __future__ import annotations

from _shared import (
    example_attributes,
    flush_and_shutdown,
    make_client,
    make_custom_identifier,
    make_respan,
    model_name,
    print_result,
    response_message_content,
    workflow_name,
)
from respan import workflow

EXAMPLE_NAME = "chat"


@workflow(name=workflow_name(EXAMPLE_NAME))
def _chat_workflow(prompt: str) -> str:
    client = make_client()
    try:
        response = client.chat(
            model=model_name(),
            messages=[{"role": "user", "content": prompt}],
        )
        return response_message_content(response)
    finally:
        client.close()


def run_chat() -> None:
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    text = ""

    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print(f"custom_identifier={custom_identifier}", flush=True)
            print(f"workflow_name={workflow_name(EXAMPLE_NAME)}", flush=True)
            text = _chat_workflow("Reply with one concise tracing sentence.")
    finally:
        flush_and_shutdown(respan)

    print_result(EXAMPLE_NAME, custom_identifier, text)


if __name__ == "__main__":
    run_chat()
