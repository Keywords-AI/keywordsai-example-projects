"""Workflow/task spans with @workflow and @task decorators."""

import os

from dotenv import find_dotenv, load_dotenv
from pydantic_ai import Agent
from respan import Respan, task, workflow
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
    return Agent(
        f"openai:{respan_model}",
        system_prompt="You are a helpful travel assistant.",
    )


@task(name="fetch_destination_info")
def fetch_destination_info(destination: str) -> str:
    agent = build_agent()
    result = agent.run_sync(f"Give me a one-sentence summary of {destination}.")
    return result.output


@workflow(name="travel_planning_workflow")
def travel_planning_workflow(destination: str) -> str:
    return fetch_destination_info(destination)


def main() -> None:
    respan = Respan(
        app_name="pydantic-ai-tracing",
        api_key=respan_api_key,
        base_url=respan_base_url,
        instrumentations=[PydanticAIInstrumentor()],
    )

    try:
        output = travel_planning_workflow("Paris")
        print("Workflow Output:", output)
    finally:
        respan.flush()


if __name__ == "__main__":
    main()
