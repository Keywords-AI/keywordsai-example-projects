from __future__ import annotations

import asyncio

from respan import workflow

from _shared import (
    example_attributes,
    first_message_text,
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
    response = await client.chat.completions.create(
        model=model_name(),
        messages=[
            {
                "role": "user",
                "content": "Reply with one concise sentence about async tracing.",
            }
        ],
        max_tokens=80,
        temperature=0,
    )
    return first_message_text(response)


async def run_async_chat() -> None:
    respan = make_respan(EXAMPLE_NAME)
    client = make_async_client()
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    text = ""

    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print_start(EXAMPLE_NAME, custom_identifier)
            text = await _async_chat_workflow(client)
    finally:
        await client.close()
        respan.flush()
        respan.shutdown()

    print_result(EXAMPLE_NAME, custom_identifier, text)


if __name__ == "__main__":
    asyncio.run(run_async_chat())
