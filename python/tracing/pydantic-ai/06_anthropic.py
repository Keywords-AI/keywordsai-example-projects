"""Anthropic (Claude) via Respan gateway with PydanticAI instrumentation."""

import os

from dotenv import find_dotenv, load_dotenv
from pydantic_ai import Agent
from respan import Respan
from respan_instrumentation_pydantic_ai import PydanticAIInstrumentor

load_dotenv(find_dotenv(), override=True)

# Route Anthropic calls through the Respan gateway.
respan_api_key = os.environ["RESPAN_API_KEY"]
respan_base_url = os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api").rstrip("/")
gateway_base_url = os.getenv("RESPAN_GATEWAY_BASE_URL", respan_base_url).rstrip("/")
gateway_api_key = os.getenv("RESPAN_GATEWAY_API_KEY", respan_api_key)
anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

# The Anthropic SDK appends /v1/messages, so the gateway URL must end in /anthropic.
os.environ["ANTHROPIC_BASE_URL"] = f"{gateway_base_url}/anthropic"
os.environ["ANTHROPIC_API_KEY"] = gateway_api_key


def main() -> None:
    respan = Respan(
        app_name="pydantic-ai-anthropic",
        api_key=respan_api_key,
        base_url=respan_base_url,
        instrumentations=[PydanticAIInstrumentor()],
    )

    try:
        agent = Agent(
            model=f"anthropic:{anthropic_model}",
            system_prompt="You are a helpful assistant. Keep answers brief.",
        )
        result = agent.run_sync("What is the largest ocean on Earth?")
        print("Agent Output:", result.output)
    finally:
        respan.flush()


if __name__ == "__main__":
    main()
