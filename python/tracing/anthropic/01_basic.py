"""Trace one basic Anthropic Messages call."""

from respan import workflow

from _shared import (
    example_attributes,
    make_client,
    make_respan,
    message_text,
    model_name,
    print_result,
    workflow_name,
)

CASE_ID = "basic"


@workflow(name=workflow_name(CASE_ID))
def run_basic() -> str:
    response = make_client().messages.create(
        model=model_name(),
        max_tokens=64,
        messages=[
            {
                "role": "user",
                "content": "Explain Python tracing in one concise sentence.",
            }
        ],
    )
    return message_text(response)


def main() -> None:
    respan = make_respan()
    try:
        with example_attributes(respan, CASE_ID):
            output = run_basic()
    finally:
        respan.shutdown()
    print_result(CASE_ID, output)


if __name__ == "__main__":
    main()
