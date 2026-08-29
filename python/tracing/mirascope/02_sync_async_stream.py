"""Consume real Mirascope sync and async stream response objects."""

from __future__ import annotations

import asyncio
import json

from _shared import (
    close_model_provider,
    create_deterministic_model,
    create_respan,
    finish_respan,
    workflow_attributes,
)
from mirascope import llm
from respan import workflow

SYNC_WORKFLOW = "mirascope-sync-stream"
ASYNC_WORKFLOW = "mirascope-async-stream"


def create_sync_runner(model: llm.Model):
    @workflow(name=SYNC_WORKFLOW)
    def run_sync_stream(prompt: str) -> str:
        response = model.stream(prompt)
        return "".join(response.text_stream()).strip()

    return run_sync_stream


def create_async_runner(model: llm.Model):
    @workflow(name=ASYNC_WORKFLOW)
    async def run_async_stream(prompt: str) -> str:
        response = await model.stream_async(prompt)
        return "".join([part async for part in response.text_stream()]).strip()

    return run_async_stream


async def main() -> None:
    respan = create_respan("mirascope-sync-async-stream")
    model: llm.Model | None = None
    try:
        model = create_deterministic_model()
        sync_runner = create_sync_runner(model)
        async_runner = create_async_runner(model)
        with respan.propagate_attributes(
            **workflow_attributes(SYNC_WORKFLOW, "02_sync_async_stream.py")
        ):
            sync_result = sync_runner("Stream the deterministic sync reply.")
        with respan.propagate_attributes(
            **workflow_attributes(ASYNC_WORKFLOW, "02_sync_async_stream.py")
        ):
            async_result = await async_runner("Stream the deterministic async reply.")
        print(json.dumps({"sync": sync_result, "async": async_result}, sort_keys=True))
    finally:
        try:
            if model is not None:
                close_model_provider(model)
        finally:
            finish_respan(respan)


if __name__ == "__main__":
    asyncio.run(main())
