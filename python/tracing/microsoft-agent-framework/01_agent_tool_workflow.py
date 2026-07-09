"""Run an Agent Framework agent with a tool inside a workflow."""

from __future__ import annotations

import asyncio

from agent_framework import (
    Agent,
    WorkflowBuilder,
    WorkflowContext,
    executor,
    tool,
)

from _shared import create_openai_chat_client, create_respan


@tool
def lookup_weather(city: str) -> str:
    """Return a deterministic weather report for a city."""
    return f"The weather in {city} is sunny and 72F."


async def run_agent_tool_workflow() -> str:
    respan = create_respan("microsoft-agent-framework-agent-tool-workflow")

    try:
        client = create_openai_chat_client()
        agent = Agent(
            client=client,
            name="weather_agent",
            instructions=(
                "You are a concise weather assistant. Use the lookup_weather "
                "tool whenever a user asks about weather."
            ),
            tools=[lookup_weather],
        )

        @executor(id="ask_weather_agent", input=str, workflow_output=str)
        async def ask_weather_agent(query: str, ctx: WorkflowContext) -> None:
            result = await agent.run(query)
            await ctx.yield_output(str(result))

        workflow = WorkflowBuilder(
            start_executor=ask_weather_agent,
            output_from=[ask_weather_agent],
            name="microsoft-agent-framework-agent-tool-workflow",
        ).build()
        events = await workflow.run("Use the weather tool for Seattle, then summarize.")
        outputs = [str(output) for output in events.get_outputs()]
        result = "\n".join(outputs)
        print(result)
        return result
    finally:
        respan.shutdown()


if __name__ == "__main__":
    asyncio.run(run_agent_tool_workflow())
