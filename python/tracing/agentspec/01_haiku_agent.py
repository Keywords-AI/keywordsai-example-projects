"""Run a basic AgentSpec assistant with Respan tracing."""

from pyagentspec.adapters.langgraph import AgentSpecLoader
from pyagentspec.agent import Agent
from pyagentspec.llms import OpenAiConfig
from _shared import build_respan, example_scope, latest_message_content


def run_haiku_agent() -> str:
    respan, model = build_respan(
        example_name="haiku-agent",
        workflow_name="agentspec_haiku_agent",
    )
    with example_scope("haiku-agent"):
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


if __name__ == "__main__":
    run_haiku_agent()
