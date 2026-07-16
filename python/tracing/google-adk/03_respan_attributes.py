"""Google ADK run with Respan customer, thread, and metadata attributes."""

import asyncio
from pathlib import Path

from google.adk.agents import Agent
from respan import propagate_attributes, workflow

from _shared import create_gateway_model, create_respan, run_agent_once

SCRIPT_NAME = Path(__file__).name
APP_NAME = SCRIPT_NAME.removesuffix(".py")


@workflow(name=SCRIPT_NAME)
async def run_respan_attributes() -> str:
    agent = Agent(
        name="attribute_agent",
        model=create_gateway_model(),
        instruction="You answer in one concise sentence.",
    )
    with propagate_attributes(
        customer_identifier="google-adk-example-user",
        thread_identifier="google-adk-example-thread",
        metadata={
            "example": "google-adk",
            "scenario": "attributes",
            "script": SCRIPT_NAME,
        },
    ):
        output = await run_agent_once(
            agent=agent,
            app_name=APP_NAME,
            prompt="Explain why trace attributes are useful.",
        )
    print(output)
    return output


async def main() -> None:
    respan = create_respan(APP_NAME)
    try:
        await run_respan_attributes()
    finally:
        respan.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
