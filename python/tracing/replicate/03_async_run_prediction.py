from __future__ import annotations

import asyncio

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

EXAMPLE_NAME = "async-run-prediction"


@workflow(name=workflow_name(EXAMPLE_NAME))
async def _async_run_prediction_workflow(client) -> str:
    output = await client.async_run(
        model_name(),
        input={"prompt": "Reply with one concise sentence about async tracing."},
    )
    return text_from_output(output)


async def run_async_prediction() -> None:
    respan = make_respan(EXAMPLE_NAME)
    client = make_client()
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    text = ""

    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print(f"custom_identifier={custom_identifier}", flush=True)
            print(f"workflow_name={workflow_name(EXAMPLE_NAME)}", flush=True)
            text = await _async_run_prediction_workflow(client)
    finally:
        respan.flush()
        respan.shutdown()

    print_result(EXAMPLE_NAME, custom_identifier, text)


if __name__ == "__main__":
    asyncio.run(run_async_prediction())
