"""Bare-minimum Agno agent run with Respan tracing."""

from respan import workflow

from _shared import build_agent, create_respan, print_result


@workflow(name="agno_01_hello_world")
def run_hello_world() -> str:
    agent = build_agent(
        name="Hello Agent",
        instructions="Answer in one concise sentence.",
    )
    result = agent.run("What is Agno?")
    return str(result.content)


def hello_world() -> None:
    respan, _ = create_respan(app_name="agno-01-hello-world")
    output = run_hello_world()
    print_result("Agent output", output)
    respan.flush()


if __name__ == "__main__":
    hello_world()
