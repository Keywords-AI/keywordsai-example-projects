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
    new_run_id,
)


WORKFLOW_NAME = "aws_bedrock_invoke_model"
EXAMPLE_NAME = "01_invoke_model"


@workflow(name=WORKFLOW_NAME)
def run_invoke_model() -> str:
    model_id = get_model_id()
    body = anthropic_messages_body("Say hello from AWS Bedrock in one short sentence.")
    client = create_bedrock_client()
    stubber = maybe_stub_invoke_model(client, model_id=model_id, body=body)
    try:
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


def main() -> str:
    run_id = new_run_id(EXAMPLE_NAME)
    respan = create_respan(example_name=EXAMPLE_NAME, run_id=run_id)
    try:
        with propagate_attributes(
            group_identifier=WORKFLOW_NAME,
            custom_identifier=run_id,
            metadata={"example": "invoke_model", "run_id": run_id},
        ):
            print(run_invoke_model())
    finally:
        respan.shutdown()
    print(f"RESPAN_EXAMPLE_RUN_ID={run_id}")
    return run_id


if __name__ == "__main__":
    main()
