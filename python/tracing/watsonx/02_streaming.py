from __future__ import annotations

from respan import workflow

from _shared import (
    example_attributes,
    make_custom_identifier,
    make_model,
    make_respan,
    print_lookup,
    stream_chunk_text,
    workflow_name,
)

EXAMPLE_NAME = "streaming"


@workflow(name=workflow_name(EXAMPLE_NAME))
def _streaming_workflow(model) -> str:
    text_chunks = [
        stream_chunk_text(chunk)
        for chunk in model.generate_text_stream(
            prompt="Stream a short sentence about production traces.",
            params={"max_new_tokens": 40},
        )
    ]
    chat_chunks = [
        stream_chunk_text(chunk)
        for chunk in model.chat_stream(
            messages=[{"role": "user", "content": "Stream a tiny Watsonx chat reply."}],
            params={"max_new_tokens": 40},
        )
    ]
    return f"text_stream={''.join(text_chunks)}\nchat_stream={''.join(chat_chunks)}"


def run_streaming() -> None:
    model = make_model()
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    output = ""

    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            output = _streaming_workflow(model)
    finally:
        respan.shutdown()

    print_lookup(EXAMPLE_NAME, custom_identifier, output)


if __name__ == "__main__":
    run_streaming()
