from __future__ import annotations

import asyncio

from _shared import (
    chat_text,
    close_provider,
    example_attributes,
    generated_text,
    make_custom_identifier,
    make_model,
    make_respan,
    print_lookup,
    stream_chunk_text,
    workflow_name,
)
from respan import workflow

EXAMPLE_NAME = "async-model-calls"
_MODEL = None


@workflow(name=workflow_name(EXAMPLE_NAME))
async def _async_model_workflow(prompt: str) -> str:
    generated = await _MODEL.agenerate(
        prompt=prompt,
        params={"max_new_tokens": 40},
    )
    generated_stream = await _MODEL.agenerate_stream(
        prompt="Stream an async Watsonx sentence.",
        params={"max_new_tokens": 40},
    )
    generated_chunks = [stream_chunk_text(chunk) async for chunk in generated_stream]

    chat = await _MODEL.achat(
        messages=[{"role": "user", "content": "Give one async chat sentence."}],
        params={"max_new_tokens": 40},
    )
    chat_stream = await _MODEL.achat_stream(
        messages=[{"role": "user", "content": "Stream async chat."}],
        params={"max_new_tokens": 40},
    )
    chat_chunks = [stream_chunk_text(chunk) async for chunk in chat_stream]

    return (
        f"agenerate={generated_text(generated)}\n"
        f"agenerate_stream={''.join(generated_chunks)}\n"
        f"achat={chat_text(chat)}\n"
        f"achat_stream={''.join(chat_chunks)}"
    )


async def _run_async_model_calls(custom_identifier: str) -> str:
    global _MODEL
    model = make_model()
    _MODEL = model
    with example_attributes(EXAMPLE_NAME, custom_identifier):
        try:
            return await _async_model_workflow(
                "Reply asynchronously about Watsonx tracing."
            )
        finally:
            close_provider(model)


def run_async_model_calls() -> None:
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    output = ""

    try:
        output = asyncio.run(_run_async_model_calls(custom_identifier))
    finally:
        respan.shutdown()

    print_lookup(EXAMPLE_NAME, custom_identifier, output)


if __name__ == "__main__":
    run_async_model_calls()
