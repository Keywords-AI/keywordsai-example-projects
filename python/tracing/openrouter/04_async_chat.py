"""OpenRouter async chat completion."""

from __future__ import annotations

import asyncio

from _shared import make_async_client, make_respan
from respan import workflow

respan = make_respan()
client, model = make_async_client()


@workflow(name="openrouter_async_chat")
async def run() -> str:
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": "Explain async tracing in one short sentence.",
            }
        ],
    )
    return response.choices[0].message.content or ""


async def main() -> None:
    try:
        print(await run())
    finally:
        respan.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
