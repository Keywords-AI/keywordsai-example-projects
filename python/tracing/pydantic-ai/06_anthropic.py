"""Anthropic Claude through the OpenAI-compatible Respan gateway."""

import os

from pydantic_ai import Agent
from respan import Respan
from respan_instrumentation_pydantic_ai import PydanticAIInstrumentor

from _gateway import build_openai_chat_model, load_gateway_config

config = load_gateway_config()
anthropic_model = os.getenv(
    "PYDANTIC_AI_ANTHROPIC_GATEWAY_MODEL",
    "claude-sonnet-4-5-20250929",
)


def main() -> None:
    respan = Respan(
        app_name="pydantic-ai-anthropic",
        api_key=config.respan_api_key,
        base_url=config.respan_base_url,
        instrumentations=[PydanticAIInstrumentor()],
    )

    agent = Agent(
        model=build_openai_chat_model(config, model_name=anthropic_model),
        system_prompt="You are a helpful assistant. Keep answers brief.",
    )
    result = agent.run_sync("What is the largest ocean on Earth?")
    print("Agent Output:", result.output)


if __name__ == "__main__":
    main()
