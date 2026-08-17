"""A managed-prompt-shaped request sent through the Responses API."""

import os

from respan import workflow

from _shared import (
    example_attributes,
    finish_respan,
    make_respan,
    make_sync_client,
    model_name,
    print_result,
)

EXAMPLE = "responses-prompt"
respan = make_respan(EXAMPLE)


@workflow(name="openai_responses_prompt")
def run() -> str:
    response = client.responses.create(
        model=model_name(),
        input="Add order-status notifications.",
        extra_body={
            "respan_params": {
                "prompt": {
                    "prompt_id": os.getenv("RESPAN_PROMPT_ID", "deterministic-prompt"),
                    "schema_version": 2,
                    "variables": {"feature_request": "Add order notifications"},
                }
            }
        },
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
