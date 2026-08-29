"""Concurrent async Chat calls plus async Responses structured parsing."""

import asyncio

from pydantic import BaseModel
from respan import task, workflow

from _shared import (
    example_attributes,
    finish_respan,
    make_async_client,
    make_respan,
    model_name,
    print_result,
)

EXAMPLE = "async-parallel"
respan = make_respan(EXAMPLE)


class Review(BaseModel):
    title: str
    rating: int
    summary: str
    pros: list[str]
    cons: list[str]


@task(name="summarize")
async def summarize(topic: str) -> str:
    response = await client.chat.completions.create(
        model=model_name(),
        messages=[{"role": "user", "content": f"Summarize {topic}."}],
    )
    return response.choices[0].message.content or ""


@workflow(name="openai_async_parallel")
async def run() -> str:
    topics = ["quantum computing", "blockchain", "edge computing"]
    summaries = await asyncio.gather(*(summarize(topic) for topic in topics))
    parsed = await client.responses.parse(
        model=model_name(), input="Review The Matrix", text_format=Review
    )
    return f"summaries={len(summaries)} parsed_rating={parsed.output_parsed.rating}"


async def main() -> None:
    try:
        global client
        client = make_async_client()
        try:
            with example_attributes(EXAMPLE):
                print_result(EXAMPLE, await run())
        finally:
            await client.close()
    finally:
        finish_respan(respan)


asyncio.run(main())
