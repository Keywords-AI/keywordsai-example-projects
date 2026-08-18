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

EXAMPLE_NAME = "chat-completion"
_CLIENT = None


@workflow(name=workflow_name(EXAMPLE_NAME))
def _chat_workflow(prompt: str) -> str:
    response = _CLIENT.chat.chat(
        model=model_name(),
        messages=[
            {"role": "system", "content": "Answer in one concise sentence."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=80,
        temperature=0,
    )
    return response.choices[0].message.content


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
            text = _chat_workflow("What does instrumentation capture?")
    finally:
        try:
            close_client(client)
        finally:
            finish_respan(respan)
    print_result("chat completion", text)
    return text


if __name__ == "__main__":
    run()
