from __future__ import annotations

from typing import Any

from _shared import (
    deterministic_model,
    deterministic_vertex_runtime,
    example_attributes,
    make_respan,
    marker_for,
    workflow_name,
)
from respan import tool, workflow
from vertexai.generative_models import FunctionDeclaration, Tool

EXAMPLE_NAME = "tool-execution"


@tool(name="get_weather")
def get_weather(city: str) -> str:
    return f"Sunny and 22 C in {city}"


@workflow(name=workflow_name(EXAMPLE_NAME))
def tool_execution(city: str) -> str:
    tool_definition = Tool(
        function_declarations=[
            FunctionDeclaration(
                name="get_weather",
                description="Return deterministic weather for a city.",
                parameters={
                    "type": "object",
                    "properties": {"city": {"type": "string"}},
                    "required": ["city"],
                },
            )
        ]
    )
    model = deterministic_model(tools=[tool_definition])
    first = model.generate_content(f"What is the weather in {city}?")
    part: Any = first.candidates[0].content.parts[0]
    call = part.function_call
    result = get_weather(city=call.args["city"])
    return model.generate_content(f"Tool result: {result}").text


def main() -> None:
    marker = marker_for(EXAMPLE_NAME)
    with deterministic_vertex_runtime():
        respan = make_respan(EXAMPLE_NAME, marker)
        try:
            with example_attributes(EXAMPLE_NAME, marker):
                result = tool_execution("Tokyo")
        finally:
            respan.shutdown()
    print({"example": EXAMPLE_NAME, "marker": marker, "result": result}, flush=True)


if __name__ == "__main__":
    main()
