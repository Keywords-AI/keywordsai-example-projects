"""Run one Strands agent call with Respan tracing."""

from _shared import create_gateway_model, create_respan, finish_respan, new_run_id
from respan import propagate_attributes, workflow
from strands import Agent

WORKFLOW_NAME = "Strands Basic Example"


def run_basic_agent() -> None:
    run_id = new_run_id("basic")
    respan = create_respan(example_name="basic", run_id=run_id)
    try:
        agent = Agent(
            name=WORKFLOW_NAME,
            model=create_gateway_model(),
            system_prompt="Answer in one short sentence.",
        )

        @workflow(name=WORKFLOW_NAME)
        def run_workflow(prompt: str) -> dict[str, str]:
            return {"answer": str(agent(prompt))}

        with propagate_attributes(
            trace_group_identifier=WORKFLOW_NAME,
            custom_identifier=run_id,
            customer_identifier="strands-example-user",
            thread_identifier=f"{run_id}-thread",
            metadata={
                "script": "01_basic_agent.py",
                "run_id": run_id,
                "example_run_id": run_id,
            },
        ):
            result = run_workflow("What is one practical use for distributed tracing?")
        print(f"RESPAN_EXAMPLE_RUN_ID={run_id}")
        print(result)
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_basic_agent()
