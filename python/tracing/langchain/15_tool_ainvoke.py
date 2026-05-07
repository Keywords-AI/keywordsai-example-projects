"""Tool ainvoke."""

import asyncio

from langchain_core.tools import tool

from _shared import flush, init_telemetry, tracing_config


@tool
async def async_add_numbers(left: int, right: int) -> int:
    """Add two integers asynchronously."""
    return left + right


async def tool_ainvoke() -> None:
    telemetry = init_telemetry("langchain-tool-ainvoke")
    try:
        response = await async_add_numbers.ainvoke(
            {"left": 21, "right": 21},
            config=tracing_config("tool_ainvoke"),
        )
        print(response)
    finally:
        flush(telemetry)


if __name__ == "__main__":
    asyncio.run(tool_ainvoke())
