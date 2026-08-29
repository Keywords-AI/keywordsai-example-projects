"""Run AgentSpec with Respan customer and thread attributes."""

from pyagentspec.adapters.langgraph import AgentSpecLoader
from pyagentspec.agent import Agent
from pyagentspec.llms import OpenAiConfig
from _shared import build_respan, example_scope, latest_message_content


def run_propagated_attributes() -> str:
    respan, model = build_respan(
        example_name="propagated-attributes",
        workflow_name="agentspec_propagated_attributes",
        use_static_identity=False,
    )
    with example_scope(
        "propagated-attributes",
        customer_identifier="agentspec-example-user",
        thread_identifier="agentspec-example-thread",
        metadata={"scenario": "propagated_attributes"},
    ):
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

        try:
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


if __name__ == "__main__":
    run_propagated_attributes()
