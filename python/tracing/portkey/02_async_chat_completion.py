from __future__ import annotations

import asyncio

from respan import workflow

from _shared import (
    example_attributes,
    make_async_client,
    make_custom_identifier,
    make_respan,
    model_name,
    print_result,
    workflow_name,
)

EXAMPLE_NAME = "async-chat-completion"


@workflow(name=workflow_name(EXAMPLE_NAME))
async def _async_chat_completion_workflow(client) -> str:
    response = await client.chat.completions.create(
        model=model_name(),
        messages=[
            {
                "role": "user",
                "content": "Reply with one concise sentence about tracing LLM apps.",
            }
        ],
    )
    return response.choices[0].message.content or ""


async def run_async_chat_completion() -> None:
    respan = make_respan(EXAMPLE_NAME)
    client = make_async_client()
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    text = ""

    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print(f"custom_identifier={custom_identifier}", flush=True)
            print(f"workflow_name={workflow_name(EXAMPLE_NAME)}", flush=True)
            text = await _async_chat_completion_workflow(client)
    finally:
        await client.close()
        respan.flush()
        respan.shutdown()

    print_result(EXAMPLE_NAME, custom_identifier, text)


if __name__ == "__main__":
    asyncio.run(run_async_chat_completion())
