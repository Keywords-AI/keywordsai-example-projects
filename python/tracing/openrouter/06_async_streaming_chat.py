"""OpenRouter async streaming completion with full stream finalization."""

from __future__ import annotations

import asyncio

from _shared import close_async, make_async_client, make_respan
from respan import workflow


async def main() -> None:
    respan = None
    client = None
    try:
        respan = make_respan(scenario="async_stream")
        client, model = make_async_client()

        @workflow(name="openrouter_async_streaming_chat")
        async def run(prompt: str) -> str:
            stream = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                stream_options={"include_usage": True},
            )
            parts: list[str] = []
            async with stream:
                async for chunk in stream:
                    if not chunk.choices:
                        continue
                    content = chunk.choices[0].delta.content
                    if content:
                        parts.append(content)
            result = "".join(parts)
            print(result)
            return result

        await run("Explain async stream tracing in one short sentence.")
    finally:
        await close_async(respan=respan, client=client)


if __name__ == "__main__":
    asyncio.run(main())
