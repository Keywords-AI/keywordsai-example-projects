from __future__ import annotations

import asyncio

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

EXAMPLE_NAME = "async-run-prediction"


@workflow(name=workflow_name(EXAMPLE_NAME))
async def _async_run_prediction_workflow(prompt: str) -> str:
    client = make_client()
    output = await client.async_run(
        model_name(),
        input={"prompt": prompt},
    )
    return text_from_output(output)


async def run_async_prediction() -> None:
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = ""
    text = ""

    try:
        with example_attributes(EXAMPLE_NAME) as custom_identifier:
            print(f"custom_identifier={custom_identifier}", flush=True)
            print(f"workflow_name={workflow_name(EXAMPLE_NAME)}", flush=True)
            text = await _async_run_prediction_workflow(
                "Reply with one concise sentence about async tracing."
            )
    finally:
        finish_respan(respan)

    print_result(EXAMPLE_NAME, custom_identifier, text)


if __name__ == "__main__":
    asyncio.run(run_async_prediction())
