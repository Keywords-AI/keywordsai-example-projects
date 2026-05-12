"""Route Agno model calls through the Respan gateway."""

from respan import workflow

from _shared import build_agent, create_respan, print_result


@workflow(name="agno_02_gateway")
def run_gateway() -> str:
    agent = build_agent(
        name="Gateway Agent",
        instructions="Keep the answer short and concrete.",
    )
    result = agent.run("Name two practical uses for distributed tracing.")
    return str(result.content)


def gateway() -> None:
    respan, settings = create_respan(app_name="agno-02-gateway")
    output = run_gateway()
    print_result("Model", settings.model)
    print_result("Agent output", output)
    respan.flush()


if __name__ == "__main__":
    gateway()
