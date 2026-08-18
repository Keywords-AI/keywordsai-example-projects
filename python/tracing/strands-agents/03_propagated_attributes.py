"""Run Strands with per-request Respan attributes."""

from _shared import create_gateway_model, create_respan, finish_respan, new_run_id
from respan import propagate_attributes, workflow
from strands import Agent

WORKFLOW_NAME = "Strands Attribute Propagation Example"


def run_propagated_attributes() -> None:
    run_id = new_run_id("attrs")
    respan = create_respan(example_name="propagated_attributes", run_id=run_id)
    try:
        agent = Agent(
            name=WORKFLOW_NAME,
            model=create_gateway_model(),
            system_prompt="You help support teams triage observability questions.",
        )

        @workflow(name=WORKFLOW_NAME)
        def run_workflow(prompt: str) -> dict[str, str]:
            return {"answer": str(agent(prompt))}

        with propagate_attributes(
            trace_group_identifier=WORKFLOW_NAME,
            custom_identifier=run_id,
            customer_identifier="customer_123",
            thread_identifier=f"{run_id}-support-thread",
            metadata={
                "script": "03_propagated_attributes.py",
                "run_id": run_id,
                "example_run_id": run_id,
                "plan": "pro",
            },
        ):
            result = run_workflow(
                "Give one trace-debugging tip for a failing tool call."
            )
        print(f"RESPAN_EXAMPLE_RUN_ID={run_id}")
        print(result)
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_propagated_attributes()
