from __future__ import annotations

from typing import Any

from respan import workflow

from _shared import (
    example_attributes,
    make_client,
    make_custom_identifier,
    make_respan,
    model_name,
    print_result,
    response_message_content,
    response_tool_calls,
    tool_call_arguments,
    tool_call_name,
    workflow_name,
)

EXAMPLE_NAME = "tool-calling"


def get_weather(city: str) -> str:
    """Return deterministic weather for a city."""
    return f"sunny and 22 C in {city}"


_TOOLS = [get_weather]


@workflow(name=workflow_name(EXAMPLE_NAME))
def _tool_calling_workflow(client) -> str:
    messages: list[dict[str, Any]] = [
        {
            "role": "user",
            "content": "Use the weather tool for Tokyo and answer briefly.",
        }
    ]
    first_response = client.chat(model=model_name(), messages=messages, tools=_TOOLS)
    tool_calls = response_tool_calls(first_response)
    if not tool_calls:
        return response_message_content(first_response)

    messages.append(
        {
            "role": "assistant",
            "content": response_message_content(first_response),
            "tool_calls": tool_calls,
        }
    )
    for tool_call in tool_calls:
        name = tool_call_name(tool_call)
        arguments = tool_call_arguments(tool_call)
        if name == "get_weather":
            result = get_weather(**arguments)
            messages.append({"role": "tool", "tool_name": name, "content": result})

    final_response = client.chat(model=model_name(), messages=messages)
    return response_message_content(final_response)


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
        respan.flush()
        respan.shutdown()

    print_result(EXAMPLE_NAME, custom_identifier, text)


if __name__ == "__main__":
    run_tool_calling()
