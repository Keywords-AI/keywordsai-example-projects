from __future__ import annotations

from respan import propagate_attributes, workflow

from _shared import (
    create_bedrock_client,
    create_respan,
    deactivate_stubber,
    get_model_id,
    maybe_stub_converse_stream,
)


WORKFLOW_NAME = "aws_bedrock_converse_stream"


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
        with propagate_attributes(
            trace_group_identifier=WORKFLOW_NAME,
            metadata={"example": "converse_stream"},
        ):
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


if __name__ == "__main__":
    respan = create_respan()
    try:
        print(run_converse_stream())
    finally:
        respan.flush()
