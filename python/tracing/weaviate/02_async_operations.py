from __future__ import annotations

import asyncio

from _shared import (
    example_attributes,
    make_custom_identifier,
    make_data,
    make_respan,
    workflow_name,
)
from respan import workflow

EXAMPLE_NAME = "async-operations"


@workflow(name=workflow_name(EXAMPLE_NAME))
async def async_operations(vector: list[float]) -> dict[str, str]:
    object_id = await make_data(async_=True).insert(
        {"text": "Async Weaviate operation"},
        vector=vector,
    )
    return {"object_id": object_id}


async def run_async() -> dict[str, str]:
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    result = {}
    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            result = await async_operations([0.3, 0.2, 0.1])
    finally:
        respan.shutdown()
    print(result)
    return result


if __name__ == "__main__":
    asyncio.run(run_async())
