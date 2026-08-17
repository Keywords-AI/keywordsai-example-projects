from __future__ import annotations

from _shared import (
    example_attributes,
    flush_and_shutdown,
    make_client,
    make_custom_identifier,
    make_respan,
    model_name,
    print_result,
    workflow_name,
)
from respan import workflow

EXAMPLE_NAME = "stream-generate"


@workflow(name=workflow_name(EXAMPLE_NAME))
def _stream_generate_workflow(prompt: str) -> str:
    client = make_client()
    try:
        chunks = client.generate(
            model=model_name(),
            prompt=prompt,
            system="Be concise.",
            stream=True,
        )
        return "".join(chunk["response"] for chunk in chunks)
    finally:
        client.close()


def run_stream_generate() -> None:
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    text = ""

    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print(f"custom_identifier={custom_identifier}", flush=True)
            print(f"workflow_name={workflow_name(EXAMPLE_NAME)}", flush=True)
            text = _stream_generate_workflow("Write a five word observability slogan.")
    finally:
        flush_and_shutdown(respan)

    print_result(EXAMPLE_NAME, custom_identifier, text)


if __name__ == "__main__":
    run_stream_generate()
