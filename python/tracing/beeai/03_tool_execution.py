"""Run a BeeAI tool directly with Respan tracing."""

import asyncio

from respan import workflow

from _shared import create_respan, example_attributes

WORKFLOW_NAME = "BeeAI Tool Execution Example"
respan = create_respan("beeai-tool-execution")

from beeai_framework.tools import tool  # noqa: E402


@tool(
    name="city_summary",
    description="Return a short deterministic city summary for demo tracing.",
)
def city_summary(city: str) -> str:
    return f"{city} is a useful example city for testing agent tool traces."


@workflow(name=WORKFLOW_NAME)
async def run_tool_execution() -> str:
    output = await city_summary.run({"city": "Paris"})
    return output.get_text_content()


async def main() -> None:
    try:
        with example_attributes(WORKFLOW_NAME) as run_id:
            output = await run_tool_execution()
            print(f"Run ID: {run_id}")
            print(f"Tool output: {output}")
    finally:
        respan.flush()


if __name__ == "__main__":
    asyncio.run(main())
