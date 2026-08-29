"""Single AutoGen assistant run traced by Respan."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

from autogen_agentchat.agents import AssistantAgent
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
async def run_assistant_agent() -> str:
    model_client = OpenAIChatCompletionClient(
        model=RESPAN_MODEL,
        api_key=RESPAN_API_KEY,
        base_url=RESPAN_BASE_URL,
        model_info=MODEL_INFO,
    )
    agent = AssistantAgent(
        name="assistant",
        model_client=model_client,
        system_message="You answer with concise, practical engineering advice.",
    )

    try:
        result = await agent.run(
            task="In one sentence, explain why tracing helps multi-agent apps."
        )
        return str(result.messages[-1].content)
    finally:
        await model_client.close()


async def main() -> None:
    run_id = os.getenv("RESPAN_EXAMPLE_RUN_ID", f"autogen-{Path(__file__).stem}")
    respan = Respan(
        api_key=RESPAN_API_KEY,
        base_url=RESPAN_BASE_URL,
        instrumentations=[AutoGenInstrumentor()],
        metadata={
            "example": "autogen-assistant-run",
            "script": SCRIPT_NAME,
            "run_id": run_id,
        },
    )
    try:
        with propagate_attributes(
            customer_identifier="autogen-example-user",
            thread_identifier="autogen-assistant-thread",
            group_identifier=SCRIPT_NAME,
            custom_identifier=run_id,
            metadata={"script": SCRIPT_NAME, "run_id": run_id},
        ):
            print(await run_assistant_agent())
    finally:
        respan.shutdown()
    print(f"RESPAN_EXAMPLE_RUN_ID={run_id}")


if __name__ == "__main__":
    asyncio.run(main())
