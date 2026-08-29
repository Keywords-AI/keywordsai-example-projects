import asyncio

from _shared import run_example


if __name__ == "__main__":
    asyncio.run(
        run_example(
            example_name="03_multi_turn",
            prompts=["My name is Alice.", "What is my name?"],
            resume=True,
        )
    )
