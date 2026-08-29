import asyncio

from _shared import ToolSpec, run_example


if __name__ == "__main__":
    asyncio.run(
        run_example(
            example_name="05_tool_use",
            prompts=["List the Python files in the current directory."],
            tools=[ToolSpec("Glob", {"pattern": "*.py"}, ["01_hello_world.py"])],
        )
    )
