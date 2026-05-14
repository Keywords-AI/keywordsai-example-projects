"""Basic Google ADK agent call traced by Respan."""

import asyncio
from pathlib import Path

from google.adk.agents import Agent
from respan import workflow

from _shared import create_gateway_model, create_respan, run_agent_once

SCRIPT_NAME = Path(__file__).name
APP_NAME = SCRIPT_NAME.removesuffix(".py")


@workflow(name=SCRIPT_NAME)
async def run_hello_world() -> str:
    agent = Agent(
        name="hello_world_agent",
        model=create_gateway_model(),
        instruction="You answer in one concise sentence.",
    )
    output = await run_agent_once(
        agent=agent,
        app_name=APP_NAME,
        prompt="Say hello from a traced Google ADK agent.",
    )
    print(output)
    return output


async def main() -> None:
    respan = create_respan(APP_NAME)
    try:
        await run_hello_world()
    finally:
        respan.flush()
        respan.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
