#!/usr/bin/env python3
"""
Approval Flow — Tool approval with state persistence.

Demonstrates the human-in-the-loop pattern where certain tool calls
require user approval before execution, with span events for approval tracking.
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool
from respan_tracing import RespanTelemetry, get_client
from respan_tracing.decorators import workflow
from respan_tracing.instruments import Instruments

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

telemetry = RespanTelemetry(
    app_name="openai-agents-approval-flow",
    api_key=os.getenv("RESPAN_API_KEY"),
    is_batching_enabled=False,
    block_instruments={Instruments.REQUESTS, Instruments.URLLIB3},
)


@function_tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email to the specified recipient."""
    return f"Email sent to {to} with subject '{subject}'."


@function_tool
def get_contacts() -> str:
    """Get the user's contact list."""
    return "Contacts: alice@example.com, bob@example.com, carol@example.com"


# Mark send_email as needing approval
send_email_tool = send_email
send_email_tool.needs_approval = True

agent = Agent(
    name="Email Assistant",
    instructions="You help manage emails. Always get contacts first, then compose emails.",
    tools=[get_contacts, send_email],
)


@workflow(name="approval_flow_workflow")
async def main_workflow():
    """Run the agent and simulate approval for sensitive tool calls."""
    result = await Runner.run(
        agent,
        "Get my contacts and then draft an email to Alice about our meeting tomorrow at 3pm.",
    )

    # Record approval event
    client = get_client()
    if client:
        client.add_event(
            "tool_approval",
            {"tool": "send_email", "status": "auto_approved_for_demo"},
        )

    print(result.final_output)
    return result.final_output


async def main():
    try:
        await main_workflow()
    finally:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
