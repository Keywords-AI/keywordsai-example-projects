"""Google ADK tool call traced by Respan."""

import asyncio
from pathlib import Path

from google.adk.agents import Agent
from respan import workflow

from _shared import create_gateway_model, create_respan, run_agent_once

SCRIPT_NAME = Path(__file__).name
APP_NAME = SCRIPT_NAME.removesuffix(".py")


def get_weather(city: str) -> str:
    """Return a deterministic weather report for a city."""
    return f"{city}: sunny, 72F, light wind"


@workflow(name=SCRIPT_NAME)
async def run_tool_use() -> str:
    agent = Agent(
        name="weather_agent",
        model=create_gateway_model(),
        instruction=(
            "Use the get_weather tool when weather is requested. "
            "Keep the final answer concise."
        ),
        tools=[get_weather],
    )
    output = await run_agent_once(
        agent=agent,
        app_name=APP_NAME,
        prompt="Use get_weather for San Francisco and summarize the result.",
    )
    print(output)
    return output


async def main() -> None:
    respan = create_respan(APP_NAME)
    try:
        await run_tool_use()
    finally:
        respan.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
