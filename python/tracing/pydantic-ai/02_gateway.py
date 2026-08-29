"""Route LLM calls through Respan gateway with content capture options."""

from _gateway import (
    build_openai_chat_model,
    finish_respan,
    load_gateway_config,
    make_respan,
)
from pydantic_ai import Agent

config = load_gateway_config()


def main() -> None:
    respan = None
    try:
        respan = make_respan("gateway")
        agent = Agent(
            model=build_openai_chat_model(config),
            system_prompt="You are a helpful assistant.",
        )
        result = agent.run_sync("What is the capital of France?")
        print("Agent Output:", result.output)
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    main()
