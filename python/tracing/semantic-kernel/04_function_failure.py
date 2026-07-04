"""Deterministic Semantic Kernel function failure traced by Respan."""

import asyncio
from pathlib import Path

from respan import workflow
from semantic_kernel.exceptions.kernel_exceptions import KernelInvokeException
from semantic_kernel.functions import kernel_function

from _shared import create_kernel, create_respan, print_result

SCRIPT_NAME = Path(__file__).name
APP_NAME = SCRIPT_NAME.removesuffix(".py")


class FailurePlugin:
    @kernel_function(
        name="fail_deterministically",
        description="Raise a predictable error for tracing failure behavior.",
    )
    def fail_deterministically(self) -> str:
        raise RuntimeError("semantic-kernel deterministic failure")


@workflow(name=SCRIPT_NAME)
async def run_function_failure() -> str:
    kernel = create_kernel(with_chat_service=False)
    kernel.add_plugin(FailurePlugin(), plugin_name="Failure")
    try:
        await kernel.invoke(
            function_name="fail_deterministically",
            plugin_name="Failure",
        )
    except (RuntimeError, KernelInvokeException) as exc:
        message = f"Caught expected failure: {exc}"
        print_result("failure", message)
        return message
    raise AssertionError("FailurePlugin.fail_deterministically unexpectedly succeeded")


async def main() -> None:
    respan = create_respan(APP_NAME)
    try:
        await run_function_failure()
    finally:
        respan.flush()
        respan.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
