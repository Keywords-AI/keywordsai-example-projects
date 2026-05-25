"""Run an AgentSpec assistant with a server tool and Respan tracing."""

from pyagentspec.adapters.langgraph import AgentSpecLoader
from pyagentspec.agent import Agent
from pyagentspec.llms import OpenAiConfig
from pyagentspec.property import FloatProperty
from pyagentspec.serialization import AgentSpecSerializer
from pyagentspec.tools import ServerTool
from respan import Respan
from respan_instrumentation_agentspec import AgentSpecInstrumentor

from _shared import configure_gateway, latest_message_content


def subtract(left: float, right: float) -> float:
    return left - right


def run_agent_with_tool() -> str:
    respan_api_key, respan_base_url, model = configure_gateway()
    respan = Respan(
        api_key=respan_api_key,
        base_url=respan_base_url,
        app_name="agentspec-tool-agent",
        instrumentations=[
            AgentSpecInstrumentor(workflow_name="agentspec_tool_agent")
        ],
    )

    try:
        subtraction_tool = ServerTool(
            name="subtract",
            description="Subtract right from left.",
            inputs=[FloatProperty(title="left"), FloatProperty(title="right")],
            outputs=[FloatProperty(title="difference")],
        )
        agent = Agent(
            name="calculator_assistant",
            description="A calculator assistant with one subtraction tool.",
            llm_config=OpenAiConfig(
                name="respan-gateway",
                model_id=model,
            ),
            system_prompt=(
                "You are a calculator assistant. Use the subtract tool for "
                "subtraction requests and return the numeric result."
            ),
            tools=[subtraction_tool],
        )
        agent_json = AgentSpecSerializer().to_json(agent)
        langgraph_agent = AgentSpecLoader(tool_registry={"subtract": subtract}).load_json(
            agent_json
        )

        result = langgraph_agent.invoke(
            input={
                "messages": [
                    {
                        "role": "user",
                        "content": "Use the subtract tool to compute 987 - 123.",
                    }
                ]
            }
        )
        output = latest_message_content(result)
        print(output)
        return output
    finally:
        respan.shutdown()
        respan.flush()


if __name__ == "__main__":
    run_agent_with_tool()
