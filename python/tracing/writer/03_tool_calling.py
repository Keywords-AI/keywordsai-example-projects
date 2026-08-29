from __future__ import annotations

import json

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
from respan import tool, workflow

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
_CLIENT = None


@tool(name="get_weather")
def get_weather(city: str) -> dict[str, object]:
    return {"city": city, "condition": "sunny", "temperature_f": 72}


@workflow(name=workflow_name(EXAMPLE_NAME))
def _tool_calling_workflow(city: str) -> dict:
    messages = [{"role": "user", "content": f"Use a tool for {city} weather."}]
    response = _CLIENT.chat.chat(
        model=model_name(),
        messages=messages,
        tools=[WEATHER_TOOL],
        tool_choice="auto",
        max_tokens=120,
        temperature=0,
    )
    message = response.choices[0].message
    call = message.tool_calls[0]
    arguments = json.loads(call.function.arguments)
    tool_result = get_weather(**arguments)
    messages.extend(
        [
            message.model_dump(mode="json"),
            {
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(tool_result, sort_keys=True),
            },
        ]
    )
    follow_up = _CLIENT.chat.chat(
        model=model_name(),
        messages=messages,
        max_tokens=120,
        temperature=0,
    )
    return {
        "tool_call_id": call.id,
        "tool_result": tool_result,
        "answer": follow_up.choices[0].message.content,
    }


def run() -> dict:
    global _CLIENT
    respan = make_respan(EXAMPLE_NAME)
    client = make_client()
    _CLIENT = client
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    result: dict = {}
    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print_start(EXAMPLE_NAME, custom_identifier)
            result = _tool_calling_workflow("Tokyo")
    finally:
        try:
            close_client(client)
        finally:
            finish_respan(respan)
    print_result("tool calling", result)
    print(json.dumps(result, default=str))
    return result


if __name__ == "__main__":
    run()
