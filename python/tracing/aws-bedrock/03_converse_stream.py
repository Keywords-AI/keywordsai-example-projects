from __future__ import annotations

from respan import propagate_attributes, workflow

from _shared import (
    create_bedrock_client,
    create_respan,
    deactivate_stubber,
    get_model_id,
    maybe_stub_converse_stream,
    new_run_id,
)


WORKFLOW_NAME = "aws_bedrock_converse_stream"
EXAMPLE_NAME = "03_converse_stream"


@workflow(name=WORKFLOW_NAME)
def run_converse_stream() -> str:
    model_id = get_model_id()
    messages = [
        {
            "role": "user",
            "content": [{"text": "Stream a short Bedrock greeting."}],
        }
    ]
    client = create_bedrock_client()
    stubber = maybe_stub_converse_stream(client, model_id=model_id, messages=messages)
    try:
        response = client.converse_stream(
            modelId=model_id,
            messages=messages,
            inferenceConfig={"maxTokens": 96},
        )

        parts: list[str] = []
        for event in response["stream"]:
            delta = event.get("contentBlockDelta", {}).get("delta", {})
            text = delta.get("text")
            if text:
                parts.append(text)
        return "".join(parts)
    finally:
        deactivate_stubber(stubber)


def main() -> str:
    run_id = new_run_id(EXAMPLE_NAME)
    respan = create_respan(example_name=EXAMPLE_NAME, run_id=run_id)
    try:
        with propagate_attributes(
            group_identifier=WORKFLOW_NAME,
            custom_identifier=run_id,
            metadata={"example": "converse_stream", "run_id": run_id},
        ):
            print(run_converse_stream())
    finally:
        respan.shutdown()
    print(f"RESPAN_EXAMPLE_RUN_ID={run_id}")
    return run_id


if __name__ == "__main__":
    main()
