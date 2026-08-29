"""Managed-prompt-shaped first turn followed by a normal Chat turn."""

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

EXAMPLE = "prompt-multi-turn"
respan = make_respan(EXAMPLE)


@workflow(name="openai_prompt_conversation")
def run() -> str:
    first = client.chat.completions.create(
        model="placeholder",
        messages=[],
        extra_body={
            "prompt": {
                "prompt_id": os.getenv("RESPAN_PROMPT_ID", "deterministic-prompt"),
                "schema_version": 2,
                "variables": {"feature_request": "Add dark mode"},
            }
        },
    )
    plan = first.choices[0].message.content or ""
    second = client.chat.completions.create(
        model=model_name(),
        messages=[
            {"role": "assistant", "content": plan},
            {"role": "user", "content": "Estimate effort."},
        ],
    )
    return second.choices[0].message.content or ""


try:
    client = make_sync_client()
    try:
        with example_attributes(EXAMPLE):
            print_result(EXAMPLE, run())
    finally:
        client.close()
finally:
    finish_respan(respan)
