"""Two-turn Chat function call with a canonical tool execution span."""

import json

from respan import tool, workflow

from _shared import (
    example_attributes,
    finish_respan,
    make_respan,
    make_sync_client,
    model_name,
    print_result,
)

EXAMPLE = "tool-calls"
respan = make_respan(EXAMPLE)
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        },
    }
]


@tool(name="get_weather")
def get_weather(city: str) -> dict[str, str]:
    return {"city": city, "weather": "sunny", "temperature_c": "22"}


@workflow(name="openai_chat_weather_assistant")
def run(question: str) -> str:
    messages: list = [{"role": "user", "content": question}]
    first = client.chat.completions.create(
        model=model_name(), messages=messages, tools=TOOLS
    )
    message = first.choices[0].message
    messages.append(message)
    for call in message.tool_calls or []:
        result = get_weather(**json.loads(call.function.arguments))
        messages.append(
            {
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result),
            }
        )
    final = client.chat.completions.create(
        model=model_name(), messages=messages, tools=TOOLS
    )
    return final.choices[0].message.content or ""


try:
    client = make_sync_client()
    try:
        with example_attributes(EXAMPLE):
            print_result(EXAMPLE, run("Weather in Paris?"))
    finally:
        client.close()
finally:
    finish_respan(respan)
