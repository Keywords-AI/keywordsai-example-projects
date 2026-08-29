"""Trace a bounded expected Strands provider connection failure."""

from _shared import create_gateway_model, create_respan, finish_respan, new_run_id
from respan import propagate_attributes, workflow
from strands import Agent

WORKFLOW_NAME = "Strands Expected Provider Error"


def main() -> None:
    run_id = new_run_id("provider-error")
    respan = create_respan("expected_provider_error", run_id)
    try:
        agent = Agent(
            name=WORKFLOW_NAME,
            model=create_gateway_model(base_url="http://127.0.0.1:1/v1"),
        )

        @workflow(name=WORKFLOW_NAME)
        def run_workflow(prompt: str) -> dict[str, str]:
            return {"answer": str(agent(prompt))}

        try:
            with propagate_attributes(
                trace_group_identifier=WORKFLOW_NAME,
                custom_identifier=run_id,
                metadata={
                    "run_id": run_id,
                    "example_run_id": run_id,
                    "script": "05_expected_provider_error.py",
                },
            ):
                run_workflow("This request is expected to fail before generation.")
        except Exception as exc:  # noqa: BLE001 - provider SDK exception surface varies
            print({"expected_error": type(exc).__name__})
        else:
            raise AssertionError("expected provider failure did not occur")
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    main()
