from __future__ import annotations

from respan import workflow

from _shared import (
    example_attributes,
    make_client,
    make_custom_identifier,
    make_respan,
    model_name,
    print_result,
    text_from_output,
    workflow_name,
)

EXAMPLE_NAME = "run-prediction"


@workflow(name=workflow_name(EXAMPLE_NAME))
def _run_prediction_workflow(client) -> str:
    output = client.run(
        model_name(),
        input={"prompt": "Reply with one concise sentence about Replicate tracing."},
    )
    return text_from_output(output)


def run_prediction() -> None:
    respan = make_respan(EXAMPLE_NAME)
    client = make_client()
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    text = ""

    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print(f"custom_identifier={custom_identifier}", flush=True)
            print(f"workflow_name={workflow_name(EXAMPLE_NAME)}", flush=True)
            text = _run_prediction_workflow(client)
    finally:
        respan.shutdown()

    print_result(EXAMPLE_NAME, custom_identifier, text)


if __name__ == "__main__":
    run_prediction()
