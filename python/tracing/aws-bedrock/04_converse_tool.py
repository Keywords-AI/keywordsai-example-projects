from __future__ import annotations

from respan import propagate_attributes, workflow

from _shared import (
    create_bedrock_client,
    create_respan,
    deactivate_stubber,
    get_model_id,
    maybe_stub_converse_tool,
    new_run_id,
)


WORKFLOW_NAME = "aws_bedrock_converse_tool"
EXAMPLE_NAME = "04_converse_tool"


@workflow(name=WORKFLOW_NAME)
def run_converse_tool() -> str:
    model_id = get_model_id()
    messages = [
        {
            "role": "user",
            "content": [{"text": "What is the weather in Tokyo?"}],
        }
    ]
    tool_config = {
        "tools": [
            {
                "toolSpec": {
                    "name": "get_weather",
                    "description": "Get the current weather for a city.",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {"city": {"type": "string"}},
                            "required": ["city"],
                        }
                    },
                }
            }
        ]
    }
    client = create_bedrock_client()
    stubber = maybe_stub_converse_tool(
        client,
        model_id=model_id,
        messages=messages,
        tool_config=tool_config,
    )
    try:
        response = client.converse(
            modelId=model_id,
            messages=messages,
            toolConfig=tool_config,
            inferenceConfig={"maxTokens": 96},
        )
        tool_use = response["output"]["message"]["content"][0]["toolUse"]
        return f"{tool_use['name']}({tool_use['input']})"
    finally:
        deactivate_stubber(stubber)


def main() -> str:
    run_id = new_run_id(EXAMPLE_NAME)
    respan = create_respan(example_name=EXAMPLE_NAME, run_id=run_id)
    try:
        with propagate_attributes(
            group_identifier=WORKFLOW_NAME,
            custom_identifier=run_id,
            metadata={"example": "converse_tool", "run_id": run_id},
        ):
            print(run_converse_tool())
    finally:
        respan.shutdown()
    print(f"RESPAN_EXAMPLE_RUN_ID={run_id}")
    return run_id


if __name__ == "__main__":
    main()
