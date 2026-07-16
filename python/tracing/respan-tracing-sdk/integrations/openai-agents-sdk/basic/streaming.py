#!/usr/bin/env python3
"""
Streaming — Stream agent responses with event tracing.

Uses Runner.run_streamed and stream_events to process response deltas,
wrapped in @workflow and @task decorators to trace each phase.
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, Runner
from respan_tracing import RespanTelemetry
from respan_tracing.decorators import workflow, task
from respan_tracing.instruments import Instruments

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

telemetry = RespanTelemetry(
    app_name="openai-agents-streaming",
    api_key=os.getenv("RESPAN_API_KEY"),
    is_batching_enabled=False,
    block_instruments={Instruments.REQUESTS, Instruments.URLLIB3},
)

agent = Agent(
    name="Joker",
    instructions="You are a helpful assistant that tells jokes.",
)


@task(name="process_stream_events")
async def process_stream_events(result):
    """Process streaming events and print text deltas."""
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(
            event.data, ResponseTextDeltaEvent
        ):
            print(event.data.delta, end="", flush=True)
    print()


@workflow(name="streaming_workflow")
async def main_workflow():
    result = Runner.run_streamed(agent, input="Please tell me 3 short jokes.")
    await process_stream_events(result)


async def main():
    try:
        await main_workflow()
    finally:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
