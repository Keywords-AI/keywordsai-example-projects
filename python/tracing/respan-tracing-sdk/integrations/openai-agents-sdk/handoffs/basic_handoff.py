#!/usr/bin/env python3
"""
Basic Handoff — Triage agent routing to specialized agents.

Demonstrates agent handoffs where a triage agent routes requests
to language-specific agents, traced with @workflow and span updates.
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from agents import Agent, Runner
from respan_tracing import RespanTelemetry, get_client
from respan_tracing.decorators import workflow
from respan_tracing.instruments import Instruments

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

telemetry = RespanTelemetry(
    app_name="openai-agents-basic-handoff",
    api_key=os.getenv("RESPAN_API_KEY"),
    is_batching_enabled=False,
    block_instruments={Instruments.REQUESTS, Instruments.URLLIB3},
)

spanish_agent = Agent(
    name="Spanish Agent",
    instructions="You only speak Spanish.",
)

english_agent = Agent(
    name="English Agent",
    instructions="You only speak English.",
)

triage_agent = Agent(
    name="Triage Agent",
    instructions="Handoff to the appropriate agent based on the language of the request.",
    handoffs=[spanish_agent, english_agent],
)


@workflow(name="basic_handoff_workflow")
async def main_workflow():
    result = await Runner.run(triage_agent, input="Hola, ¿cómo estás?")
    print(result.final_output)

    # Record which agent handled the request
    client = get_client()
    if client:
        client.update_current_span(
            respan_params={
                "metadata": {"final_agent": result.last_agent.name},
            }
        )

    return result.final_output


async def main():
    try:
        await main_workflow()
    finally:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
