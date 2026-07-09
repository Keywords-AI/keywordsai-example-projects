#!/usr/bin/env python3
"""
Function Tools — @function_tool with respan @tool decorator.

Wraps OpenAI Agents function tools with the respan @tool decorator
to add tracing hierarchy around tool invocations.
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool
from respan_tracing import RespanTelemetry
from respan_tracing.decorators import workflow, tool
from respan_tracing.instruments import Instruments

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

telemetry = RespanTelemetry(
    app_name="openai-agents-function-tools",
    api_key=os.getenv("RESPAN_API_KEY"),
    is_batching_enabled=False,
    block_instruments={Instruments.REQUESTS, Instruments.URLLIB3},
)


@tool(name="get_weather_tool")
@function_tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return f"The weather in {city} is sunny, 22°C."


@tool(name="get_population_tool")
@function_tool
def get_population(city: str) -> str:
    """Get the population of a city."""
    populations = {
        "tokyo": "14 million",
        "new york": "8.3 million",
        "london": "9 million",
        "paris": "2.2 million",
    }
    return f"The population of {city} is {populations.get(city.lower(), 'unknown')}."


agent = Agent(
    name="City Info Agent",
    instructions="You are a helpful agent that provides city information. Use the available tools to answer questions.",
    tools=[get_weather, get_population],
)


@workflow(name="function_tools_workflow")
async def main_workflow():
    result = await Runner.run(
        agent, input="What's the weather and population of Tokyo?"
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
