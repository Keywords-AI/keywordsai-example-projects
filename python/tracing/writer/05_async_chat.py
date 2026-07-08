from __future__ import annotations

import asyncio

from respan import workflow

from _shared import (
    example_attributes,
    finish_respan,
    make_async_client,
    make_custom_identifier,
    make_respan,
    model_name,
    print_result,
    print_start,
    workflow_name,
)

EXAMPLE_NAME = "async-chat"


@workflow(name=workflow_name(EXAMPLE_NAME))
async def _async_chat_workflow(client) -> str:
    response = await client.chat.chat(
        model=model_name(),
        messages=[{"role": "user", "content": "Give one async tracing tip."}],
        max_tokens=80,
        temperature=0,
    )
    return response.choices[0].message.content


async def run_async() -> str:
    respan = make_respan(EXAMPLE_NAME)
    client = await make_async_client()
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    text = ""
    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print_start(EXAMPLE_NAME, custom_identifier)
            text = await _async_chat_workflow(client)
    finally:
        await client.close()
        finish_respan(respan)
    print_result("async chat", text)
    return text


def run() -> str:
    return asyncio.run(run_async())


if __name__ == "__main__":
    run()
