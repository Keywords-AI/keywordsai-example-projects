from __future__ import annotations

import asyncio

from _shared import (
    content_to_text,
    example_attributes,
    finish_respan,
    make_client,
    make_custom_identifier,
    make_respan,
    print_result,
    print_start,
    root_request,
    workflow_name,
)
from respan import workflow

EXAMPLE_NAME = "async-chat-completion"
PROMPT = "Reply with one concise sentence about async tracing."


def _build_async_chat_completion_workflow(client):
    @workflow(name=workflow_name(EXAMPLE_NAME))
    async def run(request: dict[str, str]) -> str:
        response = await client.chat.complete_async(
            model=request["model"],
            messages=[{"role": "user", "content": request["prompt"]}],
            temperature=0.1,
            max_tokens=80,
        )
        return content_to_text(response.choices[0].message.content)

    return run


async def run_async_chat_completion() -> None:
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    text = ""

    try:
        async with make_client() as client:
            with example_attributes(EXAMPLE_NAME, custom_identifier):
                print_start(EXAMPLE_NAME, custom_identifier)
                text = await _build_async_chat_completion_workflow(client)(
                    root_request(EXAMPLE_NAME, PROMPT)
                )
    finally:
        finish_respan(respan)

    print_result(EXAMPLE_NAME, custom_identifier, text)


if __name__ == "__main__":
    asyncio.run(run_async_chat_completion())
