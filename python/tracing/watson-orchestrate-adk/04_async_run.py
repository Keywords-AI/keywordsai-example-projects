from __future__ import annotations

import asyncio

from _shared import (
    create_respan,
    deterministic_run_client,
    deterministic_watson_runtime,
    example_attributes,
    marker_for,
    workflow_name,
)
from respan import workflow

EXAMPLE_NAME = "async-run"


@workflow(name=workflow_name(EXAMPLE_NAME))
async def async_run(run_id: str) -> dict:
    return await deterministic_run_client().stream_run_with_websocket(
        agent_id="watson-agent-deterministic",
        thread_id="watson-thread-deterministic",
        run_id=run_id,
    )


async def run() -> None:
    marker = marker_for(EXAMPLE_NAME)
    with deterministic_watson_runtime():
        respan = create_respan(EXAMPLE_NAME, marker)
        try:
            with example_attributes(EXAMPLE_NAME, marker):
                result = await async_run("watson-run-deterministic")
        finally:
            respan.shutdown()
    print({"example": EXAMPLE_NAME, "marker": marker, "result": result}, flush=True)


if __name__ == "__main__":
    asyncio.run(run())
