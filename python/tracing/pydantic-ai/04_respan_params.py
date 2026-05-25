"""Setting customer_identifier, metadata, and custom_tags on spans."""

import os

from dotenv import find_dotenv, load_dotenv
from pydantic_ai import Agent
from respan import Respan, get_client, task
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
    return Agent(f"openai:{respan_model}")


@task(name="customer_query")
def customer_query(query: str) -> str:
    client = get_client()
    if client:
        client.update_current_span(
            respan_params={
                "customer_identifier": "user_12345",
                "metadata": {
                    "plan": "premium",
                    "session_id": "abc-987",
                },
                "custom_tags": ["pydantic-ai", "test-run"],
            }
        )

    agent = build_agent()
    result = agent.run_sync(query)
    return result.output


def main() -> None:
    respan = Respan(
        app_name="pydantic-ai-params",
        api_key=respan_api_key,
        base_url=respan_base_url,
        instrumentations=[PydanticAIInstrumentor()],
    )

    try:
        output = customer_query("Hello, who are you?")
        print("Output:", output)
    finally:
        respan.flush()


if __name__ == "__main__":
    main()
