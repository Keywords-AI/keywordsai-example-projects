"""Run one Strands agent call with Respan tracing."""

from respan import propagate_attributes, workflow
from strands import Agent

from _shared import create_gateway_model, create_respan, new_run_id

WORKFLOW_NAME = "Strands Basic Example"


def run_basic_agent() -> None:
    run_id = new_run_id("basic")
    respan = create_respan(example_name="basic", run_id=run_id)

    agent = Agent(
        name=WORKFLOW_NAME,
        model=create_gateway_model(),
        system_prompt="Answer in one short sentence.",
    )

    @workflow(name=WORKFLOW_NAME)
    def run_workflow():
        return agent("What is one practical use for distributed tracing?")

    with propagate_attributes(
        trace_group_identifier=WORKFLOW_NAME,
        custom_identifier=run_id,
        customer_identifier="strands-example-user",
        thread_identifier=f"{run_id}-thread",
        metadata={
            "script": "01_basic_agent.py",
            "run_id": run_id,
            "workflow_name": WORKFLOW_NAME,
        },
    ):
        result = run_workflow()

    print(f"RESPAN_EXAMPLE_RUN_ID={run_id}")
    print(result)


if __name__ == "__main__":
    run_basic_agent()
