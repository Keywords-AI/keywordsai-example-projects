"""Semantic Kernel automatic plugin/tool invocation traced by Respan."""

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
from semantic_kernel.connectors.ai.function_choice_behavior import (
    FunctionChoiceBehavior,
)
from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
from semantic_kernel.functions import KernelArguments, kernel_function

SCRIPT_NAME = Path(__file__).name
APP_NAME = SCRIPT_NAME.removesuffix(".py")


class TravelPlugin:
    @kernel_function(
        name="get_weather",
        description="Return a deterministic weather summary for a city.",
    )
    def get_weather(self, city: str) -> str:
        return f"{city}: clear, 22 C, light wind."


@workflow(name=SCRIPT_NAME)
async def run_plugin_tool_call(city: str) -> str:
    kernel = create_kernel()
    kernel.add_plugin(TravelPlugin(), plugin_name="Travel")
    settings = OpenAIChatPromptExecutionSettings(
        service_id="chat",
        temperature=0,
        max_tokens=120,
        function_choice_behavior=FunctionChoiceBehavior.Auto(auto_invoke=True),
    )
    result = await kernel.invoke_prompt(
        f"Use the Travel plugin to check the weather in {city}, then summarize it.",
        arguments=KernelArguments(settings=settings),
    )
    output = str(result)
    print_result("tool_call_answer", output)
    return output


async def main() -> None:
    respan = create_respan(APP_NAME)
    try:
        with example_attributes(APP_NAME):
            await run_plugin_tool_call("Tokyo")
    finally:
        try:
            await close_kernel_clients()
        finally:
            respan.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
