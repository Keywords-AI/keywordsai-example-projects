import asyncio

from respan import Respan, workflow

from _shared import create_respan, with_session, workflow_attributes

WORKFLOW_NAME = "mcp_prompt_fetch_workflow"


@workflow(name=WORKFLOW_NAME)
async def run_prompt_fetch_example() -> None:
    async with with_session() as session:
        prompts = await session.list_prompts()
        result = await session.get_prompt(
            "city_research_prompt",
            arguments={"city": "Lisbon"},
        )
        print("prompts:", [prompt.name for prompt in prompts.prompts])
        print("prompt:", result.messages[0].content.text)


async def main() -> None:
    respan = create_respan()
    try:
        with Respan.propagate_attributes(**workflow_attributes(WORKFLOW_NAME)):
            await run_prompt_fetch_example()
    finally:
        respan.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
