"""Tracing a Pydantic AI agent that uses tools.

This example is written so the agent is required to use a tool (add) to answer,
ensuring the exported trace contains tool-call spans.
"""

from pydantic_ai import Agent
from respan import Respan, workflow
from respan_instrumentation_pydantic_ai import PydanticAIInstrumentor

from _gateway import build_openai_chat_model, load_gateway_config

config = load_gateway_config()


def build_agent() -> Agent:
    agent = Agent(
        build_openai_chat_model(config),
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
        api_key=config.respan_api_key,
        base_url=config.respan_base_url,
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
