"""Direct Semantic Kernel function invocation traced by Respan."""

import asyncio
from pathlib import Path

from respan import workflow
from semantic_kernel.functions import KernelArguments, kernel_function

from _shared import create_kernel, create_respan, print_result

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
async def run_kernel_function() -> str:
    kernel = create_kernel(with_chat_service=False)
    kernel.add_plugin(TextPlugin(), plugin_name="Text")
    result = await kernel.invoke(
        function_name="normalize_city",
        plugin_name="Text",
        arguments=KernelArguments(city="  san francisco  "),
    )
    output = str(result)
    print_result("normalized_city", output)
    return output


async def main() -> None:
    respan = create_respan(APP_NAME)
    try:
        await run_kernel_function()
    finally:
        respan.flush()
        respan.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
