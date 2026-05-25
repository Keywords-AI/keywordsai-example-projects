"""Trace a Superagent redaction operation."""

import asyncio
from pathlib import Path

from respan import propagate_attributes, workflow

from _shared import configure_environment, create_respan, create_superagent_client

SCRIPT_NAME = Path(__file__).name


@workflow(name=SCRIPT_NAME)
async def run_redact() -> tuple[str, object]:
    config = configure_environment()
    client = create_superagent_client()

    with propagate_attributes(
        customer_identifier="superagent-example-user",
        thread_identifier="superagent-example-thread",
        metadata={"example": "superagent_redact", "script": SCRIPT_NAME},
    ):
        result = await client.redact(
            input="Contact Ada at ada@example.com or 415-555-0100.",
            model=config.model,
            entities=["EMAIL", "PHONE"],
        )

    return result.redacted, result.findings


async def main() -> None:
    respan = create_respan(SCRIPT_NAME)
    try:
        redacted, findings = await run_redact()
    finally:
        respan.flush()
        respan.shutdown()

    print("redacted:", redacted)
    print("findings:", findings)


if __name__ == "__main__":
    asyncio.run(main())
