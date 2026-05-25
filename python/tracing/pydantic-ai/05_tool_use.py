"""Tracing a Pydantic AI agent that uses tools.

This example is written so the agent is required to use a tool (add) to answer,
ensuring the exported trace contains tool-call spans.
"""

import os
from dotenv import find_dotenv, load_dotenv

from pydantic_ai import Agent
from respan import Respan, workflow
from respan_instrumentation_pydantic_ai import PydanticAIInstrumentor

load_dotenv(find_dotenv(), override=True)

# Route LLM calls through the Respan gateway.
respan_api_key = os.environ["RESPAN_API_KEY"]
respan_base_url = os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api").rstrip("/")
gateway_api_key = os.getenv("RESPAN_GATEWAY_API_KEY", respan_api_key)
respan_model = os.getenv("RESPAN_MODEL", "gpt-4o")

os.environ["OPENAI_BASE_URL"] = respan_base_url
os.environ["OPENAI_API_KEY"] = gateway_api_key


def build_agent() -> Agent:
    agent = Agent(
        f"openai:{respan_model}",
        system_prompt=(
            "You are a calculator assistant. You must use the provided tools for any arithmetic. "
            "Never compute numbers yourself; always call the add tool when asked to add numbers."
        ),
    )

    @agent.tool_plain
    def add(a: int, b: int) -> int:
        """Add two numbers together."""
        return a + b

    return agent


@workflow(name="calculator_agent_run")
def run_calculator_agent(prompt: str) -> str:
    agent = build_agent()
    result = agent.run_sync(prompt)
    return result.output


def main() -> None:
    respan = Respan(
        app_name="pydantic-ai-tool-use",
        api_key=respan_api_key,
        base_url=respan_base_url,
        instrumentations=[PydanticAIInstrumentor()],
    )

    try:
        output = run_calculator_agent(
            "Use your add tool to compute 15 + 27, then reply with the result."
        )
        print("Agent Output:", output)
    finally:
        respan.flush()


if __name__ == "__main__":
    main()
