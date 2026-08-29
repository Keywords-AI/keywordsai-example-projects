import asyncio

from _shared import (
    create_respan,
    finish_respan,
    print_result,
    with_session,
    workflow_attributes,
)
from respan import Respan, workflow

WORKFLOW_NAME = "mcp_prompt_fetch_workflow"


@workflow(name=WORKFLOW_NAME)
async def run_prompt_fetch_example() -> dict[str, object]:
    async with with_session() as session:
        prompts = await session.list_prompts()
        result = await session.get_prompt(
            "city_research_prompt",
            arguments={"city": "Lisbon"},
        )
        output = {
            "available_prompts": [prompt.name for prompt in prompts.prompts],
            "prompt_name": "city_research_prompt",
            "result": result.messages[0].content.text,
        }
        print_result(WORKFLOW_NAME, output)
        return output


async def main() -> None:
    respan = create_respan(WORKFLOW_NAME)
    try:
        with Respan.propagate_attributes(**workflow_attributes(WORKFLOW_NAME)):
            await run_prompt_fetch_example()
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    asyncio.run(main())
