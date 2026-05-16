"""Run AgentSpec with Respan customer and thread attributes."""

from pyagentspec.adapters.langgraph import AgentSpecLoader
from pyagentspec.agent import Agent
from pyagentspec.llms import OpenAiConfig
from respan import Respan, propagate_attributes
from respan_instrumentation_agentspec import AgentSpecInstrumentor

from _shared import configure_gateway, latest_message_content


def run_propagated_attributes() -> str:
    respan_api_key, respan_base_url, model = configure_gateway()
    respan = Respan(
        api_key=respan_api_key,
        base_url=respan_base_url,
        app_name="agentspec-propagated-attributes",
        instrumentations=[
            AgentSpecInstrumentor(workflow_name="agentspec_propagated_attributes")
        ],
        metadata={"example": "agentspec"},
        environment="examples",
    )

    try:
        agent = Agent(
            name="support_assistant",
            description="A concise support assistant.",
            llm_config=OpenAiConfig(
                name="respan-gateway",
                model_id=model,
            ),
            system_prompt=(
                "Answer in one short sentence using the phrase "
                "'propagated Respan attributes'."
            ),
        )
        langgraph_agent = AgentSpecLoader().load_component(agent)

        with propagate_attributes(
            customer_identifier="agentspec-example-user",
            thread_identifier="agentspec-example-thread",
            metadata={"scenario": "propagated_attributes"},
        ):
            result = langgraph_agent.invoke(
                input={
                    "messages": [
                        {
                            "role": "user",
                            "content": (
                                "Say that this trace is testing propagated "
                                "Respan attributes."
                            ),
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
    run_propagated_attributes()
