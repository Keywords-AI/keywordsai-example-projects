#!/usr/bin/env python3
"""
Parallelization — Concurrent agent execution.

Runs the same translation agent three times in parallel to get
multiple candidates, then picks the best one. Uses @workflow
with parallel @task decorators.
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from agents import Agent, ItemHelpers, Runner
from respan_tracing import RespanTelemetry
from respan_tracing.decorators import workflow, task
from respan_tracing.instruments import Instruments

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

telemetry = RespanTelemetry(
    app_name="openai-agents-parallelization",
    api_key=os.getenv("RESPAN_API_KEY"),
    is_batching_enabled=False,
    block_instruments={Instruments.REQUESTS, Instruments.URLLIB3},
)

spanish_agent = Agent(
    name="Spanish Translator",
    instructions="You translate the user's message to Spanish.",
)

translation_picker = Agent(
    name="Translation Picker",
    instructions="You pick the best Spanish translation from the given options.",
)


@task(name="translate_candidate")
async def translate_candidate(msg: str) -> str:
    """Generate a single translation candidate."""
    result = await Runner.run(spanish_agent, msg)
    return ItemHelpers.text_message_outputs(result.new_items)


@workflow(name="parallelization_workflow")
async def main_workflow():
    msg = "Good morning, Agent!"

    # Run 3 translations in parallel
    outputs = await asyncio.gather(
        translate_candidate(msg),
        translate_candidate(msg),
        translate_candidate(msg),
    )

    translations = "\n\n".join(outputs)
    print(f"Translations:\n{translations}")

    # Pick the best one
    best = await Runner.run(
        translation_picker,
        f"Input: {msg}\n\nTranslations:\n{translations}",
    )
    print(f"\nBest translation: {best.final_output}")
    return best.final_output


async def main():
    try:
        await main_workflow()
    finally:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
