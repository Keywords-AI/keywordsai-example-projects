"""Chat Completions streaming with explicit close and exact usage."""

from respan import workflow

from _shared import (
    example_attributes,
    finish_respan,
    make_respan,
    make_sync_client,
    model_name,
    print_result,
)

EXAMPLE = "streaming"
respan = make_respan(EXAMPLE)


@workflow(name="openai_chat_streaming")
def run() -> str:
    parts: list[str] = []
    stream = client.chat.completions.create(
        model=model_name(),
        messages=[{"role": "user", "content": "Write a Python haiku."}],
        stream=True,
        stream_options={"include_usage": True},
    )
    with stream:
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                parts.append(chunk.choices[0].delta.content)
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
