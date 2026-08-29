"""Local Watson Orchestrate ADK tool and agent definitions traced by Respan."""

from pathlib import Path

from _shared import (
    create_respan,
    example_attributes,
    marker_for,
    workflow_name,
)
from ibm_watsonx_orchestrate.agent_builder.agents import Agent
from ibm_watsonx_orchestrate.agent_builder.tools import tool
from respan import workflow

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


@workflow(name=workflow_name(APP_NAME))
def run_local_agent_tool(ticket_id: str) -> dict[str, object]:
    agent = Agent(
        name="respan_watson_orchestrate_local_agent",
        description="Local agent spec for Respan instrumentation examples.",
        instructions="Use lookup_ticket when asked about support tickets.",
        llm="watsonx/meta-llama/llama-3-3-70b-instruct",
        tools=[lookup_ticket],
    )

    success = lookup_ticket(ticket_id=ticket_id)
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
    marker = marker_for(APP_NAME)
    respan = create_respan(APP_NAME, marker)
    try:
        with example_attributes(APP_NAME, marker):
            result = run_local_agent_tool("INC-1001")
    finally:
        respan.shutdown()
    print({"example": APP_NAME, "marker": marker, "result": result}, flush=True)


if __name__ == "__main__":
    main()
