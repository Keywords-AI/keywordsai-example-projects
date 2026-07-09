import asyncio

from respan import Respan, workflow

from _shared import create_respan, with_session, workflow_attributes

WORKFLOW_NAME = "mcp_resource_read_workflow"


@workflow(name=WORKFLOW_NAME)
async def run_resource_read_example() -> None:
    async with with_session() as session:
        resources = await session.list_resources()
        result = await session.read_resource("profile://city/paris")
        print("resources:", [str(resource.uri) for resource in resources.resources])
        print("resource:", result.contents[0].text)


async def main() -> None:
    respan = create_respan()
    try:
        with Respan.propagate_attributes(**workflow_attributes(WORKFLOW_NAME)):
            await run_resource_read_example()
    finally:
        respan.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
