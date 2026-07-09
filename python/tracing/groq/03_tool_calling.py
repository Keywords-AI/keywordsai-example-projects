from __future__ import annotations

import json

from respan import tool, workflow

from _shared import (
    example_attributes,
    make_client,
    make_custom_identifier,
    make_respan,
    model_name,
    print_result,
    workflow_name,
)

EXAMPLE_NAME = "tool-calling"


def _weather_tool_schema() -> dict:
    return {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Return deterministic weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name for the weather lookup.",
                    }
                },
                "required": ["city"],
            },
        },
    }


@tool(name="get_weather")
def get_weather(city: str) -> str:
    return f"Sunny and 22 C in {city}"


def _tool_calls_content(tool_calls) -> str:
    descriptions: list[str] = []
    for tool_call in tool_calls:
        name = tool_call.function.name
        arguments = tool_call.function.arguments or "{}"
        descriptions.append(f"{name}({arguments})")
    prefix = "Tool call" if len(descriptions) == 1 else "Tool calls"
    return f"{prefix}: {', '.join(descriptions)}"


@workflow(name=workflow_name(EXAMPLE_NAME))
def _tool_calling_workflow(client) -> str:
    messages = [
        {
            "role": "user",
            "content": "What is the weather in Tokyo? Use the tool and answer briefly.",
        }
    ]
    response = client.chat.completions.create(
        model=model_name(),
        messages=messages,
        tools=[_weather_tool_schema()],
        tool_choice={"type": "function", "function": {"name": "get_weather"}},
        temperature=0,
    )
    message = response.choices[0].message
    tool_calls = message.tool_calls or []

    if not tool_calls:
        return get_weather(city="Tokyo")

    assistant_message = message.model_dump(exclude_none=True)
    assistant_message["content"] = assistant_message.get("content") or _tool_calls_content(tool_calls)
    messages.append(assistant_message)
    for tool_call in tool_calls:
        arguments = json.loads(tool_call.function.arguments or "{}")
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": get_weather(city=arguments.get("city", "Tokyo")),
            }
        )

    follow_up = client.chat.completions.create(
        model=model_name(),
        messages=messages,
        temperature=0,
    )
    return follow_up.choices[0].message.content or ""


def run_tool_calling() -> None:
    respan = make_respan(EXAMPLE_NAME)
    client = make_client()
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    text = ""

    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print(f"custom_identifier={custom_identifier}", flush=True)
            print(f"workflow_name={workflow_name(EXAMPLE_NAME)}", flush=True)
            text = _tool_calling_workflow(client)
    finally:
        respan.shutdown()

    print_result(EXAMPLE_NAME, custom_identifier, text)


if __name__ == "__main__":
    run_tool_calling()
