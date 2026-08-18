"""Trace a real Strands structured-output invocation."""

from _shared import create_gateway_model, create_respan, finish_respan, new_run_id
from pydantic import BaseModel
from respan import propagate_attributes, workflow
from strands import Agent

WORKFLOW_NAME = "Strands Structured Output Example"


class TraceTip(BaseModel):
    title: str
    action: str


def main() -> None:
    run_id = new_run_id("structured")
    respan = create_respan("structured_output", run_id)
    try:
        agent = Agent(name=WORKFLOW_NAME, model=create_gateway_model())

        @workflow(name=WORKFLOW_NAME)
        def run_workflow(prompt: str) -> dict[str, str]:
            result = agent(prompt, structured_output_model=TraceTip)
            parsed = result.structured_output
            return (
                parsed.model_dump()
                if parsed
                else {"error": "missing structured output"}
            )

        with propagate_attributes(
            trace_group_identifier=WORKFLOW_NAME,
            custom_identifier=run_id,
            metadata={
                "run_id": run_id,
                "example_run_id": run_id,
                "script": "04_structured_output.py",
            },
        ):
            result = run_workflow("Return one short distributed tracing debugging tip.")
        print(result)
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    main()
