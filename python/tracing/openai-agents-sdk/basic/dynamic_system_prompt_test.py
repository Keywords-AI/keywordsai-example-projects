from dotenv import load_dotenv

load_dotenv(override=False)
import asyncio
import os
import random
from typing import Literal

import pytest
from agents import Agent, RunContextWrapper, Runner
from agents.tracing import set_trace_processors

from respan_exporter_openai_agents import (
    RespanTraceProcessor,
)

set_trace_processors(
    [
        RespanTraceProcessor(
            os.getenv("RESPAN_API_KEY"),
            endpoint=os.getenv("RESPAN_OAIA_TRACING_ENDPOINT"),
        )
    ]
)


class CustomContext:
    def __init__(self, style: Literal["haiku", "pirate", "robot"]):
        self.style = style


def custom_instructions(
    run_context: RunContextWrapper[CustomContext], agent: Agent[CustomContext]
) -> str:
    context = run_context.context
    if context.style == "haiku":
        return "Only respond in haikus."
    elif context.style == "pirate":
        return "Respond as a pirate."
    else:
        return "Respond as a robot and say 'beep boop' a lot."


agent = Agent(
    name="Chat agent",
    instructions=custom_instructions,
)


@pytest.mark.asyncio
async def test_main():
    choice: Literal["haiku", "pirate", "robot"] = random.choice(
        ["haiku", "pirate", "robot"]
    )
    context = CustomContext(style=choice)
    print(f"Using style: {choice}\n")

    user_message = "Tell me a joke."
    print(f"User: {user_message}")
    result = await Runner.run(agent, user_message, context=context)

    print(f"Assistant: {result.final_output}")


if __name__ == "__main__":
    asyncio.run(test_main())

"""
$ python examples/basic/dynamic_system_prompt.py

Using style: haiku

User: Tell me a joke.
Assistant: Why don't eggs tell jokes?
They might crack each other's shells,
leaving yolk on face.

$ python examples/basic/dynamic_system_prompt.py
Using style: robot

User: Tell me a joke.
Assistant: Beep boop! Why was the robot so bad at soccer? Beep boop... because it kept kicking up a debug! Beep boop!

$ python examples/basic/dynamic_system_prompt.py
Using style: pirate

User: Tell me a joke.
Assistant: Why did the pirate go to school?

To improve his arrr-ticulation! Har har har! 🏴‍☠️
"""
