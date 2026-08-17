from __future__ import annotations

from _shared import (
    example_attributes,
    execution_id,
    finish_respan,
    make_client,
    make_respan,
    marker,
    model_name,
    print_result,
    workflow_name,
)
from respan import workflow

EXAMPLE_NAME = "streaming-chat"


@workflow(name=workflow_name(EXAMPLE_NAME))
def trace_stream(prompt: str) -> dict[str, str]:
    client = make_client()
    content: list[str] = []
    try:
        stream = client.chat.completions.create(
            model=model_name(),
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            stream_options={"include_usage": True},
        )
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content.append(chunk.choices[0].delta.content)
        return {"response": "".join(content)}
    finally:
        client.close()


def main() -> None:
    run_marker = marker()
    execution = execution_id()
    respan = make_respan(EXAMPLE_NAME, run_marker)
    try:
        with example_attributes(
            EXAMPLE_NAME, run_marker, execution, mode="deterministic"
        ):
            result = trace_stream("Stream a short Portkey tracing confirmation.")
        print_result(EXAMPLE_NAME, run_marker, result)
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    main()
