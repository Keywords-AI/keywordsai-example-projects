"""Workflow/task spans with @workflow and @task decorators."""

from pydantic_ai import Agent
from respan import Respan, task, workflow
from respan_instrumentation_pydantic_ai import PydanticAIInstrumentor

from _gateway import build_openai_chat_model, load_gateway_config

config = load_gateway_config()


def build_agent() -> Agent:
    return Agent(
        build_openai_chat_model(config),
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
        api_key=config.respan_api_key,
        base_url=config.respan_base_url,
        instrumentations=[PydanticAIInstrumentor()],
    )

    try:
        output = travel_planning_workflow("Paris")
        print("Workflow Output:", output)
    finally:
        respan.flush()


if __name__ == "__main__":
    main()
