from dotenv import load_dotenv

load_dotenv(override=True)
from openai import AsyncOpenAI
import pytest
# ==========copy paste below==========
import asyncio
import os
from agents import Agent, Runner, set_default_openai_client
from agents.tracing import set_trace_processors, trace
from keywordsai_exporter_openai_agents import KeywordsAITraceProcessor
API_KEY = os.getenv("KEYWORDSAI_API_KEY")
ENDPOINT = os.getenv("KEYWORDSAI_OAIA_TRACING_ENDPOINT")
BASE_URL = os.getenv("KEYWORDSAI_BASE_URL")
set_trace_processors(
    [
        KeywordsAITraceProcessor(
            api_key=API_KEY,
            endpoint=ENDPOINT,
        ),
    ]
)
# client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)

# set_default_openai_client(client)


@pytest.mark.asyncio
async def test_main():
    agent = Agent(
        name="Assistant",
        instructions="You only respond in haikus."
    )

    with trace("Hello world test"):
        result = await Runner.run(agent, "Tell me about recursion in programming.")
        print(result.final_output)
    # Function calls itself,
    # Looping in smaller pieces,
    # Endless by design.


if __name__ == "__main__":
    asyncio.run(test_main())
