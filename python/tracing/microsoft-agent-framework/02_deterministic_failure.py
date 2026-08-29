"""Run a deterministic failing tool through Agent Framework tracing."""

from __future__ import annotations

import asyncio
import json

from _shared import create_respan, finish_respan, workflow_attributes
from agent_framework import tool
from respan import Respan, workflow

WORKFLOW_NAME = "microsoft-agent-framework-deterministic-failure"


@tool
def always_fail(reason: str) -> str:
    """Raise a deterministic error for failure-span verification."""
    raise RuntimeError(f"deterministic Agent Framework failure: {reason}")


@workflow(name=WORKFLOW_NAME)
async def run_failure_example(reason: str) -> dict[str, str]:
    try:
        await always_fail.invoke(arguments={"reason": reason})
    except RuntimeError as exc:
        return {"reason": reason, "expected_error": str(exc)}
    raise AssertionError("always_fail unexpectedly succeeded")


async def main() -> None:
    respan = create_respan(WORKFLOW_NAME)
    try:
        with Respan.propagate_attributes(**workflow_attributes(WORKFLOW_NAME)):
            result = await run_failure_example("example")
        print(json.dumps(result, indent=2, sort_keys=True))
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    asyncio.run(main())
