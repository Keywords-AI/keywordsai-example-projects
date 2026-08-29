"""One successful Responses API call inside a workflow."""

from respan import workflow

from _shared import (
    example_attributes,
    finish_respan,
    make_respan,
    make_sync_client,
    model_name,
    print_result,
)

EXAMPLE = "responses-hello-world"
respan = make_respan(EXAMPLE)


@workflow(name="openai_responses_hello_world")
def run() -> str:
    response = client.responses.create(
        model=model_name(),
        instructions="You are a helpful assistant.",
        input="Say hello in three languages.",
    )
    return response.output_text


try:
    client = make_sync_client()
    try:
        with example_attributes(EXAMPLE):
            print_result(EXAMPLE, run())
    finally:
        client.close()
finally:
    finish_respan(respan)
