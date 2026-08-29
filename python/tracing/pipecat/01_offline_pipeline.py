"""Run a deterministic current-Pipecat pipeline and export Respan spans."""

from __future__ import annotations

import asyncio
from pathlib import Path

from _pipeline import OfflineLLMService, run_pipeline
from _shared import (
    create_respan,
    execution_id,
    finish_respan,
    marker,
    print_result,
    workflow_attributes,
)
from respan import Respan, workflow

SCRIPT_NAME = Path(__file__).name
WORKFLOW_NAME = "pipecat_offline_pipeline"


async def main() -> None:
    run_marker = marker()
    execution = execution_id()
    respan = create_respan(WORKFLOW_NAME, run_marker)
    try:

        @workflow(name=WORKFLOW_NAME)
        async def trace_pipeline(prompt: str) -> dict[str, str]:
            result = await run_pipeline(
                OfflineLLMService(response="Pipecat instrumentation is active."),
                prompt=prompt,
                conversation_id=f"offline-{execution}",
            )
            return {"response": result.text, "status": "completed"}

        with Respan.propagate_attributes(
            **workflow_attributes(
                WORKFLOW_NAME, run_marker, execution, mode="deterministic"
            )
        ):
            result = await trace_pipeline(
                "Confirm that the Pipecat pipeline is traced."
            )
        print_result(SCRIPT_NAME, result, run_marker)
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    asyncio.run(main())
