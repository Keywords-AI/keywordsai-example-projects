from __future__ import annotations

from respan import workflow

from _shared import (
    example_attributes,
    make_client,
    make_custom_identifier,
    make_respan,
    model_name,
    print_result,
    workflow_name,
)

EXAMPLE_NAME = "stream-prediction"


@workflow(name=workflow_name(EXAMPLE_NAME))
def _stream_prediction_workflow(client) -> str:
    chunks: list[str] = []
    for event in client.stream(
        model_name(),
        input={"prompt": "Stream a short sentence about production traces."},
    ):
        chunks.append(str(getattr(event, "data", event)))
    return "".join(chunks)


def run_stream_prediction() -> None:
    respan = make_respan(EXAMPLE_NAME)
    client = make_client()
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    text = ""

    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print(f"custom_identifier={custom_identifier}", flush=True)
            print(f"workflow_name={workflow_name(EXAMPLE_NAME)}", flush=True)
            text = _stream_prediction_workflow(client)
    finally:
        respan.shutdown()

    print_result(EXAMPLE_NAME, custom_identifier, text)


if __name__ == "__main__":
    run_stream_prediction()
