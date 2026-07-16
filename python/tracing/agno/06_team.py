"""Trace an Agno team run."""

from agno.models.openai import OpenAIChat
from agno.team import Team
from respan import workflow

from _shared import build_agent, create_respan, load_gateway_settings, print_result


@workflow(name="agno_06_team")
def run_team() -> str:
    settings = load_gateway_settings()
    researcher = build_agent(
        name="Researcher",
        instructions="Find the most relevant operational facts.",
    )
    writer = build_agent(
        name="Writer",
        instructions="Turn operational facts into concise prose.",
    )
    team_agent = Team(
        name="Tracing Team",
        model=OpenAIChat(id=settings.model),
        members=[researcher, writer],
        instructions="Coordinate a concise final answer.",
    )

    result = team_agent.run("Explain why tool spans are useful in one paragraph.")
    return str(result.content)


def team() -> None:
    respan, _ = create_respan(app_name="agno-06-team")
    output = run_team()
    print_result("Team output", output)


if __name__ == "__main__":
    team()
