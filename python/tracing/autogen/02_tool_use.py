"""AutoGen assistant run that uses a Python tool and exports tool spans."""

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
async def run_tool_agent() -> str:
    async def estimate_latency(service: str, requests_per_minute: int) -> str:
        """Estimate API latency for a service under load."""
        baseline_ms = 120
        load_penalty_ms = max(requests_per_minute - 100, 0) // 4
        return f"{service}: about {baseline_ms + load_penalty_ms} ms p95 latency"

    model_client = OpenAIChatCompletionClient(
        model=RESPAN_MODEL,
        api_key=RESPAN_API_KEY,
        base_url=RESPAN_BASE_URL,
        model_info=MODEL_INFO,
    )
    agent = AssistantAgent(
        name="capacity_planner",
        model_client=model_client,
        tools=[estimate_latency],
        reflect_on_tool_use=True,
        system_message=(
            "Use the estimate_latency tool before answering. "
            "Summarize the estimate in one short paragraph."
        ),
    )

    try:
        result = await agent.run(
            task=(
                "Estimate the p95 latency for the tracing-api service at "
                "240 requests per minute."
            )
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
            "example": "autogen-tool-use",
            "script": SCRIPT_NAME,
            "run_id": run_id,
        },
    )
    try:
        with propagate_attributes(
            customer_identifier="autogen-example-user",
            thread_identifier="autogen-tool-thread",
            group_identifier=SCRIPT_NAME,
            custom_identifier=run_id,
            metadata={"script": SCRIPT_NAME, "run_id": run_id},
        ):
            print(await run_tool_agent())
    finally:
        respan.shutdown()
    print(f"RESPAN_EXAMPLE_RUN_ID={run_id}")


if __name__ == "__main__":
    asyncio.run(main())
