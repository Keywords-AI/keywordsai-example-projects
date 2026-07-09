#!/usr/bin/env python3
"""
Hello World — Simple agent with @workflow wrapper.

Initializes RespanTelemetry (which auto-instruments OpenAI SDK calls),
then wraps the agent run in a @workflow decorator to add structured hierarchy.
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from agents import Agent, Runner
from respan_tracing import RespanTelemetry
from respan_tracing.decorators import workflow
from respan_tracing.instruments import Instruments

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

telemetry = RespanTelemetry(
    app_name="openai-agents-hello-world",
    api_key=os.getenv("RESPAN_API_KEY"),
    is_batching_enabled=False,
    block_instruments={Instruments.REQUESTS, Instruments.URLLIB3},
)

agent = Agent(
    name="Assistant",
    instructions="You only respond in haikus.",
)


@workflow(name="hello_world_workflow")
async def main_workflow():
    result = await Runner.run(agent, "Tell me about recursion in programming.")
    print(result.final_output)
    return result.final_output


async def main():
    try:
        await main_workflow()
    finally:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
