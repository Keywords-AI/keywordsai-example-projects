"""Deterministic Semantic Kernel function failure traced by Respan."""

import asyncio
from pathlib import Path

from _shared import (
    close_kernel_clients,
    create_kernel,
    create_respan,
    example_attributes,
    print_result,
)
from respan import workflow
from semantic_kernel.exceptions.kernel_exceptions import KernelInvokeException
from semantic_kernel.functions import kernel_function

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
async def run_function_failure(scenario: str) -> None:
    kernel = create_kernel(with_chat_service=False)
    kernel.add_plugin(FailurePlugin(), plugin_name="Failure")
    await kernel.invoke(
        function_name="fail_deterministically",
        plugin_name="Failure",
    )
    raise AssertionError(f"FailurePlugin unexpectedly succeeded for {scenario}")


async def main() -> None:
    respan = create_respan(APP_NAME)
    try:
        with example_attributes(APP_NAME):
            try:
                await run_function_failure("deterministic")
            except (RuntimeError, KernelInvokeException) as exc:
                print_result(
                    "failure", f"Caught expected failure: {type(exc).__name__}"
                )
    finally:
        try:
            await close_kernel_clients()
        finally:
            respan.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
