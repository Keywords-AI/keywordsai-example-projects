"""Trace a forced Anthropic tool call, tool result, and final response."""

from respan import workflow

from _shared import (
    example_attributes,
    make_client,
    make_respan,
    message_text,
    model_name,
    print_result,
    workflow_name,
)

CASE_ID = "tool_round"
TOOL_NAME = "lookup_weather"


def lookup_weather(city: str) -> str:
    return f"The weather in {city} is sunny and 22C."


@workflow(name=workflow_name(CASE_ID))
def run_tool_round() -> str:
    client = make_client()
    user_message = {"role": "user", "content": "What is the weather in Tokyo?"}
    tool_definition = {
        "name": TOOL_NAME,
        "description": "Look up current weather for a city.",
        "input_schema": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        },
    }
    first = client.messages.create(
        model=model_name(),
        max_tokens=96,
        messages=[user_message],
        tools=[tool_definition],
        tool_choice={"type": "tool", "name": TOOL_NAME},
    )
    tool_use = next(block for block in first.content if block.type == "tool_use")
    result = lookup_weather(str(tool_use.input["city"]))
    final = client.messages.create(
        model=model_name(),
        max_tokens=96,
        messages=[
            user_message,
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_use",
                        "id": tool_use.id,
                        "name": tool_use.name,
                        "input": tool_use.input,
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": result,
                    }
                ],
            },
        ],
        tools=[tool_definition],
    )
    return message_text(final)


def main() -> None:
    respan = make_respan()
    try:
        with example_attributes(respan, CASE_ID):
            output = run_tool_round()
    finally:
        respan.shutdown()
    print_result(CASE_ID, output)


if __name__ == "__main__":
    main()
