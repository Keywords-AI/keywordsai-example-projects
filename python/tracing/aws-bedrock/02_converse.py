from __future__ import annotations

from respan import propagate_attributes, workflow

from _shared import (
    create_bedrock_client,
    create_respan,
    deactivate_stubber,
    get_model_id,
    maybe_stub_converse,
)


WORKFLOW_NAME = "aws_bedrock_converse"


@workflow(name=WORKFLOW_NAME)
def run_converse() -> str:
    model_id = get_model_id()
    messages = [
        {
            "role": "user",
            "content": [{"text": "Name one practical use for AWS Bedrock."}],
        }
    ]
    client = create_bedrock_client()
    stubber = maybe_stub_converse(client, model_id=model_id, messages=messages)
    try:
        with propagate_attributes(
            trace_group_identifier=WORKFLOW_NAME,
            metadata={"example": "converse"},
        ):
            response = client.converse(
                modelId=model_id,
                messages=messages,
                inferenceConfig={"maxTokens": 96},
            )
        return response["output"]["message"]["content"][0]["text"]
    finally:
        deactivate_stubber(stubber)


if __name__ == "__main__":
    respan = create_respan()
    print(run_converse())
