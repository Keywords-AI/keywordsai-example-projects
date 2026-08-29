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

CASE = "service_success"


@workflow(name="restate_service_success")
async def service_success(customer: str) -> dict[str, str]:
    greeter = restate.Service("GreeterService")

    @greeter.handler(name="greet")
    async def greet(_ctx, request: dict[str, str]) -> dict[str, str]:
        return {"message": f"Hello, {request['customer']}"}

    return await invoke_registered_handler(
        greeter,
        "greet",
        {"customer": customer},
        invocation_id="greeter-service-1",
    )


async def main() -> None:
    respan = create_respan()
    try:
        with example_context(CASE):
            print(await service_success("Ada"), flush=True)
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    asyncio.run(main())
