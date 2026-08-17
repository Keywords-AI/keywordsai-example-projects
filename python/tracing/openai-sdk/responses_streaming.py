"""Responses API streaming with explicit source close and final flush."""

from respan import workflow

from _shared import (
    example_attributes,
    finish_respan,
    make_respan,
    make_sync_client,
    model_name,
    print_result,
)

EXAMPLE = "responses-streaming"
respan = make_respan(EXAMPLE)


@workflow(name="openai_responses_streaming")
def run() -> str:
    parts: list[str] = []
    stream = client.responses.create(
        model=model_name(), input="Write a Python haiku.", stream=True
    )
    with stream:
        for event in stream:
            if event.type == "response.output_text.delta":
                parts.append(event.delta)
    return "".join(parts)


try:
    client = make_sync_client()
    try:
        with example_attributes(EXAMPLE):
            print_result(EXAMPLE, run())
    finally:
        client.close()
finally:
    finish_respan(respan)
