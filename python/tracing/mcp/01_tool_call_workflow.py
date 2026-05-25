import asyncio

from respan import Respan, workflow

from _shared import create_respan, with_session, workflow_attributes

WORKFLOW_NAME = "mcp_tool_call_workflow"


@workflow(name=WORKFLOW_NAME)
async def run_tool_call_example() -> None:
    async with with_session() as session:
        tools = await session.list_tools()
        result = await session.call_tool(
            "summarize_city",
            arguments={"city": "Paris"},
        )
        print("tools:", [tool.name for tool in tools.tools])
        print("tool result:", result.content[0].text)


async def main() -> None:
    respan = create_respan()
    try:
        with Respan.propagate_attributes(**workflow_attributes(WORKFLOW_NAME)):
            await run_tool_call_example()
        respan.flush()
    finally:
        respan.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
