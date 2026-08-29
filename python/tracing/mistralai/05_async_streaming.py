from __future__ import annotations

import asyncio
import json

from _shared import (
    deterministic_stream_response,
    example_attributes,
    finish_respan,
    make_custom_identifier,
    make_mock_async_client,
    make_respan,
    print_result,
    print_start,
    root_request,
    workflow_name,
)
from respan import workflow

EXAMPLE_NAME = "async-streaming"
PROMPT = "Stream a concise sentence about async Mistral tracing."


def _response(request):
    payload = json.loads(request.content)
    if payload.get("stream") is not True:
        raise RuntimeError("async streaming fixture expected stream=true")
    return deterministic_stream_response(
        request,
        fragments=("Async Mistral ", "streaming keeps complete telemetry."),
        prompt_tokens=23,
        completion_tokens=8,
    )


def _build_async_streaming_workflow(client):
    @workflow(name=workflow_name(EXAMPLE_NAME))
    async def run(request: dict[str, str]) -> dict[str, object]:
        stream = await client.chat.stream_async(
            model=request["model"],
            messages=[{"role": "user", "content": request["prompt"]}],
            max_tokens=80,
            temperature=0,
        )
        fragments = []
        async for event in stream:
            if event.data.choices:
                fragments.append(event.data.choices[0].delta.content or "")
        return {
            "content": "".join(fragments),
            "fragments": len(fragments),
        }

    return run


async def run_async_streaming() -> None:
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    result: dict[str, object] = {}

    try:
        async with make_mock_async_client(_response) as client:
            with example_attributes(EXAMPLE_NAME, custom_identifier):
                print_start(
                    EXAMPLE_NAME, custom_identifier, "deterministic-current-sdk"
                )
                result = await _build_async_streaming_workflow(client)(
                    root_request(EXAMPLE_NAME, PROMPT, stream=True)
                )
    finally:
        finish_respan(respan)

    print_result(
        EXAMPLE_NAME,
        custom_identifier,
        result,
        "deterministic-current-sdk",
    )


if __name__ == "__main__":
    asyncio.run(run_async_streaming())
