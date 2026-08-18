from __future__ import annotations

import asyncio

from _shared import (
    close_async_client,
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
from respan import workflow

EXAMPLE_NAME = "async-chat"
_CLIENT = None


@workflow(name=workflow_name(EXAMPLE_NAME))
async def _async_chat_workflow(prompt: str) -> str:
    response = await _CLIENT.chat.chat(
        model=model_name(),
        messages=[{"role": "user", "content": prompt}],
        max_tokens=80,
        temperature=0,
    )
    return response.choices[0].message.content


async def run_async() -> str:
    global _CLIENT
    respan = make_respan(EXAMPLE_NAME)
    client = await make_async_client()
    _CLIENT = client
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    text = ""
    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print_start(EXAMPLE_NAME, custom_identifier)
            text = await _async_chat_workflow("Give one async tracing tip.")
    finally:
        try:
            await close_async_client(client)
        finally:
            finish_respan(respan)
    print_result("async chat", text)
    return text


def run() -> str:
    return asyncio.run(run_async())


if __name__ == "__main__":
    run()
