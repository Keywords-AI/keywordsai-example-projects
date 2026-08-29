"""Three Responses calls linked by previous_response_id."""

from respan import workflow

from _shared import (
    example_attributes,
    finish_respan,
    make_respan,
    make_sync_client,
    model_name,
    print_result,
)

EXAMPLE = "responses-multi-turn"
respan = make_respan(EXAMPLE)


@workflow(name="openai_responses_conversation")
def run() -> str:
    first = client.responses.create(
        model=model_name(), input="Capital of France?", store=True
    )
    second = client.responses.create(
        model=model_name(),
        input="Population?",
        previous_response_id=first.id,
        store=True,
    )
    third = client.responses.create(
        model=model_name(),
        input="Three landmarks?",
        previous_response_id=second.id,
        store=True,
    )
    return third.output_text


try:
    client = make_sync_client()
    try:
        with example_attributes(EXAMPLE):
            print_result(EXAMPLE, run())
    finally:
        client.close()
finally:
    finish_respan(respan)
