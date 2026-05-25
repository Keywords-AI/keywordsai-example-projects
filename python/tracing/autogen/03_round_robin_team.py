"""AutoGen round-robin team conversation traced by Respan."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
from respan import Respan, propagate_attributes, workflow
from respan_instrumentation_autogen import AutoGenInstrumentor

SCRIPT_NAME = Path(__file__).name
ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(ROOT_ENV, override=True)

RESPAN_API_KEY = os.environ["RESPAN_API_KEY"]
RESPAN_BASE_URL = os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api")
RESPAN_MODEL = os.getenv("RESPAN_MODEL", "gpt-4o-mini")
MODEL_INFO = {
    "vision": False,
    "function_calling": True,
    "json_output": True,
    "structured_output": True,
    "family": "unknown",
}


@workflow(name=SCRIPT_NAME)
async def run_round_robin_team() -> None:
    model_client = OpenAIChatCompletionClient(
        model=RESPAN_MODEL,
        api_key=RESPAN_API_KEY,
        base_url=RESPAN_BASE_URL,
        model_info=MODEL_INFO,
    )
    planner = AssistantAgent(
        name="planner",
        model_client=model_client,
        system_message=(
            "Create a compact implementation plan with exactly three numbered steps."
        ),
    )
    reviewer = AssistantAgent(
        name="reviewer",
        model_client=model_client,
        system_message=(
            "Review the plan briefly. If it is clear, end your response with APPROVED."
        ),
    )
    termination = TextMentionTermination("APPROVED") | MaxMessageTermination(4)
    team = RoundRobinGroupChat(
        [planner, reviewer],
        termination_condition=termination,
    )

    try:
        with propagate_attributes(
            customer_identifier="autogen-example-user",
            thread_identifier="autogen-team-thread",
            metadata={"script": SCRIPT_NAME},
        ):
            result = await team.run(
                task="Plan a small release checklist for a new Python tracing plugin."
            )
        for message in result.messages:
            content = getattr(message, "content", None)
            if content:
                print(f"{message.source}: {content}")
    finally:
        await model_client.close()


async def main() -> None:
    respan = Respan(
        api_key=RESPAN_API_KEY,
        base_url=RESPAN_BASE_URL,
        instrumentations=[AutoGenInstrumentor()],
        metadata={"example": "autogen-round-robin-team", "script": SCRIPT_NAME},
    )
    try:
        await run_round_robin_team()
    finally:
        respan.flush()


if __name__ == "__main__":
    asyncio.run(main())
