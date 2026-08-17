"""Export a deterministic real-Pipecat provider error path."""

from __future__ import annotations

import asyncio
from pathlib import Path

from _pipeline import OfflineLLMService, ProviderHTTPError, run_pipeline
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
WORKFLOW_NAME = "pipecat_expected_error"


async def main() -> None:
    run_marker = marker()
    execution = execution_id()
    respan = create_respan(WORKFLOW_NAME, run_marker)

    @workflow(name=WORKFLOW_NAME)
    async def trace_expected_error(prompt: str) -> None:
        result = await run_pipeline(
            OfflineLLMService(response="", fail_status=401),
            prompt=prompt,
            conversation_id=f"error-{execution}",
        )
        raise ProviderHTTPError(
            result.error or "deterministic provider authorization failure",
            status_code=401,
        )

    try:
        try:
            with Respan.propagate_attributes(
                **workflow_attributes(
                    WORKFLOW_NAME,
                    run_marker,
                    execution,
                    mode="deterministic-error",
                )
            ):
                await trace_expected_error(
                    "Exercise the provider authorization failure path."
                )
        except ProviderHTTPError as exc:
            print_result(
                SCRIPT_NAME,
                {"expected_error": type(exc).__name__, "status_code": exc.status_code},
                run_marker,
            )
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    asyncio.run(main())
