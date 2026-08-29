"""Trace an expected real Superagent provider/model failure."""

import asyncio
from pathlib import Path

from _shared import (
    create_respan,
    create_superagent_client,
    example_marker,
    finish_respan,
)
from respan import propagate_attributes, workflow

SCRIPT_NAME = Path(__file__).name


@workflow(name=SCRIPT_NAME)
async def expected_failure(text: str) -> None:
    client = create_superagent_client()
    await client.guard(
        input=text,
        model="openai-compatible/definitely-not-a-real-model",
        chunk_size=0,
    )


async def main() -> None:
    marker = example_marker()
    respan = create_respan(SCRIPT_NAME)
    try:
        try:
            with propagate_attributes(
                trace_group_identifier=SCRIPT_NAME,
                custom_identifier=marker,
                metadata={
                    "example": "superagent_expected_error",
                    "script": SCRIPT_NAME,
                    "run_id": marker,
                    "example_run_id": marker,
                },
            ):
                await expected_failure(
                    "This call should fail with an unavailable model."
                )
        except Exception as exc:  # noqa: BLE001 - provider SDK exception surface varies
            print({"expected_error": type(exc).__name__})
        else:
            raise AssertionError("expected Superagent failure did not occur")
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    asyncio.run(main())
