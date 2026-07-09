"""Local Watson Orchestrate ADK tool and agent definitions traced by Respan."""

from pathlib import Path

from ibm_watsonx_orchestrate.agent_builder.agents import Agent
from ibm_watsonx_orchestrate.agent_builder.tools import tool
from respan import workflow

from _shared import create_respan

SCRIPT_NAME = Path(__file__).name
APP_NAME = SCRIPT_NAME.removesuffix(".py")


@tool(name="lookup_ticket", description="Return a deterministic support ticket.")
def lookup_ticket(ticket_id: str) -> dict[str, str]:
    """Return a fake ticket payload for local tracing."""
    return {"ticket_id": ticket_id, "status": "open", "priority": "high"}


@tool(name="always_fails", description="Raise a deterministic tool failure.")
def always_fails(reason: str) -> str:
    """Raise a predictable exception for instrumentation failure spans."""
    raise RuntimeError(f"deterministic failure: {reason}")


@workflow(name=SCRIPT_NAME)
def run_local_agent_tool() -> dict[str, object]:
    agent = Agent(
        name="respan_watson_orchestrate_local_agent",
        description="Local agent spec for Respan instrumentation examples.",
        instructions="Use lookup_ticket when asked about support tickets.",
        llm="watsonx/meta-llama/llama-3-3-70b-instruct",
        tools=[lookup_ticket],
    )

    success = lookup_ticket(ticket_id="INC-1001")
    failure = None
    try:
        always_fails(reason="example coverage")
    except RuntimeError as exc:
        failure = str(exc)

    result = {
        "agent": agent.name,
        "tools": agent.tools,
        "success": success.content,
        "failure": failure,
    }
    print(result)
    return result


def main() -> None:
    respan = create_respan(APP_NAME)
    try:
        run_local_agent_tool()
    finally:
        respan.shutdown()


if __name__ == "__main__":
    main()
