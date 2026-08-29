"""OpenRouter async chat completion."""

from __future__ import annotations

import asyncio

from _shared import close_async, make_async_client, make_respan
from respan import workflow


async def main() -> None:
    respan = None
    client = None
    try:
        respan = make_respan(scenario="async_chat")
        client, model = make_async_client()

        @workflow(name="openrouter_async_chat")
        async def run(prompt: str) -> str:
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content or ""

        print(await run("Explain async tracing in one short sentence."))
    finally:
        await close_async(respan=respan, client=client)


if __name__ == "__main__":
    asyncio.run(main())
