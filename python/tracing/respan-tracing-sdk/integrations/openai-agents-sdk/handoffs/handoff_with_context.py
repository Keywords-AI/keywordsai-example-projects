#!/usr/bin/env python3
"""
Handoff with Context — Handoff with input data and message filters.

Demonstrates handoff() with input_filter to control what context
is passed to the next agent, traced with @workflow and respan_params metadata.
"""

from __future__ import annotations

import os
import random
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from agents import Agent, HandoffInputData, Runner, function_tool, handoff
from agents.extensions import handoff_filters
from respan_tracing import RespanTelemetry, get_client
from respan_tracing.decorators import workflow
from respan_tracing.instruments import Instruments

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

telemetry = RespanTelemetry(
    app_name="openai-agents-handoff-context",
    api_key=os.getenv("RESPAN_API_KEY"),
    is_batching_enabled=False,
    block_instruments={Instruments.REQUESTS, Instruments.URLLIB3},
)


@function_tool
def random_number(max: int) -> int:
    """Return a random integer between 0 and the given maximum."""
    return random.randint(0, max)


def spanish_handoff_filter(
    handoff_message_data: HandoffInputData,
) -> HandoffInputData:
    """Remove tool-related messages before handing off to the Spanish agent."""
    handoff_message_data = handoff_filters.remove_all_tools(handoff_message_data)
    return handoff_message_data


first_agent = Agent(
    name="Assistant",
    instructions="Be extremely concise.",
    tools=[random_number],
)

spanish_agent = Agent(
    name="Spanish Assistant",
    instructions="You only speak Spanish and are extremely concise.",
    handoff_description="A Spanish-speaking assistant.",
)

second_agent = Agent(
    name="Router Assistant",
    instructions=(
        "Be a helpful assistant. If the user speaks Spanish, handoff to the Spanish assistant."
    ),
    handoffs=[handoff(spanish_agent, input_filter=spanish_handoff_filter)],
)


@workflow(name="handoff_with_context_workflow")
async def main_workflow():
    # Step 1: Initial conversation
    result = await Runner.run(first_agent, input="Hi, my name is Sora.")
    print("Step 1 done")

    # Step 2: Use a tool
    result = await Runner.run(
        second_agent,
        input=result.to_input_list()
        + [{"content": "Generate a random number between 0 and 100.", "role": "user"}],
    )
    print("Step 2 done")

    # Step 3: Trigger handoff to Spanish agent
    result = await Runner.run(
        second_agent,
        input=result.to_input_list()
        + [{"content": "Por favor habla en español. ¿Cuál es mi nombre?", "role": "user"}],
    )
    print("Step 3 done")

    # Record handoff metadata
    client = get_client()
    if client:
        client.update_current_span(
            respan_params={
                "metadata": {
                    "handoff_target": result.last_agent.name,
                    "filter_applied": "remove_all_tools",
                },
            }
        )

    print(f"\nFinal output: {result.final_output}")
    return result.final_output


async def main():
    try:
        await main_workflow()
    finally:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
