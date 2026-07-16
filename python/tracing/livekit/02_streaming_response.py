from __future__ import annotations

import asyncio

from _shared import (
    MockLiveKitLLM,
    chat_context,
    example_attributes,
    finish_respan,
    make_custom_identifier,
    make_respan,
    print_result,
    print_start,
)


async def main() -> None:
    example_name = "02-streaming-response"
    custom_identifier = make_custom_identifier(example_name)
    respan = make_respan(example_name)
    try:
        print_start(example_name, custom_identifier)
        model = MockLiveKitLLM()
        chunks: list[str] = []
        with example_attributes(example_name, custom_identifier):
            stream = model.chat(
                chat_ctx=chat_context("Stream a short LiveKit reply."),
                extra_kwargs={"scenario": "stream"},
            )
            async with stream:
                async for chunk in stream:
                    if chunk.delta and chunk.delta.content:
                        chunks.append(chunk.delta.content)
        print_result("streamed_text", "".join(chunks))
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    asyncio.run(main())
