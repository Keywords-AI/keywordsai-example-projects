"""Workflow/task spans with @workflow and @task decorators."""

from _gateway import (
    build_openai_chat_model,
    finish_respan,
    load_gateway_config,
    make_respan,
)
from pydantic_ai import Agent
from respan import task, workflow

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
    respan = None
    try:
        respan = make_respan("tracing")
        output = travel_planning_workflow("Paris")
        print("Workflow Output:", output)
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    main()
