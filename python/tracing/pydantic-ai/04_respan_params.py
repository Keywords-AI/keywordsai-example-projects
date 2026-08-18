"""Setting customer_identifier, metadata, and custom_tags on spans."""

from _gateway import (
    build_openai_chat_model,
    finish_respan,
    load_gateway_config,
    make_respan,
)
from pydantic_ai import Agent
from respan import get_client, task

config = load_gateway_config()


def build_agent() -> Agent:
    return Agent(build_openai_chat_model(config))


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
    respan = None
    try:
        respan = make_respan("params")
        output = customer_query("Hello, who are you?")
        print("Output:", output)
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    main()
