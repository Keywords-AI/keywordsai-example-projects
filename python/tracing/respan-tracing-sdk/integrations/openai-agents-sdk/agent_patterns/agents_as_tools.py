#!/usr/bin/env python3
"""
Agents as Tools — Agent.as_tool() with structured input.

Demonstrates the agents-as-tools pattern where a frontline orchestrator
agent uses other agents as callable tools for translation.
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from agents import Agent, ItemHelpers, MessageOutputItem, Runner
from respan_tracing import RespanTelemetry
from respan_tracing.decorators import workflow
from respan_tracing.instruments import Instruments

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

telemetry = RespanTelemetry(
    app_name="openai-agents-as-tools",
    api_key=os.getenv("RESPAN_API_KEY"),
    is_batching_enabled=False,
    block_instruments={Instruments.REQUESTS, Instruments.URLLIB3},
)

spanish_agent = Agent(
    name="Spanish Translator",
    instructions="You translate the user's message to Spanish.",
    handoff_description="An English to Spanish translator",
)

french_agent = Agent(
    name="French Translator",
    instructions="You translate the user's message to French.",
    handoff_description="An English to French translator",
)

italian_agent = Agent(
    name="Italian Translator",
    instructions="You translate the user's message to Italian.",
    handoff_description="An English to Italian translator",
)

orchestrator_agent = Agent(
    name="Orchestrator",
    instructions=(
        "You are a translation agent. You use the tools given to you to translate. "
        "If asked for multiple translations, you call the relevant tools in order. "
        "You never translate on your own, you always use the provided tools."
    ),
    tools=[
        spanish_agent.as_tool(
            tool_name="translate_to_spanish",
            tool_description="Translate the user's message to Spanish",
        ),
        french_agent.as_tool(
            tool_name="translate_to_french",
            tool_description="Translate the user's message to French",
        ),
        italian_agent.as_tool(
            tool_name="translate_to_italian",
            tool_description="Translate the user's message to Italian",
        ),
    ],
)

synthesizer_agent = Agent(
    name="Synthesizer",
    instructions="You inspect translations, correct them if needed, and produce a final concatenated response.",
)


@workflow(name="agents_as_tools_workflow")
async def main_workflow():
    msg = "Translate 'Good morning' to Spanish and French."

    orchestrator_result = await Runner.run(orchestrator_agent, msg)

    for item in orchestrator_result.new_items:
        if isinstance(item, MessageOutputItem):
            text = ItemHelpers.text_message_output(item)
            if text:
                print(f"  Translation step: {text}")

    synthesizer_result = await Runner.run(
        synthesizer_agent, orchestrator_result.to_input_list()
    )
    print(f"\nFinal response: {synthesizer_result.final_output}")
    return synthesizer_result.final_output


async def main():
    try:
        await main_workflow()
    finally:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
