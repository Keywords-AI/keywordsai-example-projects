from __future__ import annotations

from botocore.exceptions import ClientError
from respan import propagate_attributes, workflow

from _shared import (
    create_bedrock_client,
    create_respan,
    deactivate_stubber,
    get_model_id,
    maybe_stub_converse_error,
    new_run_id,
)


WORKFLOW_NAME = "aws_bedrock_converse_error"
EXAMPLE_NAME = "05_converse_error"


@workflow(name=WORKFLOW_NAME)
def run_converse_error() -> str:
    model_id = get_model_id()
    messages = [
        {
            "role": "user",
            "content": [{"text": "Trigger the deterministic missing-model route."}],
        }
    ]
    client = create_bedrock_client()
    stubber = maybe_stub_converse_error(
        client,
        model_id=model_id,
        messages=messages,
    )
    try:
        client.converse(modelId=model_id, messages=messages)
    except ClientError as error:
        status_code = error.response["ResponseMetadata"]["HTTPStatusCode"]
        return f"expected Bedrock error {status_code}"
    finally:
        deactivate_stubber(stubber)
    raise AssertionError("the deterministic Bedrock error route unexpectedly succeeded")


def main() -> str:
    run_id = new_run_id(EXAMPLE_NAME)
    respan = create_respan(example_name=EXAMPLE_NAME, run_id=run_id)
    try:
        with propagate_attributes(
            group_identifier=WORKFLOW_NAME,
            custom_identifier=run_id,
            metadata={"example": "converse_error", "run_id": run_id},
        ):
            print(run_converse_error())
    finally:
        respan.shutdown()
    print(f"RESPAN_EXAMPLE_RUN_ID={run_id}")
    return run_id


if __name__ == "__main__":
    main()
