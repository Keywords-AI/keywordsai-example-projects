from __future__ import annotations

import json

from _shared import (
    chat_text,
    close_provider,
    example_attributes,
    make_custom_identifier,
    make_model,
    make_respan,
    print_lookup,
    workflow_name,
)
from respan import tool, workflow

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
_MODEL = None


@tool(name="get_weather")
def get_weather(city: str) -> dict[str, object]:
    return {"city": city, "condition": "sunny", "temperature_c": 24}


@workflow(name=workflow_name(EXAMPLE_NAME))
def _chat_tool_calling_workflow(city: str) -> dict[str, object]:
    messages = [
        {"role": "system", "content": "Use the weather tool when needed."},
        {"role": "user", "content": f"What is the weather in {city}?"},
    ]
    response = _MODEL.chat(
        messages=messages,
        tools=[WEATHER_TOOL],
        tool_choice_option="auto",
        params={"max_new_tokens": 80},
    )
    message = response["choices"][0]["message"]
    call = message["tool_calls"][0]
    arguments = call["function"]["arguments"]
    if isinstance(arguments, str):
        arguments = json.loads(arguments)
    result = get_weather(**arguments)
    messages.extend(
        [
            message,
            {
                "role": "tool",
                "tool_call_id": call["id"],
                "content": json.dumps(result, sort_keys=True),
            },
        ]
    )
    follow_up = _MODEL.chat(messages=messages, params={"max_new_tokens": 80})
    return {
        "tool_call_id": call["id"],
        "tool_result": result,
        "answer": chat_text(follow_up),
    }


def run_chat_tool_calling() -> None:
    global _MODEL
    model = make_model()
    _MODEL = model
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    output = ""

    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            output = _chat_tool_calling_workflow("Tokyo")
    finally:
        try:
            close_provider(model)
        finally:
            respan.shutdown()

    print_lookup(EXAMPLE_NAME, custom_identifier, output)


if __name__ == "__main__":
    run_chat_tool_calling()
