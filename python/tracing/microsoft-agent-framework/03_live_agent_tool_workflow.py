"""Optionally run the Agent Framework tool path against the configured gateway."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable

from _shared import (
    close_chat_client,
    create_openai_chat_client,
    create_respan,
    finish_respan,
    live_example_enabled,
    workflow_attributes,
)
from agent_framework import Agent, tool
from respan import Respan, workflow

WORKFLOW_NAME = "microsoft-agent-framework-live-agent-tool-workflow"
QUERY = "Use the lookup_weather tool for Seattle, then answer in one sentence."


@tool
def lookup_weather(city: str) -> str:
    return f"The weather in {city} is sunny and 72F."


def create_live_runner(agent: Agent) -> Callable[[str], Awaitable[dict[str, str]]]:
    @workflow(name=WORKFLOW_NAME)
    async def run_live_agent(query: str) -> dict[str, str]:
        result = await agent.run(query)
        return {"query": query, "answer": str(result)}

    return run_live_agent


async def main() -> None:
    if not live_example_enabled():
        print("skipped optional live path; set RESPAN_MAF_RUN_LIVE=1 to enable")
        return

    client = create_openai_chat_client()
    try:
        agent = Agent(
            client=client,
            name="live_weather_agent",
            instructions="Always call lookup_weather for a weather question.",
            tools=[lookup_weather],
        )
        respan = create_respan(WORKFLOW_NAME)
        run_live_agent = create_live_runner(agent)
        try:
            with Respan.propagate_attributes(**workflow_attributes(WORKFLOW_NAME)):
                result = await asyncio.wait_for(run_live_agent(QUERY), timeout=60)
            print(json.dumps(result, indent=2, sort_keys=True))
        finally:
            finish_respan(respan)
    finally:
        await close_chat_client(client)


if __name__ == "__main__":
    asyncio.run(main())
