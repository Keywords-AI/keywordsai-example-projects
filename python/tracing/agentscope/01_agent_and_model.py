"""Direct AgentScope model and agent invocation traced by Respan."""

from __future__ import annotations

import asyncio

from agentscope.agent import Agent
from agentscope.message import UserMsg

from _shared import build_respan, text_response, ScriptedChatModel


async def main() -> None:
    model = ScriptedChatModel(
        model="agentscope-scripted-chat",
        responses=[
            text_response("Direct model call: tracing is active."),
            text_response("Agent reply: the plan is ready."),
        ],
    )
    respan = build_respan(
        example_name="agent-and-model",
        workflow_name="agentscope_agent_and_model",
        models=[model],
    )

    try:
        direct_response = await model([UserMsg(name="user", content="Ping the model.")])
        print(direct_response.content[0].text)

        agent = Agent(
            name="PlanningAgent",
            system_prompt="Return concise planning updates.",
            model=model,
        )
        result = await agent.reply(UserMsg(name="user", content="Draft a tiny plan."))
        print(result.get_text_content())
    finally:
        respan.flush()
        respan.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
