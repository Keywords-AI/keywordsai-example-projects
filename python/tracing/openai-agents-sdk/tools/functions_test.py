from dotenv import load_dotenv

load_dotenv(override=False)
# ==========copy the below==========
import asyncio
import os

import pytest
from agents import Agent, Runner, function_tool
from agents.tracing import set_trace_processors

from respan_exporter_openai_agents import (
    RespanTraceProcessor,
)

set_trace_processors(
    [
        RespanTraceProcessor(
            os.getenv("RESPAN_API_KEY"),
            endpoint="http://localhost:8000/api/openai/v1/traces/ingest",
        ),
    ]
)


@function_tool
def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny."


agent = Agent(
    name="Hello world",
    instructions="You are a helpful agent.",
    tools=[get_weather],
)


@pytest.mark.asyncio
async def test_main():
    result = await Runner.run(agent, input="What's the weather in Tokyo?")
    print(result.final_output)
    # The weather in Tokyo is sunny.


if __name__ == "__main__":
    asyncio.run(test_main())
