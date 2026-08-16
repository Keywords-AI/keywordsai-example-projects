import asyncio

from _shared import ToolSpec, run_example


if __name__ == "__main__":
    asyncio.run(
        run_example(
            example_name="06_multi_tool",
            prompts=["Find all Python files and read the first one."],
            tools=[
                ToolSpec("Glob", {"pattern": "*.py"}, ["01_hello_world.py"]),
                ToolSpec(
                    "Read",
                    {"file_path": "01_hello_world.py"},
                    "import asyncio",
                ),
            ],
        )
    )
