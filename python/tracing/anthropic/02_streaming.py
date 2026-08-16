"""Trace and assemble an Anthropic Messages stream."""

from respan import workflow

from _shared import (
    example_attributes,
    make_client,
    make_respan,
    model_name,
    print_result,
    workflow_name,
)

CASE_ID = "streaming"


@workflow(name=workflow_name(CASE_ID))
def run_streaming() -> str:
    with make_client().messages.stream(
        model=model_name(),
        max_tokens=64,
        messages=[
            {
                "role": "user",
                "content": "Stream one concise sentence about trace context.",
            }
        ],
    ) as stream:
        text = "".join(stream.text_stream)
        stream.get_final_message()
    return text


def main() -> None:
    respan = make_respan()
    try:
        with example_attributes(respan, CASE_ID):
            output = run_streaming()
    finally:
        respan.shutdown()
    print_result(CASE_ID, output)


if __name__ == "__main__":
    main()
