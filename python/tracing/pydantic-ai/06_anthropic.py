"""Anthropic Claude through the OpenAI-compatible Respan gateway."""

import os

from _gateway import (
    build_openai_chat_model,
    finish_respan,
    load_gateway_config,
    make_respan,
)
from pydantic_ai import Agent

config = load_gateway_config()
anthropic_model = os.getenv(
    "PYDANTIC_AI_ANTHROPIC_GATEWAY_MODEL",
    "claude-sonnet-4-5-20250929",
)


def main() -> None:
    respan = None
    try:
        respan = make_respan("anthropic")
        agent = Agent(
            model=build_openai_chat_model(config, model_name=anthropic_model),
            system_prompt="You are a helpful assistant. Keep answers brief.",
        )
        result = agent.run_sync("What is the largest ocean on Earth?")
        print("Agent Output:", result.output)
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    main()
