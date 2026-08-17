from __future__ import annotations

from _shared import (
    content_to_text,
    example_attributes,
    finish_respan,
    make_client,
    make_custom_identifier,
    make_respan,
    print_result,
    print_start,
    root_request,
    workflow_name,
)
from respan import workflow

EXAMPLE_NAME = "multi-turn-chat"
PROMPT = "Now make that advice specific to Mistral AI apps."


def _build_multi_turn_chat_workflow(client):
    @workflow(name=workflow_name(EXAMPLE_NAME))
    def run(request: dict[str, str]) -> str:
        response = client.chat.complete(
            model=request["model"],
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
                {"role": "user", "content": request["prompt"]},
            ],
            temperature=0.1,
            max_tokens=100,
        )
        return content_to_text(response.choices[0].message.content)

    return run


def run_multi_turn_chat() -> None:
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    text = ""

    try:
        with (
            make_client() as client,
            example_attributes(EXAMPLE_NAME, custom_identifier),
        ):
            print_start(EXAMPLE_NAME, custom_identifier)
            text = _build_multi_turn_chat_workflow(client)(
                root_request(
                    EXAMPLE_NAME,
                    PROMPT,
                    prior_turns=3,
                )
            )
    finally:
        finish_respan(respan)

    print_result(EXAMPLE_NAME, custom_identifier, text)


if __name__ == "__main__":
    run_multi_turn_chat()
