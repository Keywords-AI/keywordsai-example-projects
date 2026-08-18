from __future__ import annotations

from _shared import (
    example_attributes,
    finish_respan,
    make_client,
    make_respan,
    model_name,
    print_result,
    workflow_name,
)
from respan import workflow

EXAMPLE_NAME = "stream-prediction"


@workflow(name=workflow_name(EXAMPLE_NAME))
def _stream_prediction_workflow(prompt: str) -> str:
    client = make_client()
    chunks: list[str] = []
    for event in client.stream(
        model_name(),
        input={"prompt": prompt},
    ):
        chunks.append(str(getattr(event, "data", event)))
    return "".join(chunks)


def run_stream_prediction() -> None:
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = ""
    text = ""

    try:
        with example_attributes(EXAMPLE_NAME) as custom_identifier:
            print(f"custom_identifier={custom_identifier}", flush=True)
            print(f"workflow_name={workflow_name(EXAMPLE_NAME)}", flush=True)
            text = _stream_prediction_workflow(
                "Stream a short sentence about production traces."
            )
    finally:
        finish_respan(respan)

    print_result(EXAMPLE_NAME, custom_identifier, text)


if __name__ == "__main__":
    run_stream_prediction()
