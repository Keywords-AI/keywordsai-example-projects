from __future__ import annotations

import asyncio

import restate
from _shared import (
    create_respan,
    example_context,
    finish_respan,
    invoke_registered_handler,
)
from respan import workflow

CASE = "expected_error"


@workflow(name="restate_expected_error")
async def expected_error(reason: str) -> None:
    failing = restate.Service("FailureService")

    @failing.handler(name="fail")
    async def fail(_ctx, request: dict[str, str]) -> None:
        raise RuntimeError(request["reason"])

    await invoke_registered_handler(
        failing,
        "fail",
        {"reason": reason},
        invocation_id="failure-service-1",
    )


async def main() -> None:
    respan = create_respan()
    result = ""
    try:
        try:
            with example_context(CASE):
                await expected_error("deterministic Restate handler failure")
        except RuntimeError as exc:
            result = f"expected {type(exc).__name__}"
    finally:
        finish_respan(respan)
    print(result, flush=True)


if __name__ == "__main__":
    asyncio.run(main())
