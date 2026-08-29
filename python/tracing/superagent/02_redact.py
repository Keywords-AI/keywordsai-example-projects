"""Trace a Superagent redaction operation."""

import asyncio
from pathlib import Path

from _shared import (
    configure_environment,
    create_respan,
    create_superagent_client,
    example_marker,
    finish_respan,
)
from respan import propagate_attributes, workflow

SCRIPT_NAME = Path(__file__).name


@workflow(name=SCRIPT_NAME)
async def run_redact(text: str) -> tuple[str, object]:
    config = configure_environment()
    client = create_superagent_client()

    result = await client.redact(
        input=text, model=config.model, entities=["EMAIL", "PHONE"]
    )

    return result.redacted, result.findings


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
                "example": "superagent_redact",
                "script": SCRIPT_NAME,
                "run_id": marker,
                "example_run_id": marker,
            },
        ):
            redacted, findings = await run_redact(
                "Contact Ada at ada@example.com or 415-555-0100."
            )
    finally:
        finish_respan(respan)

    print("redacted:", redacted)
    print("findings:", findings)


if __name__ == "__main__":
    asyncio.run(main())
