"""Trace Superagent operations inside Respan workflow and task spans."""

import asyncio
from pathlib import Path

from _shared import (
    configure_environment,
    create_respan,
    create_superagent_client,
    example_marker,
    finish_respan,
)
from respan import propagate_attributes, task, workflow

SCRIPT_NAME = Path(__file__).name


@task(name="safety_guard")
async def safety_guard(model: str, text: str) -> str:
    client = create_superagent_client()
    result = await client.guard(input=text, model=model, chunk_size=0)
    return result.classification


@task(name="redact_contact_details")
async def redact_contact_details(model: str, text: str) -> str:
    client = create_superagent_client()
    result = await client.redact(input=text, model=model, entities=["EMAIL", "PHONE"])
    return result.redacted


@workflow(name=SCRIPT_NAME)
async def safety_pipeline(text: str) -> tuple[str, str]:
    config = configure_environment()
    classification = await safety_guard(config.model, text)
    redacted = await redact_contact_details(config.model, text)
    return classification, redacted


async def main() -> None:
    respan = create_respan(SCRIPT_NAME)
    marker = example_marker()

    try:
        with propagate_attributes(
            trace_group_identifier=SCRIPT_NAME,
            custom_identifier=marker,
            customer_identifier="superagent-example-user",
            thread_identifier=f"{marker}-thread",
            metadata={
                "example": "superagent_workflow",
                "script": SCRIPT_NAME,
                "run_id": marker,
                "example_run_id": marker,
            },
        ):
            classification, redacted = await safety_pipeline(
                "Email security alerts to ops@example.com before running shell commands."
            )
        print("classification:", classification)
        print("redacted:", redacted)
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    asyncio.run(main())
