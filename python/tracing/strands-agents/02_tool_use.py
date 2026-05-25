"""Run a Strands agent tool call with Respan tracing."""

from respan import propagate_attributes, workflow
from strands import Agent, tool

from _shared import create_gateway_model, create_respan, new_run_id

WORKFLOW_NAME = "Strands Tool Use Example"


@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return f"The weather in {city} is sunny and 72F."


def run_tool_use() -> None:
    run_id = new_run_id("tool")
    respan = create_respan(example_name="tool_use", run_id=run_id)

    agent = Agent(
        name=WORKFLOW_NAME,
        model=create_gateway_model(),
        tools=[get_weather],
        system_prompt="Use available tools when weather data is requested.",
    )

    @workflow(name=WORKFLOW_NAME)
    def run_workflow():
        return agent("Use the get_weather tool to answer: weather in Seattle?")

    with propagate_attributes(
        trace_group_identifier=WORKFLOW_NAME,
        custom_identifier=run_id,
        customer_identifier="strands-example-user",
        thread_identifier=f"{run_id}-thread",
        metadata={
            "script": "02_tool_use.py",
            "run_id": run_id,
            "workflow_name": WORKFLOW_NAME,
        },
    ):
        result = run_workflow()

    print(f"RESPAN_EXAMPLE_RUN_ID={run_id}")
    print(result)
    respan.flush()


if __name__ == "__main__":
    run_tool_use()
