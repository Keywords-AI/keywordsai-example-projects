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

EXAMPLE_NAME = "prediction-lifecycle"


@workflow(name=workflow_name(EXAMPLE_NAME))
def _prediction_lifecycle_workflow(client) -> str:
    prediction = client.predictions.create(
        model=model_name(),
        input={"prompt": "Reply with one concise sentence about background jobs."},
        wait=False,
    )
    prediction.wait()
    fetched_prediction = client.predictions.get(prediction.id)
    listed_predictions = client.predictions.list()
    listed_count = len(getattr(listed_predictions, "results", listed_predictions))
    return (
        f"prediction_id={prediction.id}; "
        f"status={prediction.status}; "
        f"fetched={fetched_prediction.status}; "
        f"listed_count={listed_count}; "
        f"output={text_from_output(prediction.output)}"
    )


def run_prediction_lifecycle() -> None:
    respan = make_respan(EXAMPLE_NAME)
    client = make_client()
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    text = ""

    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print(f"custom_identifier={custom_identifier}", flush=True)
            print(f"workflow_name={workflow_name(EXAMPLE_NAME)}", flush=True)
            text = _prediction_lifecycle_workflow(client)
    finally:
        respan.flush()
        respan.shutdown()

    print_result(EXAMPLE_NAME, custom_identifier, text)


if __name__ == "__main__":
    run_prediction_lifecycle()
