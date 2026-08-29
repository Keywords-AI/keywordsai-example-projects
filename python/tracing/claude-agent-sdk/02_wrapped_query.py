import asyncio

from _shared import run_example


if __name__ == "__main__":
    asyncio.run(
        run_example(
            example_name="02_wrapped_query",
            prompts=["Name three primary colors."],
        )
    )
