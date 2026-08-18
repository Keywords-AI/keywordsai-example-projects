from __future__ import annotations

from _shared import (
    example_attributes,
    finish_respan,
    make_client,
    make_respan,
    model_name,
    print_result,
    text_from_output,
    workflow_name,
)
from respan import workflow

EXAMPLE_NAME = "run-prediction"


@workflow(name=workflow_name(EXAMPLE_NAME))
def _run_prediction_workflow(prompt: str) -> str:
    client = make_client()
    output = client.run(
        model_name(),
        input={"prompt": prompt},
    )
    return text_from_output(output)


def run_prediction() -> None:
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = ""
    text = ""

    try:
        with example_attributes(EXAMPLE_NAME) as custom_identifier:
            print(f"custom_identifier={custom_identifier}", flush=True)
            print(f"workflow_name={workflow_name(EXAMPLE_NAME)}", flush=True)
            text = _run_prediction_workflow(
                "Reply with one concise sentence about Replicate tracing."
            )
    finally:
        finish_respan(respan)

    print_result(EXAMPLE_NAME, custom_identifier, text)


if __name__ == "__main__":
    run_prediction()
