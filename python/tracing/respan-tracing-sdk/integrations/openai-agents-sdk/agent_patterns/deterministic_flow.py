#!/usr/bin/env python3
"""
Deterministic Flow — Sequential pipeline with gates.

A three-step agent pipeline:
1. Generate a story outline
2. Validate the outline (quality + genre check)
3. Write the full story (only if validation passes)

Uses @workflow with @task per step.
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel
from agents import Agent, Runner
from respan_tracing import RespanTelemetry
from respan_tracing.decorators import workflow, task
from respan_tracing.instruments import Instruments

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

telemetry = RespanTelemetry(
    app_name="openai-agents-deterministic-flow",
    api_key=os.getenv("RESPAN_API_KEY"),
    is_batching_enabled=False,
    block_instruments={Instruments.REQUESTS, Instruments.URLLIB3},
)

story_outline_agent = Agent(
    name="Outline Generator",
    instructions="Generate a very short story outline based on the user's input.",
)


class OutlineCheckerOutput(BaseModel):
    good_quality: bool
    is_scifi: bool


outline_checker_agent = Agent(
    name="Outline Checker",
    instructions="Read the given story outline, judge the quality, and determine if it is a scifi story.",
    output_type=OutlineCheckerOutput,
)

story_agent = Agent(
    name="Story Writer",
    instructions="Write a short story based on the given outline.",
    output_type=str,
)


@task(name="generate_outline")
async def generate_outline(prompt: str) -> str:
    """Step 1: Generate the outline."""
    result = await Runner.run(story_outline_agent, prompt)
    print("Outline generated.")
    return result.final_output


@task(name="check_outline")
async def check_outline(outline: str) -> OutlineCheckerOutput:
    """Step 2: Validate the outline."""
    result = await Runner.run(outline_checker_agent, outline)
    return result.final_output


@task(name="write_story")
async def write_story(outline: str) -> str:
    """Step 3: Write the story."""
    result = await Runner.run(story_agent, outline)
    return result.final_output


@workflow(name="deterministic_flow_workflow")
async def main_workflow():
    prompt = "A woman with supernatural powers discovers she is the first human to evolve to a higher intelligence."

    # Step 1
    outline = await generate_outline(prompt)

    # Step 2 — Gate
    check = await check_outline(outline)
    assert isinstance(check, OutlineCheckerOutput)

    if not check.good_quality:
        print("Outline is not good quality. Stopping.")
        return

    if not check.is_scifi:
        print("Outline is not a scifi story. Stopping.")
        return

    print("Outline passed validation. Writing story...")

    # Step 3
    story = await write_story(outline)
    print(f"Story:\n{story}")
    return story


async def main():
    try:
        await main_workflow()
    finally:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
