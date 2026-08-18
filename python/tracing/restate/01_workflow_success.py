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

CASE = "workflow_success"


@workflow(name="restate_workflow_success")
async def workflow_success(order_id: str) -> dict[str, str]:
    checkout = restate.Workflow("CheckoutWorkflow")

    @checkout.main(name="run")
    async def run(_ctx, request: dict[str, str]) -> dict[str, str]:
        return {"order_id": request["order_id"], "status": "accepted"}

    return await invoke_registered_handler(
        checkout,
        "run",
        {"order_id": order_id},
        invocation_id="checkout-workflow-1",
        key=order_id,
    )


async def main() -> None:
    respan = create_respan()
    try:
        with example_context(CASE):
            print(await workflow_success("order-42"), flush=True)
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    asyncio.run(main())
