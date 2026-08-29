from __future__ import annotations

import asyncio
from typing import Any

from _shared import (
    create_async_pinecone_index,
    create_respan,
    execution_id,
    finish_respan,
    marker,
    print_result,
    to_jsonable,
    workflow_attributes,
)
from respan import Respan, workflow

WORKFLOW_NAME = "pinecone_async_fetch_workflow"


@workflow(name=WORKFLOW_NAME)
async def run_async_fetch(vector_ids: list[str], namespace: str) -> dict[str, Any]:
    index = create_async_pinecone_index()
    try:
        result = await index.fetch(ids=vector_ids, namespace=namespace)
        return to_jsonable({"ids": vector_ids, "namespace": namespace, "fetch": result})
    finally:
        await index.close()


async def main() -> None:
    run_marker = marker()
    execution = execution_id()
    respan = create_respan(WORKFLOW_NAME, run_marker)
    try:
        with Respan.propagate_attributes(
            **workflow_attributes(WORKFLOW_NAME, run_marker, execution)
        ):
            result = await run_async_fetch(["trace-doc"], "respan-example")
        print_result(WORKFLOW_NAME, result, run_marker)
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    asyncio.run(main())
