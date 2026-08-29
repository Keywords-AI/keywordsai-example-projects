"""A managed-prompt-shaped Chat request using a configurable prompt ID."""

import os

from respan import workflow

from _shared import (
    example_attributes,
    finish_respan,
    make_respan,
    make_sync_client,
    print_result,
)

EXAMPLE = "prompt"
respan = make_respan(EXAMPLE)


@workflow(name="openai_managed_prompt")
def run() -> str:
    response = client.chat.completions.create(
        model="placeholder",
        messages=[],
        extra_body={
            "prompt": {
                "prompt_id": os.getenv("RESPAN_PROMPT_ID", "deterministic-prompt"),
                "schema_version": 2,
                "variables": {"feature_request": "Add order notifications"},
            }
        },
    )
    return response.choices[0].message.content or ""


try:
    client = make_sync_client()
    try:
        with example_attributes(EXAMPLE):
            print_result(EXAMPLE, run())
    finally:
        client.close()
finally:
    finish_respan(respan)
