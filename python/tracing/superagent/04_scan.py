"""Trace a Superagent repository scan when Daytona credentials are available."""

import asyncio
import os
from pathlib import Path

from respan import propagate_attributes, workflow

from _shared import configure_environment, create_respan, create_superagent_client

SCRIPT_NAME = Path(__file__).name


@workflow(name=SCRIPT_NAME)
async def run_scan() -> str:
    configure_environment()
    if not os.getenv("DAYTONA_API_KEY"):
        return "DAYTONA_API_KEY is not set; skipping live scan example."

    client = create_superagent_client()

    with propagate_attributes(
        customer_identifier="superagent-example-user",
        thread_identifier="superagent-example-thread",
        metadata={"example": "superagent_scan", "script": SCRIPT_NAME},
    ):
        result = await client.scan(
            repo="https://github.com/respanai/respan-example-projects",
            model=os.getenv("SUPERAGENT_SCAN_MODEL", "anthropic/claude-sonnet-4-5"),
        )

    return result.result


async def main() -> None:
    respan = create_respan(SCRIPT_NAME)
    try:
        result = await run_scan()
    finally:
        respan.flush()
        respan.shutdown()

    if result.startswith("DAYTONA_API_KEY"):
        print(result)
    else:
        print("scan result:", result[:500])


if __name__ == "__main__":
    asyncio.run(main())
