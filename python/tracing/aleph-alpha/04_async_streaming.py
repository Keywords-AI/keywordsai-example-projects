from __future__ import annotations

import asyncio

from aleph_alpha_client import ChatRequest, CompletionRequest, Message, Prompt
from aleph_alpha_client.chat import Role, StreamOptions
from _shared import (
    async_client_context,
    example_attributes,
    make_custom_identifier,
    make_respan,
    model_name,
    print_result,
    workflow,
    workflow_name,
)

EXAMPLE_NAME = "async-streaming"


@workflow(name=workflow_name(EXAMPLE_NAME))
async def _async_streaming_workflow(client) -> str:
    completion_request = CompletionRequest(
        prompt=Prompt.from_text("Stream a short completion about tracing."),
        maximum_tokens=24,
    )
    completion_parts: list[str] = []
    async for item in client.complete_with_streaming(
        request=completion_request,
        model=model_name(),
    ):
        completion = getattr(item, "completion", None)
        if completion:
            completion_parts.append(completion)

    chat_request = ChatRequest(
        model=model_name(),
        messages=[Message(role=Role.User, content="Stream one short chat sentence.")],
        stream_options=StreamOptions(include_usage=True),
    )
    chat_parts: list[str] = []
    async for item in client.chat_with_streaming(request=chat_request, model=model_name()):
        content = getattr(item, "content", None)
        if content:
            chat_parts.append(content)

    return f"completion={''.join(completion_parts)} chat={''.join(chat_parts)}"


async def _run_async_streaming(custom_identifier: str) -> tuple[str, str]:
    with async_client_context() as (client, mode):
        async with client:
            with example_attributes(EXAMPLE_NAME, custom_identifier):
                print(f"custom_identifier={custom_identifier}", flush=True)
                print(f"workflow_name={workflow_name(EXAMPLE_NAME)}", flush=True)
                text = await _async_streaming_workflow(client)
                return text, mode


def run_async_streaming() -> None:
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    text = ""
    mode = "unknown"
    try:
        text, mode = asyncio.run(_run_async_streaming(custom_identifier))
    finally:
        respan.flush()
        respan.shutdown()

    print_result(EXAMPLE_NAME, custom_identifier, mode, text)


if __name__ == "__main__":
    run_async_streaming()
