from dotenv import load_dotenv

load_dotenv(override=False)
# ==========copy paste below==========
import asyncio
import os

import pytest
from agents import Agent, Runner
from agents.tracing import set_trace_processors, trace

from respan_exporter_openai_agents import RespanTraceProcessor

API_KEY = os.getenv("RESPAN_API_KEY")
ENDPOINT = os.getenv("RESPAN_OAIA_TRACING_ENDPOINT")
BASE_URL = os.getenv("RESPAN_BASE_URL")
set_trace_processors(
    [
        RespanTraceProcessor(
            api_key=API_KEY,
            endpoint=ENDPOINT,
        ),
    ]
)
# client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)

# set_default_openai_client(client)


@pytest.mark.asyncio
async def test_main():
    agent = Agent(name="Assistant", instructions="You only respond in haikus.")

    with trace("Hello world test"):
        result = await Runner.run(agent, "Tell me about recursion in programming.")
        print(result.final_output)
    # Function calls itself,
    # Looping in smaller pieces,
    # Endless by design.


if __name__ == "__main__":
    asyncio.run(test_main())
