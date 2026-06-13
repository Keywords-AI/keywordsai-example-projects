from __future__ import annotations

import asyncio

from respan import workflow

from _shared import (
    chat_text,
    example_attributes,
    generated_text,
    make_custom_identifier,
    make_model,
    make_respan,
    print_lookup,
    stream_chunk_text,
    workflow_name,
)

EXAMPLE_NAME = "async-model-calls"


@workflow(name=workflow_name(EXAMPLE_NAME))
async def _async_model_workflow(model) -> str:
    generated = await model.agenerate(
        prompt="Reply asynchronously about Watsonx tracing.",
        params={"max_new_tokens": 40},
    )
    generated_stream = await model.agenerate_stream(
        prompt="Stream an async Watsonx sentence.",
        params={"max_new_tokens": 40},
    )
    generated_chunks = [stream_chunk_text(chunk) async for chunk in generated_stream]

    chat = await model.achat(
        messages=[{"role": "user", "content": "Give one async chat sentence."}],
        params={"max_new_tokens": 40},
    )
    chat_stream = await model.achat_stream(
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
    model = make_model()
    with example_attributes(EXAMPLE_NAME, custom_identifier):
        return await _async_model_workflow(model)


def run_async_model_calls() -> None:
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    output = ""

    try:
        output = asyncio.run(_run_async_model_calls(custom_identifier))
    finally:
        respan.flush()
        respan.shutdown()

    print_lookup(EXAMPLE_NAME, custom_identifier, output)


if __name__ == "__main__":
    run_async_model_calls()
