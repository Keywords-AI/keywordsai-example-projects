"""Semantic Kernel chat completion through the Respan gateway."""

import asyncio
from pathlib import Path

from respan import workflow
from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
from semantic_kernel.functions import KernelArguments

from _shared import create_kernel, create_respan, print_result

SCRIPT_NAME = Path(__file__).name
APP_NAME = SCRIPT_NAME.removesuffix(".py")


@workflow(name=SCRIPT_NAME)
async def run_chat_completion() -> str:
    kernel = create_kernel()
    settings = OpenAIChatPromptExecutionSettings(
        service_id="chat",
        temperature=0.2,
        max_tokens=80,
    )
    result = await kernel.invoke_prompt(
        "Reply in one sentence: what does Semantic Kernel help developers build?",
        arguments=KernelArguments(settings=settings),
    )
    output = str(result)
    print_result("chat_completion", output)
    return output


async def main() -> None:
    respan = create_respan(APP_NAME)
    try:
        await run_chat_completion()
    finally:
        respan.flush()
        respan.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
