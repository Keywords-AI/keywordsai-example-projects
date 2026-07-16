"""Bare-minimum sanity check: instrument + run one agent call."""

from pydantic_ai import Agent
from respan import Respan
from respan_instrumentation_pydantic_ai import PydanticAIInstrumentor

from _gateway import build_openai_chat_model, load_gateway_config

config = load_gateway_config()


def main() -> None:
    respan = Respan(
        app_name="pydantic-ai-hello-world",
        api_key=config.respan_api_key,
        base_url=config.respan_base_url,
        instrumentations=[PydanticAIInstrumentor()],
    )

    try:
        agent = Agent(
            model=build_openai_chat_model(config),
            system_prompt="You are a helpful assistant.",
        )
        result = agent.run_sync("What is the capital of France?")
        print("Agent Output:", result.output)
    finally:
        respan.flush()


if __name__ == "__main__":
    main()
