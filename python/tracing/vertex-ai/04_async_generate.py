from __future__ import annotations

import asyncio

from _shared import (
    deterministic_model,
    deterministic_vertex_runtime,
    example_attributes,
    make_respan,
    marker_for,
    workflow_name,
)
from respan import workflow

EXAMPLE_NAME = "async-generate"


@workflow(name=workflow_name(EXAMPLE_NAME))
async def async_generate(prompt: str) -> str:
    model = deterministic_model()
    response = await model.generate_content_async(prompt)
    return response.text


async def run() -> None:
    marker = marker_for(EXAMPLE_NAME)
    with deterministic_vertex_runtime():
        respan = make_respan(EXAMPLE_NAME, marker)
        try:
            with example_attributes(EXAMPLE_NAME, marker):
                result = await async_generate("Trace an async Vertex response.")
        finally:
            respan.shutdown()
    print({"example": EXAMPLE_NAME, "marker": marker, "result": result}, flush=True)


if __name__ == "__main__":
    asyncio.run(run())
