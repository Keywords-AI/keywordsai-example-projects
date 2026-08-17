from __future__ import annotations

import json

from _shared import (
    deterministic_stream_response,
    example_attributes,
    finish_respan,
    make_custom_identifier,
    make_mock_sync_client,
    make_respan,
    print_result,
    print_start,
    root_request,
    workflow_name,
)
from respan import workflow

EXAMPLE_NAME = "sync-streaming"
PROMPT = "Stream a concise sentence about Mistral observability."


def _response(request):
    payload = json.loads(request.content)
    if payload.get("stream") is not True:
        raise RuntimeError("sync streaming fixture expected stream=true")
    return deterministic_stream_response(
        request,
        fragments=("Sync Mistral ", "streaming stays observable."),
        prompt_tokens=19,
        completion_tokens=7,
    )


def _build_sync_streaming_workflow(client):
    @workflow(name=workflow_name(EXAMPLE_NAME))
    def run(request: dict[str, str]) -> dict[str, object]:
        stream = client.chat.stream(
            model=request["model"],
            messages=[{"role": "user", "content": request["prompt"]}],
            max_tokens=80,
            temperature=0,
        )
        fragments = [
            event.data.choices[0].delta.content or ""
            for event in stream
            if event.data.choices
        ]
        return {
            "content": "".join(fragments),
            "fragments": len(fragments),
        }

    return run


def run_sync_streaming() -> None:
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    result: dict[str, object] = {}

    try:
        with (
            make_mock_sync_client(_response) as client,
            example_attributes(EXAMPLE_NAME, custom_identifier),
        ):
            print_start(EXAMPLE_NAME, custom_identifier, "deterministic-current-sdk")
            result = _build_sync_streaming_workflow(client)(
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
    run_sync_streaming()
