"""Run a deterministic Agent Framework agent/tool workflow."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable
from typing import Any

from _shared import (
    close_chat_client,
    create_deterministic_chat_client,
    create_respan,
    finish_respan,
    workflow_attributes,
)
from agent_framework import (
    Agent,
    WorkflowBuilder,
    WorkflowContext,
    executor,
    tool,
)
from respan import Respan, task, workflow

WORKFLOW_NAME = "microsoft-agent-framework-agent-tool-workflow"
NATIVE_WORKFLOW_NAME = "microsoft-agent-framework-native-weather-workflow"
QUERY = "Use the weather tool for Seattle, then summarize."


@tool
def lookup_weather(city: str) -> str:
    """Return a deterministic weather report for a city."""
    return f"The weather in {city} is sunny and 72F."


def build_agent_workflow(client: Any):
    """Build the native workflow before Respan starts to avoid a build-only trace."""
    agent = Agent(
        client=client,
        name="weather_agent",
        instructions=(
            "You are a concise weather assistant. Use the lookup_weather "
            "tool whenever a user asks about weather."
        ),
        tools=[lookup_weather],
    )

    @task(name="invoke_weather_agent")
    async def invoke_weather_agent(query: str) -> str:
        return str(await agent.run(query))

    @executor(id="ask_weather_agent", input=str, workflow_output=str)
    async def ask_weather_agent(query: str, ctx: WorkflowContext) -> None:
        await ctx.yield_output(await invoke_weather_agent(query))

    return WorkflowBuilder(
        start_executor=ask_weather_agent,
        output_from=[ask_weather_agent],
        name=NATIVE_WORKFLOW_NAME,
    ).build()


def create_traced_runner(
    native_workflow: Any,
) -> Callable[[str], Awaitable[dict[str, str]]]:
    @workflow(name=WORKFLOW_NAME)
    async def run_agent_tool_workflow(query: str) -> dict[str, str]:
        events = await native_workflow.run(query)
        outputs = [str(output) for output in events.get_outputs()]
        return {"query": query, "answer": "\n".join(outputs)}

    return run_agent_tool_workflow


async def main() -> None:
    client = create_deterministic_chat_client()
    try:
        native_workflow = build_agent_workflow(client)
        respan = create_respan(WORKFLOW_NAME)
        run_agent_tool_workflow = create_traced_runner(native_workflow)
        try:
            with Respan.propagate_attributes(**workflow_attributes(WORKFLOW_NAME)):
                result = await run_agent_tool_workflow(QUERY)
            print(json.dumps(result, indent=2, sort_keys=True))
        finally:
            finish_respan(respan)
    finally:
        await close_chat_client(client)


if __name__ == "__main__":
    asyncio.run(main())
