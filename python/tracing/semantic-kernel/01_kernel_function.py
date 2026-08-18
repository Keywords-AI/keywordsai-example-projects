"""Direct Semantic Kernel function invocation traced by Respan."""

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
from semantic_kernel.functions import KernelArguments, kernel_function

SCRIPT_NAME = Path(__file__).name
APP_NAME = SCRIPT_NAME.removesuffix(".py")


class TextPlugin:
    @kernel_function(
        name="normalize_city",
        description="Normalize a city name for downstream prompts.",
    )
    def normalize_city(self, city: str) -> str:
        return city.strip().title()


@workflow(name=SCRIPT_NAME)
async def run_kernel_function(city: str) -> str:
    kernel = create_kernel(with_chat_service=False)
    kernel.add_plugin(TextPlugin(), plugin_name="Text")
    result = await kernel.invoke(
        function_name="normalize_city",
        plugin_name="Text",
        arguments=KernelArguments(city=city),
    )
    output = str(result)
    print_result("normalized_city", output)
    return output


async def main() -> None:
    respan = create_respan(APP_NAME)
    try:
        with example_attributes(APP_NAME):
            await run_kernel_function("  san francisco  ")
    finally:
        try:
            await close_kernel_clients()
        finally:
            respan.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
