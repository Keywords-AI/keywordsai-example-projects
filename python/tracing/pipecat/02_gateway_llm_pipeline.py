"""Run a real Pipecat OpenAI service through the configured Respan gateway."""

from __future__ import annotations

import asyncio
from pathlib import Path

from _pipeline import OfflineLLMService, run_pipeline
from _shared import (
    create_respan,
    execution_id,
    finish_respan,
    gateway_config,
    load_example_env,
    marker,
    print_result,
    workflow_attributes,
)
from pipecat.services.openai.llm import OpenAILLMService
from respan import Respan, workflow

SCRIPT_NAME = Path(__file__).name
WORKFLOW_NAME = "pipecat_gateway_pipeline"


async def main() -> None:
    load_example_env()
    run_marker = marker()
    execution = execution_id()
    config = gateway_config()
    mode = "live" if config else "deterministic-fallback"
    respan = create_respan(WORKFLOW_NAME, run_marker)
    try:

        @workflow(name=WORKFLOW_NAME)
        async def trace_gateway(prompt: str) -> dict[str, str]:
            service = (
                OpenAILLMService(
                    api_key=config["api_key"],
                    base_url=config["base_url"],
                    settings=OpenAILLMService.Settings(
                        model=config["model"], max_completion_tokens=32
                    ),
                )
                if config
                else OfflineLLMService(response="Pipecat gateway fallback is active.")
            )
            result = await run_pipeline(
                service,
                prompt=prompt,
                conversation_id=f"gateway-{execution}",
            )
            if result.error:
                raise RuntimeError(result.error)
            return {"response": result.text, "status": "completed"}

        with Respan.propagate_attributes(
            **workflow_attributes(WORKFLOW_NAME, run_marker, execution, mode=mode)
        ):
            result = await trace_gateway(
                "Reply with exactly: Pipecat gateway tracing works."
            )
        print_result(SCRIPT_NAME, result, run_marker)
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    asyncio.run(main())
