"""Run a basic AgentSpec assistant with Respan tracing."""

from pyagentspec.adapters.langgraph import AgentSpecLoader
from pyagentspec.agent import Agent
from pyagentspec.llms import OpenAiConfig
from respan import Respan
from respan_instrumentation_agentspec import AgentSpecInstrumentor

from _shared import configure_gateway, latest_message_content


def run_haiku_agent() -> str:
    respan_api_key, respan_base_url, model = configure_gateway()
    respan = Respan(
        api_key=respan_api_key,
        base_url=respan_base_url,
        app_name="agentspec-haiku-agent",
        instrumentations=[
            AgentSpecInstrumentor(workflow_name="agentspec_haiku_agent")
        ],
    )

    try:
        agent = Agent(
            name="haiku_assistant",
            description="A concise assistant that writes haikus.",
            llm_config=OpenAiConfig(
                name="respan-gateway",
                model_id=model,
            ),
            system_prompt="You are a helpful assistant. Respond only with a haiku.",
        )

        langgraph_agent = AgentSpecLoader().load_component(agent)
        result = langgraph_agent.invoke(
            input={
                "messages": [
                    {
                        "role": "user",
                        "content": "Write a haiku about reliable traces.",
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
    run_haiku_agent()
