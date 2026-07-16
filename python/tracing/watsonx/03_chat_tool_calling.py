from __future__ import annotations

from respan import workflow

from _shared import (
    chat_text,
    example_attributes,
    make_custom_identifier,
    make_model,
    make_respan,
    print_lookup,
    workflow_name,
)

EXAMPLE_NAME = "chat-tool-calling"

WEATHER_TOOL = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Return deterministic weather for a city.",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        },
    },
}


@workflow(name=workflow_name(EXAMPLE_NAME))
def _chat_tool_calling_workflow(model) -> str:
    response = model.chat(
        messages=[
            {"role": "system", "content": "Use the weather tool when needed."},
            {"role": "user", "content": "What is the weather in Tokyo?"},
        ],
        tools=[WEATHER_TOOL],
        tool_choice_option="auto",
        params={"max_new_tokens": 80},
    )
    return chat_text(response)


def run_chat_tool_calling() -> None:
    model = make_model()
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    output = ""

    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            output = _chat_tool_calling_workflow(model)
    finally:
        respan.shutdown()

    print_lookup(EXAMPLE_NAME, custom_identifier, output)


if __name__ == "__main__":
    run_chat_tool_calling()
