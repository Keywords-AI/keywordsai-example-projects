"""Trace a Superagent repository scan when Daytona credentials are available."""

import asyncio
import os
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
async def run_scan(repo: str) -> str:
    configure_environment()
    if not os.getenv("DAYTONA_API_KEY"):
        return "DAYTONA_API_KEY is not set; skipping live scan example."

    client = create_superagent_client()

    result = await client.scan(
        repo=repo,
        model=os.getenv("SUPERAGENT_SCAN_MODEL", "anthropic/claude-sonnet-4-5"),
    )

    return result.result


async def main() -> None:
    respan = create_respan(SCRIPT_NAME)
    marker = example_marker()
    try:
        with propagate_attributes(
            trace_group_identifier=SCRIPT_NAME,
            custom_identifier=marker,
            metadata={
                "example": "superagent_scan",
                "script": SCRIPT_NAME,
                "run_id": marker,
                "example_run_id": marker,
            },
        ):
            result = await run_scan(
                "https://github.com/respanai/respan-example-projects"
            )
    finally:
        finish_respan(respan)

    if result.startswith("DAYTONA_API_KEY"):
        print(result)
    else:
        print("scan result:", result[:500])


if __name__ == "__main__":
    asyncio.run(main())
