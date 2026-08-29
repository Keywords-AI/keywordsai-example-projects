from dotenv import load_dotenv

load_dotenv(override=False)
import asyncio
import os

import pytest

# ==========copy the below==========
from agents import Agent, Runner
from agents.tracing import set_trace_processors, trace

from respan_exporter_openai_agents import RespanTraceProcessor

set_trace_processors(
    [
        RespanTraceProcessor(
            api_key=os.getenv("RESPAN_API_KEY"),
            endpoint=os.getenv("RESPAN_OAIA_TRACING_ENDPOINT"),
        ),
    ]
)

spanish_agent = Agent(
    name="Spanish agent",
    instructions="You only speak Spanish.",
)

english_agent = Agent(
    name="English agent",
    instructions="You only speak English",
)

triage_agent = Agent(
    name="Triage agent",
    instructions="Handoff to the appropriate agent based on the language of the request.",
    handoffs=[spanish_agent, english_agent],
)


@pytest.mark.asyncio
async def test_main():
    with trace("Handoff test"):
        result = await Runner.run(triage_agent, input="Hola, ¿cómo estás?")
        print(result.final_output)
    # ¡Hola! Estoy bien, gracias por preguntar. ¿Y tú, cómo estás?


if __name__ == "__main__":
    asyncio.run(test_main())
