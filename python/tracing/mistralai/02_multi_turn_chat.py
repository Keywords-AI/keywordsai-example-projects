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

EXAMPLE_NAME = "multi-turn-chat"


@workflow(name=workflow_name(EXAMPLE_NAME))
def _multi_turn_chat_workflow(client) -> str:
    response = client.chat.complete(
        model=model_name(),
        messages=[
            {
                "role": "system",
                "content": "You answer with concise observability advice.",
            },
            {
                "role": "user",
                "content": "Name one reason traces help LLM applications.",
            },
            {
                "role": "assistant",
                "content": "They reveal where latency, errors, and token use happen.",
            },
            {
                "role": "user",
                "content": "Now make that advice specific to Mistral AI apps.",
            },
        ],
        temperature=0.1,
        max_tokens=100,
    )
    return content_to_text(response.choices[0].message.content)


def run_multi_turn_chat() -> None:
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    text = ""

    try:
        with make_client() as client:
            with example_attributes(EXAMPLE_NAME, custom_identifier):
                print(f"custom_identifier={custom_identifier}", flush=True)
                print(f"workflow_name={workflow_name(EXAMPLE_NAME)}", flush=True)
                text = _multi_turn_chat_workflow(client)
    finally:
        respan.flush()
        respan.shutdown()

    print_result(EXAMPLE_NAME, custom_identifier, text)


if __name__ == "__main__":
    run_multi_turn_chat()
