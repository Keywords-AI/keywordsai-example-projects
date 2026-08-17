"""Run a real Mirascope Model.call and Toolkit.execute with deterministic data."""

from __future__ import annotations

import json

from _shared import (
    close_model_provider,
    create_deterministic_model,
    create_respan,
    finish_respan,
    workflow_attributes,
)
from mirascope import llm
from respan import workflow

WORKFLOW_NAME = "mirascope-call-and-tool"


@llm.tool
def lookup_weather(city: str) -> dict[str, object]:
    """Return deterministic weather for a city."""
    return {"city": city, "temperature_c": 18, "conditions": "sunny"}


def create_runner(model: llm.Model):
    @workflow(name=WORKFLOW_NAME)
    def run_call_and_tool(city: str) -> dict[str, object]:
        response = model.call(
            f"Use lookup_weather for {city}.",
            tools=[lookup_weather],
        )
        outputs = response.execute_tools()
        return {
            "assistant_tool_calls": [
                {"id": call.id, "name": call.name, "args": json.loads(call.args)}
                for call in response.tool_calls
            ],
            "tool_results": [output.result for output in outputs],
        }

    return run_call_and_tool


def main() -> None:
    respan = create_respan(WORKFLOW_NAME)
    model: llm.Model | None = None
    try:
        model = create_deterministic_model()
        runner = create_runner(model)
        with respan.propagate_attributes(
            **workflow_attributes(WORKFLOW_NAME, "01_call_and_tool.py")
        ):
            result = runner("Paris")
        print(json.dumps(result, sort_keys=True))
    finally:
        try:
            if model is not None:
                close_model_provider(model)
        finally:
            finish_respan(respan)


if __name__ == "__main__":
    main()
