"""Two-turn Responses function call with a canonical tool execution span."""

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

EXAMPLE = "responses-tool-calls"
respan = make_respan(EXAMPLE)
TOOLS = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get the weather for a city.",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
            "additionalProperties": False,
        },
        "strict": True,
    }
]


@tool(name="get_weather")
def get_weather(city: str) -> dict[str, str]:
    return {"city": city, "weather": "sunny", "temperature_c": "22"}


@workflow(name="openai_responses_weather_assistant")
def run(question: str) -> str:
    first = client.responses.create(model=model_name(), input=question, tools=TOOLS)
    call = next(item for item in first.output if item.type == "function_call")
    result = get_weather(**json.loads(call.arguments))
    final = client.responses.create(
        model=model_name(),
        input=[
            {"role": "user", "content": question},
            *first.output,
            {
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": json.dumps(result),
            },
        ],
        tools=TOOLS,
    )
    return final.output_text


try:
    client = make_sync_client()
    try:
        with example_attributes(EXAMPLE):
            print_result(EXAMPLE, run("Weather in Paris?"))
    finally:
        client.close()
finally:
    finish_respan(respan)
