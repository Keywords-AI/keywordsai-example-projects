"""Run a deterministic failing tool through Agent Framework tracing."""

from __future__ import annotations

import asyncio

from agent_framework import tool

from _shared import create_respan


@tool
def always_fail(reason: str) -> str:
    """Raise a deterministic error for failure-span verification."""
    raise RuntimeError(f"deterministic Agent Framework failure: {reason}")


async def run_failure_example() -> None:
    respan = create_respan("microsoft-agent-framework-deterministic-failure")
    try:
        try:
            await always_fail.invoke(arguments={"reason": "example"})
        except RuntimeError as exc:
            print(f"expected failure: {exc}")
    finally:
        respan.shutdown()


if __name__ == "__main__":
    asyncio.run(run_failure_example())
