"""Trace Superagent operations inside Respan workflow and task spans."""

import asyncio
from pathlib import Path

from respan import propagate_attributes, task, workflow

from _shared import configure_environment, create_respan, create_superagent_client

SCRIPT_NAME = Path(__file__).name


@task(name="safety_guard")
async def safety_guard(client, model: str, text: str) -> str:
    result = await client.guard(input=text, model=model, chunk_size=0)
    return result.classification


@task(name="redact_contact_details")
async def redact_contact_details(client, model: str, text: str) -> str:
    result = await client.redact(input=text, model=model, entities=["EMAIL", "PHONE"])
    return result.redacted


@workflow(name=SCRIPT_NAME)
async def safety_pipeline() -> tuple[str, str]:
    config = configure_environment()
    client = create_superagent_client()
    text = "Email security alerts to ops@example.com before running shell commands."
    classification = await safety_guard(client, config.model, text)
    redacted = await redact_contact_details(client, config.model, text)
    return classification, redacted


async def main() -> None:
    respan = create_respan(SCRIPT_NAME)

    with propagate_attributes(
        customer_identifier="superagent-example-user",
        thread_identifier="superagent-example-thread",
        metadata={"example": "superagent_workflow", "script": SCRIPT_NAME},
    ):
        classification, redacted = await safety_pipeline()

    print("classification:", classification)
    print("redacted:", redacted)
    respan.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
