from __future__ import annotations

import json

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

EXAMPLE_NAME = "tool-calling"

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
def _tool_calling_workflow(client) -> dict:
    response = client.chat.chat(
        model=model_name(),
        messages=[{"role": "user", "content": "Use a tool for Tokyo weather."}],
        tools=[WEATHER_TOOL],
        tool_choice="auto",
        max_tokens=120,
        temperature=0,
    )
    message = response.choices[0].message
    return {
        "content": message.content,
        "tool_calls": [tool_call.model_dump(mode="json") for tool_call in (message.tool_calls or [])],
    }


def run() -> dict:
    respan = make_respan(EXAMPLE_NAME)
    client = make_client()
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    result: dict = {}
    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print_start(EXAMPLE_NAME, custom_identifier)
            result = _tool_calling_workflow(client)
    finally:
        finish_respan(respan)
    print_result("tool calling", result)
    print(json.dumps(result, default=str))
    return result


if __name__ == "__main__":
    run()
