from __future__ import annotations

from _shared import (
    close_provider,
    example_attributes,
    make_custom_identifier,
    make_model,
    make_respan,
    print_lookup,
    stream_chunk_text,
    workflow_name,
)
from respan import workflow

EXAMPLE_NAME = "streaming"
_MODEL = None


@workflow(name=workflow_name(EXAMPLE_NAME))
def _streaming_workflow(text_prompt: str, chat_prompt: str) -> str:
    text_chunks = [
        stream_chunk_text(chunk)
        for chunk in _MODEL.generate_text_stream(
            prompt=text_prompt,
            params={"max_new_tokens": 40},
        )
    ]
    chat_chunks = [
        stream_chunk_text(chunk)
        for chunk in _MODEL.chat_stream(
            messages=[{"role": "user", "content": chat_prompt}],
            params={"max_new_tokens": 40},
        )
    ]
    return f"text_stream={''.join(text_chunks)}\nchat_stream={''.join(chat_chunks)}"


def run_streaming() -> None:
    global _MODEL
    model = make_model()
    _MODEL = model
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    output = ""

    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            output = _streaming_workflow(
                "Stream a short sentence about production traces.",
                "Stream a tiny Watsonx chat reply.",
            )
    finally:
        try:
            close_provider(model)
        finally:
            respan.shutdown()

    print_lookup(EXAMPLE_NAME, custom_identifier, output)


if __name__ == "__main__":
    run_streaming()
