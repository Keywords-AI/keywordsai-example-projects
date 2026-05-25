"""Route LLM calls through Respan gateway with content capture options."""

import os

from dotenv import find_dotenv, load_dotenv
from pydantic_ai import Agent
from respan import Respan
from respan_instrumentation_pydantic_ai import PydanticAIInstrumentor

load_dotenv(find_dotenv(), override=True)

# Route LLM calls through the Respan gateway.
respan_api_key = os.environ["RESPAN_API_KEY"]
respan_base_url = os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api").rstrip("/")
gateway_api_key = os.getenv("RESPAN_GATEWAY_API_KEY", respan_api_key)
respan_model = os.getenv("RESPAN_MODEL", "gpt-4o")

os.environ["OPENAI_BASE_URL"] = respan_base_url
os.environ["OPENAI_API_KEY"] = gateway_api_key


def main() -> None:
    respan = Respan(
        app_name="pydantic-ai-gateway",
        api_key=respan_api_key,
        base_url=respan_base_url,
        instrumentations=[
            PydanticAIInstrumentor(
                include_content=True,
                include_binary_content=True,
            )
        ],
    )

    try:
        agent = Agent(
            model=f"openai:{respan_model}",
            system_prompt="You are a helpful assistant.",
        )
        result = agent.run_sync("What is the capital of France?")
        print("Agent Output:", result.output)
    finally:
        respan.flush()


if __name__ == "__main__":
    main()
