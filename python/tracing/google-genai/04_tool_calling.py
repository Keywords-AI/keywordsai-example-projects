from __future__ import annotations

from google.genai import types

from respan import workflow

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


def get_weather(city: str) -> str:
    """Return deterministic weather for a city."""
    return f"Sunny and 22 C in {city}"


@workflow(name=workflow_name(EXAMPLE_NAME))
def _tool_calling_workflow(client) -> str:
    config = types.GenerateContentConfig(
        tools=[get_weather],
        temperature=0,
        system_instruction="Use the weather tool when a city forecast is requested.",
    )
    response = client.models.generate_content(
        model=model_name(),
        contents="What is the weather in Tokyo? Use the tool and answer briefly.",
        config=config,
    )
    return response.text or ""


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
