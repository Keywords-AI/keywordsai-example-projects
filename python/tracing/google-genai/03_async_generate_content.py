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
    workflow_name,
)

EXAMPLE_NAME = "async-generate-content"


@workflow(name=workflow_name(EXAMPLE_NAME))
async def _async_generate_content_workflow(client) -> str:
    response = await client.aio.models.generate_content(
        model=model_name(),
        contents="Reply with one sentence about async Gemini workloads.",
    )
    return response.text or ""


async def _run_async_generate_content(custom_identifier: str) -> str:
    client = make_client()
    with example_attributes(EXAMPLE_NAME, custom_identifier):
        print(f"custom_identifier={custom_identifier}", flush=True)
        print(f"workflow_name={workflow_name(EXAMPLE_NAME)}", flush=True)
        return await _async_generate_content_workflow(client)


def run_async_generate_content() -> None:
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    text = ""

    try:
        text = asyncio.run(_run_async_generate_content(custom_identifier))
    finally:
        respan.flush()
        respan.shutdown()

    print_result(EXAMPLE_NAME, custom_identifier, text)


if __name__ == "__main__":
    run_async_generate_content()
