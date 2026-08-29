from __future__ import annotations

import json
from typing import Any

from _shared import (
    deterministic_chat_response,
    example_attributes,
    finish_respan,
    make_custom_identifier,
    make_mock_sync_client,
    make_respan,
    print_result,
    print_start,
    root_request,
    workflow_name,
)
from respan import tool, workflow

EXAMPLE_NAME = "tool-calling"
PROMPT = "What is the weather in Paris? Use the available tool."
TOOL_SCHEMA = {
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


@tool(name="get_weather")
def get_weather(city: str) -> dict[str, Any]:
    """Return deterministic weather for a city."""
    return {"city": city, "condition": "sunny", "temperature_c": 22}


def _response(request):
    payload = json.loads(request.content)
    if not payload.get("tools"):
        raise RuntimeError("tool fixture expected a tool definition")
    return deterministic_chat_response(
        request,
        content="",
        prompt_tokens=27,
        completion_tokens=9,
        tool_calls=[
            {
                "id": "call_weather_paris",
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "arguments": '{"city":"Paris"}',
                },
            }
        ],
    )


def _build_tool_calling_workflow(client):
    @workflow(name=workflow_name(EXAMPLE_NAME))
    def run(request: dict[str, str]) -> dict[str, Any]:
        response = client.chat.complete(
            model=request["model"],
            messages=[{"role": "user", "content": request["prompt"]}],
            tools=[TOOL_SCHEMA],
            tool_choice="auto",
            temperature=0,
        )
        tool_call = response.choices[0].message.tool_calls[0]
        arguments = json.loads(tool_call.function.arguments)
        tool_result = get_weather(**arguments)
        return {
            "tool_call": {
                "id": tool_call.id,
                "name": tool_call.function.name,
                "arguments": arguments,
            },
            "tool_result": tool_result,
        }

    return run


def run_tool_calling() -> None:
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    result: dict[str, Any] = {}

    try:
        with (
            make_mock_sync_client(_response) as client,
            example_attributes(EXAMPLE_NAME, custom_identifier),
        ):
            print_start(EXAMPLE_NAME, custom_identifier, "deterministic-current-sdk")
            result = _build_tool_calling_workflow(client)(
                root_request(EXAMPLE_NAME, PROMPT, available_tools=["get_weather"])
            )
    finally:
        finish_respan(respan)

    print_result(
        EXAMPLE_NAME,
        custom_identifier,
        result,
        "deterministic-current-sdk",
    )


if __name__ == "__main__":
    run_tool_calling()
