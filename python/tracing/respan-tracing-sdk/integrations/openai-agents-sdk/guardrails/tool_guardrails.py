#!/usr/bin/env python3
"""
Tool Guardrails — Tool input/output guardrails.

Demonstrates guardrails that validate tool inputs and outputs
before and after tool execution, with @workflow and @tool tracing.
"""

from __future__ import annotations

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel
from agents import (
    Agent,
    Runner,
    RunContextWrapper,
    function_tool,
    tool_input_guardrail,
    tool_output_guardrail,
    ToolInputGuardrailTripwireTriggered,
    ToolOutputGuardrailTripwireTriggered,
    GuardrailFunctionOutput,
)
from respan_tracing import RespanTelemetry, get_client
from respan_tracing.decorators import workflow, tool
from respan_tracing.instruments import Instruments

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

telemetry = RespanTelemetry(
    app_name="openai-agents-tool-guardrails",
    api_key=os.getenv("RESPAN_API_KEY"),
    is_batching_enabled=False,
    block_instruments={Instruments.REQUESTS, Instruments.URLLIB3},
)


class SensitivityCheck(BaseModel):
    contains_sensitive: bool
    detail: str


@tool_input_guardrail
async def check_tool_input(
    context: RunContextWrapper, agent: Agent, tool_call: dict
) -> GuardrailFunctionOutput:
    """Block tool calls that contain sensitive patterns."""
    args_str = str(tool_call)
    is_sensitive = "password" in args_str.lower() or "secret" in args_str.lower()
    return GuardrailFunctionOutput(
        output_info=SensitivityCheck(
            contains_sensitive=is_sensitive,
            detail="Sensitive keyword detected in tool input" if is_sensitive else "Clean",
        ),
        tripwire_triggered=is_sensitive,
    )


@tool_output_guardrail
async def check_tool_output(
    context: RunContextWrapper, agent: Agent, tool_result: dict
) -> GuardrailFunctionOutput:
    """Block tool outputs that contain sensitive data."""
    result_str = str(tool_result)
    is_sensitive = "ssn" in result_str.lower() or "credit_card" in result_str.lower()
    return GuardrailFunctionOutput(
        output_info=SensitivityCheck(
            contains_sensitive=is_sensitive,
            detail="Sensitive data in tool output" if is_sensitive else "Clean",
        ),
        tripwire_triggered=is_sensitive,
    )


@tool(name="lookup_user_tool")
@function_tool
def lookup_user(user_id: str) -> str:
    """Look up user information by ID."""
    return f"User {user_id}: name=John Doe, email=john@example.com"


agent = Agent(
    name="Lookup Agent",
    instructions="You help look up user information.",
    tools=[lookup_user],
    tool_input_guardrails=[check_tool_input],
    tool_output_guardrails=[check_tool_output],
)


@workflow(name="tool_guardrails_workflow")
async def main_workflow():
    # Normal lookup — should pass
    try:
        result = await Runner.run(agent, "Look up user ID 'user_123'")
        print(f"Lookup result: {result.final_output}")
    except (ToolInputGuardrailTripwireTriggered, ToolOutputGuardrailTripwireTriggered) as e:
        print(f"Guardrail tripped: {e}")
        client = get_client()
        if client:
            client.update_current_span(
                respan_params={
                    "metadata": {"tool_guardrail_triggered": True},
                }
            )


async def main():
    try:
        await main_workflow()
    finally:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
