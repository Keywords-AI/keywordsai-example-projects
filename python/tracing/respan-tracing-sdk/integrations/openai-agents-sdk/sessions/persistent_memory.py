#!/usr/bin/env python3
"""
Persistent Memory — SQLite session for multi-turn context.

Demonstrates multi-turn conversation with persistent memory using
a simple in-memory store, with @workflow per turn and session metadata.
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from agents import Agent, Runner
from respan_tracing import RespanTelemetry, get_client
from respan_tracing.decorators import workflow, task
from respan_tracing.instruments import Instruments

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

telemetry = RespanTelemetry(
    app_name="openai-agents-persistent-memory",
    api_key=os.getenv("RESPAN_API_KEY"),
    is_batching_enabled=False,
    block_instruments={Instruments.REQUESTS, Instruments.URLLIB3},
)

agent = Agent(
    name="Memory Assistant",
    instructions=(
        "You are a helpful assistant with memory. "
        "Remember details the user shares and reference them in later turns."
    ),
)


class ConversationSession:
    """Simple session that maintains conversation history across turns."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.history = []

    def add_turn(self, role: str, content: str):
        self.history.append({"role": role, "content": content})

    def get_input(self):
        return list(self.history)


@task(name="conversation_turn")
async def conversation_turn(session: ConversationSession, user_message: str) -> str:
    """Run a single conversation turn with session context."""
    session.add_turn("user", user_message)

    result = await Runner.run(agent, session.get_input())
    response = result.final_output

    session.add_turn("assistant", response)

    # Record session metadata
    client = get_client()
    if client:
        client.update_current_span(
            respan_params={
                "metadata": {
                    "session_id": session.session_id,
                    "turn_count": len(session.history) // 2,
                },
            }
        )

    return response


@workflow(name="persistent_memory_workflow")
async def main_workflow():
    session = ConversationSession(session_id="demo-session-001")

    # Turn 1: Share information
    response1 = await conversation_turn(session, "My name is Alice and I live in Tokyo.")
    print(f"Turn 1: {response1}")

    # Turn 2: Ask about something else
    response2 = await conversation_turn(session, "What's a good restaurant recommendation?")
    print(f"Turn 2: {response2}")

    # Turn 3: Test memory recall
    response3 = await conversation_turn(session, "What's my name and where do I live?")
    print(f"Turn 3: {response3}")


async def main():
    try:
        await main_workflow()
    finally:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
