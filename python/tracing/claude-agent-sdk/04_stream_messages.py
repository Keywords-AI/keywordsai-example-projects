import asyncio

from _shared import run_example


if __name__ == "__main__":
    asyncio.run(
        run_example(
            example_name="04_stream_messages",
            prompts=["Write a haiku about programming."],
        )
    )
