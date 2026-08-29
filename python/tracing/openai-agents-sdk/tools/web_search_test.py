from dotenv import load_dotenv

load_dotenv(override=False)

import asyncio
import os

import pytest
from agents import Agent, Runner, WebSearchTool, trace
from agents.tracing import set_trace_processors

from respan_exporter_openai_agents import (
    RespanTraceProcessor,
)

set_trace_processors(
    [
        RespanTraceProcessor(
            os.getenv("RESPAN_API_KEY"),
            endpoint=os.getenv("RESPAN_OAIA_TRACING_ENDPOINT"),
        )
    ]
)


@pytest.mark.asyncio
async def test_main():
    agent = Agent(
        name="Web searcher",
        instructions="You are a helpful agent.",
        tools=[
            WebSearchTool(user_location={"type": "approximate", "city": "New York"})
        ],
    )

    with trace("Web search example"):
        result = await Runner.run(
            agent,
            "search the web for 'local sports news' and give me 1 interesting update in a sentence.",
        )
        print(result.final_output)
        # The New York Giants are reportedly pursuing quarterback Aaron Rodgers after his ...


if __name__ == "__main__":
    asyncio.run(test_main())
