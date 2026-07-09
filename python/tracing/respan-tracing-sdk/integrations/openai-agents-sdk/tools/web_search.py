#!/usr/bin/env python3
"""
Web Search — WebSearchTool traced as a task.

Uses the built-in WebSearchTool from the OpenAI Agents SDK,
with the entire search operation wrapped in a @workflow.
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from agents import Agent, Runner, WebSearchTool
from respan_tracing import RespanTelemetry
from respan_tracing.decorators import workflow
from respan_tracing.instruments import Instruments

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

telemetry = RespanTelemetry(
    app_name="openai-agents-web-search",
    api_key=os.getenv("RESPAN_API_KEY"),
    is_batching_enabled=False,
    block_instruments={Instruments.REQUESTS, Instruments.URLLIB3},
)

agent = Agent(
    name="Web Searcher",
    instructions="You are a helpful agent that searches the web for information.",
    tools=[
        WebSearchTool(
            user_location={"type": "approximate", "city": "New York"}
        )
    ],
)


@workflow(name="web_search_workflow")
async def main_workflow():
    result = await Runner.run(
        agent,
        "Search the web for 'latest AI news' and give me 1 interesting update in a sentence.",
    )
    print(result.final_output)
    return result.final_output


async def main():
    try:
        await main_workflow()
    finally:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
