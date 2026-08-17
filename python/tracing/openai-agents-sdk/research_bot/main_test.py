from dotenv import load_dotenv

loaded = load_dotenv(override=False)
import asyncio
import os

import pytest
from agents import set_trace_processors

from respan_exporter_openai_agents import (
    RespanTraceProcessor,
)

from .manager import ResearchManager

set_trace_processors(
    [
        RespanTraceProcessor(
            os.getenv("RESPAN_API_KEY"),
            endpoint=os.getenv("RESPAN_OAIA_TRACING_ENDPOINT"),
        )
    ]
)


@pytest.mark.asyncio
async def test_main() -> None:
    query = "What is the capital of France?"
    await ResearchManager().run(query)


if __name__ == "__main__":
    asyncio.run(test_main())
