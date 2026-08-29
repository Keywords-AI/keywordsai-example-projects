"""OpenRouter tool calling with a traced local tool span."""

from __future__ import annotations

import json

from _shared import close_sync, make_client, make_respan
from respan import tool, workflow

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
                "additionalProperties": False,
            },
        },
    }
]


def main() -> None:
    respan = None
    client = None
    try:
        respan = make_respan(scenario="tool_calling")
        client, model = make_client()

        @tool(name="get_weather")
        def get_weather(city: str) -> str:
            return f"Sunny and 72F in {city}"

        @workflow(name="openrouter_tool_calling")
        def run(question: str) -> str:
            messages = [{"role": "user", "content": question}]
            first_response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=TOOLS,
                tool_choice={
                    "type": "function",
                    "function": {"name": "get_weather"},
                },
            )
            first_message = first_response.choices[0].message
            messages.append(first_message)

            for tool_call in first_message.tool_calls or []:
                args = json.loads(tool_call.function.arguments or "{}")
                result = get_weather(**args)
                print(f"Tool: {tool_call.function.name}({args}) -> {result}")
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    }
                )

            final_response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=TOOLS,
            )
            answer = final_response.choices[0].message.content or ""
            print(answer)
            return answer

        run("What is the weather in Tokyo?")
    finally:
        close_sync(respan=respan, client=client)


if __name__ == "__main__":
    main()
