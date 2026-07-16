from __future__ import annotations

import json

from respan import tool, workflow

from _shared import (
    custom_attributes,
    endpoint_name,
    example_attributes,
    json_bytes,
    make_client,
    make_custom_identifier,
    make_respan,
    print_result,
    print_run_header,
    read_json_body,
    streaming_body,
    stubbed_response,
    workflow_name,
)

EXAMPLE_NAME = "invoke-endpoint-chat-tools"


TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get deterministic weather for a city.",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        },
    },
}


@tool(name="get_weather")
def get_weather(city: str) -> str:
    return f"Sunny and 22 C in {city}"


def _extract_tool_call(response_payload: dict) -> dict:
    choices = response_payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise RuntimeError("SageMaker tool example expected a choices response.")
    first_choice = choices[0]
    message = first_choice.get("message") if isinstance(first_choice, dict) else None
    if not isinstance(message, dict):
        raise RuntimeError("SageMaker tool example expected an assistant message.")
    tool_calls = message.get("tool_calls")
    if not isinstance(tool_calls, list) or not tool_calls:
        raise RuntimeError("SageMaker tool example expected an assistant tool call.")
    tool_call = tool_calls[0]
    if not isinstance(tool_call, dict):
        raise RuntimeError("SageMaker tool example received an invalid tool call.")
    return tool_call


def _tool_arguments(tool_call: dict) -> dict:
    function = tool_call.get("function")
    arguments = function.get("arguments") if isinstance(function, dict) else None
    if isinstance(arguments, str):
        return json.loads(arguments)
    if isinstance(arguments, dict):
        return arguments
    return {}


@workflow(name=workflow_name(EXAMPLE_NAME))
def _invoke_chat_tools_workflow(client) -> dict:
    user_message = {
        "role": "user",
        "content": "What is the weather in Tokyo? Use the tool.",
    }
    first_body = {
        "messages": [user_message],
        "tools": [TOOL_SCHEMA],
    }
    first_params = {
        "EndpointName": endpoint_name(),
        "Body": json_bytes(first_body),
        "ContentType": "application/json",
        "Accept": "application/json",
        "CustomAttributes": custom_attributes(),
    }
    first_response = {
        "Body": streaming_body(
            {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "",
                            "tool_calls": [
                                {
                                    "id": "call_weather",
                                    "type": "function",
                                    "function": {
                                        "name": "get_weather",
                                        "arguments": "{\"city\": \"Tokyo\"}",
                                    },
                                }
                            ],
                        }
                    }
                ],
                "usage": {
                    "prompt_tokens": 18,
                    "completion_tokens": 8,
                    "total_tokens": 26,
                },
            }
        ),
        "ContentType": "application/json",
    }

    with stubbed_response(client, "invoke_endpoint", first_response, first_params):
        first_result = read_json_body(client.invoke_endpoint(**first_params))

    tool_call = _extract_tool_call(first_result)
    tool_result = get_weather(**_tool_arguments(tool_call))

    assistant_message = first_result["choices"][0]["message"]
    second_body = {
        "messages": [
            user_message,
            assistant_message,
            {
                "role": "tool",
                "tool_call_id": tool_call.get("id"),
                "content": tool_result,
            },
        ],
        "tools": [TOOL_SCHEMA],
    }
    second_params = {
        "EndpointName": endpoint_name(),
        "Body": json_bytes(second_body),
        "ContentType": "application/json",
        "Accept": "application/json",
        "CustomAttributes": custom_attributes(),
    }
    second_response = {
        "Body": streaming_body(
            {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "Tokyo is sunny and 22 C.",
                        }
                    }
                ],
                "usage": {
                    "prompt_tokens": 32,
                    "completion_tokens": 7,
                    "total_tokens": 39,
                },
            }
        ),
        "ContentType": "application/json",
    }

    with stubbed_response(client, "invoke_endpoint", second_response, second_params):
        final_result = read_json_body(client.invoke_endpoint(**second_params))

    return {
        "tool_call": tool_call,
        "tool_result": tool_result,
        "final_response": final_result,
    }


def run_invoke_endpoint_chat_tools() -> None:
    respan = make_respan(EXAMPLE_NAME)
    client = make_client()
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    result: dict = {}

    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print_run_header(EXAMPLE_NAME, custom_identifier)
            result = _invoke_chat_tools_workflow(client)
    finally:
        respan.flush()
        respan.shutdown()

    print_result(EXAMPLE_NAME, custom_identifier, result)


if __name__ == "__main__":
    run_invoke_endpoint_chat_tools()
