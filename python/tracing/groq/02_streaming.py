from __future__ import annotations

from respan import workflow

from _shared import (
    example_attributes,
    make_client,
    make_custom_identifier,
    make_respan,
    model_name,
    print_result,
    workflow_name,
)

EXAMPLE_NAME = "streaming"


@workflow(name=workflow_name(EXAMPLE_NAME))
def _streaming_workflow(client) -> str:
    stream = client.chat.completions.create(
        model=model_name(),
        messages=[
            {
                "role": "user",
                "content": "Write a four-line checklist for reliable LLM traces.",
            }
        ],
        temperature=0,
        stream=True,
    )
    chunks: list[str] = []
    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            chunks.append(content)
    return "".join(chunks)


def run_streaming() -> None:
    respan = make_respan(EXAMPLE_NAME)
    client = make_client()
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    text = ""

    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print(f"custom_identifier={custom_identifier}", flush=True)
            print(f"workflow_name={workflow_name(EXAMPLE_NAME)}", flush=True)
            text = _streaming_workflow(client)
    finally:
        respan.flush()
        respan.shutdown()

    print_result(EXAMPLE_NAME, custom_identifier, text)


if __name__ == "__main__":
    run_streaming()
