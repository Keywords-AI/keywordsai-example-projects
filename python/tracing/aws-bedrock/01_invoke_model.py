from __future__ import annotations

import json

from respan import propagate_attributes, workflow

from _shared import (
    anthropic_messages_body,
    create_bedrock_client,
    create_respan,
    deactivate_stubber,
    get_model_id,
    maybe_stub_invoke_model,
)


WORKFLOW_NAME = "aws_bedrock_invoke_model"


@workflow(name=WORKFLOW_NAME)
def run_invoke_model() -> str:
    model_id = get_model_id()
    body = anthropic_messages_body("Say hello from AWS Bedrock in one short sentence.")
    client = create_bedrock_client()
    stubber = maybe_stub_invoke_model(client, model_id=model_id, body=body)
    try:
        with propagate_attributes(
            trace_group_identifier=WORKFLOW_NAME,
            metadata={"example": "invoke_model"},
        ):
            response = client.invoke_model(
                modelId=model_id,
                body=body,
                contentType="application/json",
                accept="application/json",
            )
        payload = json.loads(response["body"].read())
        return payload["content"][0]["text"]
    finally:
        deactivate_stubber(stubber)


if __name__ == "__main__":
    respan = create_respan()
    print(run_invoke_model())
