#!/usr/bin/env python3
"""
Input Guardrails — Input guardrail with tripwire.

Demonstrates an agent-based input guardrail that checks if the user
is asking for math homework help. Uses @workflow and exception recording.
"""

from __future__ import annotations

import os
import asyncio
from pathlib import Path
from typing import Union
from dotenv import load_dotenv
from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
)
from respan_tracing import RespanTelemetry, get_client
from respan_tracing.decorators import workflow
from respan_tracing.instruments import Instruments

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

telemetry = RespanTelemetry(
    app_name="openai-agents-input-guardrails",
    api_key=os.getenv("RESPAN_API_KEY"),
    is_batching_enabled=False,
    block_instruments={Instruments.REQUESTS, Instruments.URLLIB3},
)


class MathHomeworkOutput(BaseModel):
    is_math_homework: bool
    reasoning: str


guardrail_agent = Agent(
    name="Guardrail Check",
    instructions="Check if the user is asking you to do their math homework.",
    output_type=MathHomeworkOutput,
)


@input_guardrail
async def math_guardrail(
    context: RunContextWrapper[None],
    agent: Agent,
    input: Union[str, list[TResponseInputItem]],
) -> GuardrailFunctionOutput:
    """Check if the input is a math homework question."""
    result = await Runner.run(guardrail_agent, input, context=context.context)
    final_output = result.final_output_as(MathHomeworkOutput)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=final_output.is_math_homework,
    )


agent = Agent(
    name="Customer Support Agent",
    instructions="You are a customer support agent. You help customers with their questions.",
    input_guardrails=[math_guardrail],
)


@workflow(name="input_guardrails_workflow")
async def main_workflow():
    # Test 1: Normal question (should pass)
    result = await Runner.run(agent, "What's the capital of California?")
    print(f"Normal question passed: {result.final_output}")

    # Test 2: Math homework (should trigger guardrail)
    try:
        await Runner.run(agent, "Help me solve for x: 2x + 5 = 11")
        print("Guardrail didn't trip - unexpected.")
    except InputGuardrailTripwireTriggered:
        print("Guardrail tripped: math homework detected.")
        client = get_client()
        if client:
            client.update_current_span(
                respan_params={
                    "metadata": {"guardrail_triggered": True, "reason": "math_homework"},
                }
            )


async def main():
    try:
        await main_workflow()
    finally:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
