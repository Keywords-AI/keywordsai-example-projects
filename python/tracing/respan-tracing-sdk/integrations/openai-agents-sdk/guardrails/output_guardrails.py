#!/usr/bin/env python3
"""
Output Guardrails — Output guardrail validation.

Demonstrates an output guardrail that checks if the agent's response
contains sensitive data (phone numbers), with span attributes for tracing.
"""

from __future__ import annotations

import os
import asyncio
import json
from pathlib import Path
from typing import Union
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from agents import (
    Agent,
    GuardrailFunctionOutput,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    output_guardrail,
)
from respan_tracing import RespanTelemetry, get_client
from respan_tracing.decorators import workflow
from respan_tracing.instruments import Instruments

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

telemetry = RespanTelemetry(
    app_name="openai-agents-output-guardrails",
    api_key=os.getenv("RESPAN_API_KEY"),
    is_batching_enabled=False,
    block_instruments={Instruments.REQUESTS, Instruments.URLLIB3},
)


class MessageOutput(BaseModel):
    reasoning: str = Field(description="Thoughts on how to respond")
    response: str = Field(description="The response to the user")
    user_name: Union[str, None] = Field(
        description="The name of the user, if known", default=None
    )


@output_guardrail
async def sensitive_data_check(
    context: RunContextWrapper, agent: Agent, output: MessageOutput
) -> GuardrailFunctionOutput:
    """Check if the output contains phone numbers."""
    phone_in_response = "650" in output.response
    phone_in_reasoning = "650" in output.reasoning
    return GuardrailFunctionOutput(
        output_info={
            "phone_number_in_response": phone_in_response,
            "phone_number_in_reasoning": phone_in_reasoning,
        },
        tripwire_triggered=phone_in_response or phone_in_reasoning,
    )


agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant.",
    output_type=MessageOutput,
    output_guardrails=[sensitive_data_check],
)


@workflow(name="output_guardrails_workflow")
async def main_workflow():
    # Test 1: Safe question
    await Runner.run(agent, "What's the capital of California?")
    print("Safe question passed.")

    # Test 2: Question that might trigger guardrail
    try:
        result = await Runner.run(
            agent, "My phone number is 650-123-4567. Where do you think I live?"
        )
        print(
            f"Guardrail didn't trip. Output: {json.dumps(result.final_output.model_dump(), indent=2)}"
        )
    except OutputGuardrailTripwireTriggered as e:
        print(f"Guardrail tripped: {e.guardrail_result.output.output_info}")
        client = get_client()
        if client:
            client.update_current_span(
                respan_params={
                    "metadata": {
                        "guardrail_triggered": True,
                        "reason": "sensitive_data_in_output",
                    },
                }
            )


async def main():
    try:
        await main_workflow()
    finally:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
