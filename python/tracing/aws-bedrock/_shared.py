from __future__ import annotations

import io
import json
import os
import uuid
from pathlib import Path
from typing import Any

import boto3
from botocore.response import StreamingBody
from botocore.stub import Stubber
from dotenv import load_dotenv
from respan import Respan
from respan_instrumentation_aws_bedrock import AWSBedrockInstrumentor


EXAMPLE_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXAMPLE_DIR.parents[2]
load_dotenv(REPO_ROOT / ".env")

DEFAULT_MODEL_ID = "us.anthropic.claude-3-5-haiku-20241022-v1:0"
DEFAULT_REGION = "us-east-1"


def get_model_id() -> str:
    return os.getenv("AWS_BEDROCK_MODEL_ID") or os.getenv("BEDROCK_MODEL_ID") or DEFAULT_MODEL_ID


def get_region() -> str:
    return os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or DEFAULT_REGION


def should_use_stubs() -> bool:
    explicit = os.getenv("AWS_BEDROCK_USE_STUBS")
    if explicit is not None:
        return explicit.lower() not in {"0", "false", "no"}
    return not (os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("AWS_PROFILE"))


def new_run_id(example_name: str) -> str:
    return os.getenv("RESPAN_EXAMPLE_RUN_ID") or f"{example_name}-{uuid.uuid4().hex[:10]}"


def create_respan(*, example_name: str, run_id: str) -> Respan:
    return Respan(
        app_name="aws-bedrock-examples",
        instrumentations=[AWSBedrockInstrumentor()],
        metadata={
            "example_set": "aws-bedrock",
            "example_name": example_name,
            "run_id": run_id,
        },
        environment=os.getenv("RESPAN_ENVIRONMENT", "examples"),
    )


def create_bedrock_client():
    kwargs: dict[str, Any] = {"region_name": get_region()}
    if should_use_stubs():
        kwargs.update(
            {
                "aws_access_key_id": "stub-access-key",
                "aws_secret_access_key": "stub-secret-key",
                "aws_session_token": "stub-session-token",
            }
        )
    return boto3.client("bedrock-runtime", **kwargs)


def anthropic_messages_body(prompt: str, *, max_tokens: int = 96) -> str:
    return json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
    )


def _streaming_body(payload: dict[str, Any]) -> StreamingBody:
    body = json.dumps(payload).encode("utf-8")
    return StreamingBody(io.BytesIO(body), len(body))


def maybe_stub_invoke_model(client, *, model_id: str, body: str) -> Stubber | None:
    if not should_use_stubs():
        return None

    stubber = Stubber(client)
    stubber.add_response(
        "invoke_model",
        {
            "body": _streaming_body(
                {
                    "id": "stubbed-bedrock-message",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": "Stubbed Bedrock response for invoke_model.",
                        }
                    ],
                    "usage": {"input_tokens": 8, "output_tokens": 9},
                }
            ),
            "contentType": "application/json",
            "ResponseMetadata": {"HTTPStatusCode": 200},
        },
        {
            "modelId": model_id,
            "body": body,
            "contentType": "application/json",
            "accept": "application/json",
        },
    )
    stubber.activate()
    return stubber


def maybe_stub_converse(client, *, model_id: str, messages: list[dict[str, Any]]) -> Stubber | None:
    if not should_use_stubs():
        return None

    stubber = Stubber(client)
    expected_params = {
        "modelId": model_id,
        "messages": messages,
        "inferenceConfig": {"maxTokens": 96},
    }
    stubber.add_response(
        "converse",
        {
            "output": {
                "message": {
                    "role": "assistant",
                    "content": [{"text": "Stubbed Bedrock response for converse."}],
                }
            },
            "stopReason": "end_turn",
            "usage": {"inputTokens": 10, "outputTokens": 11, "totalTokens": 21},
            "metrics": {"latencyMs": 12},
            "ResponseMetadata": {"HTTPStatusCode": 200},
        },
        expected_params,
    )
    stubber.activate()
    return stubber


def maybe_stub_converse_stream(
    client,
    *,
    model_id: str,
    messages: list[dict[str, Any]],
) -> Stubber | None:
    if not should_use_stubs():
        return None

    stubber = Stubber(client)
    expected_params = {
        "modelId": model_id,
        "messages": messages,
        "inferenceConfig": {"maxTokens": 96},
    }
    stubber.add_response(
        "converse_stream",
        {
            "stream": {
                "contentBlockDelta": {
                    "contentBlockIndex": 0,
                    "delta": {"text": "Stubbed stream."},
                },
                "metadata": {
                    "usage": {
                        "inputTokens": 12,
                        "outputTokens": 13,
                        "totalTokens": 25,
                    },
                    "metrics": {"latencyMs": 7},
                },
            },
            "ResponseMetadata": {"HTTPStatusCode": 200},
        },
        expected_params,
    )
    stubber.activate()
    return stubber


def maybe_stub_converse_tool(
    client,
    *,
    model_id: str,
    messages: list[dict[str, Any]],
    tool_config: dict[str, Any],
) -> Stubber | None:
    if not should_use_stubs():
        return None

    stubber = Stubber(client)
    stubber.add_response(
        "converse",
        {
            "output": {
                "message": {
                    "role": "assistant",
                    "content": [
                        {
                            "toolUse": {
                                "toolUseId": "tooluse-weather-1",
                                "name": "get_weather",
                                "input": {"city": "Tokyo"},
                            }
                        }
                    ],
                }
            },
            "stopReason": "tool_use",
            "usage": {"inputTokens": 14, "outputTokens": 6, "totalTokens": 20},
            "metrics": {"latencyMs": 8},
            "ResponseMetadata": {"HTTPStatusCode": 200},
        },
        {
            "modelId": model_id,
            "messages": messages,
            "toolConfig": tool_config,
            "inferenceConfig": {"maxTokens": 96},
        },
    )
    stubber.activate()
    return stubber


def maybe_stub_converse_error(
    client,
    *,
    model_id: str,
    messages: list[dict[str, Any]],
) -> Stubber | None:
    if not should_use_stubs():
        return None

    stubber = Stubber(client)
    stubber.add_client_error(
        "converse",
        service_error_code="ResourceNotFoundException",
        service_message="The requested model was not found.",
        http_status_code=404,
        expected_params={"modelId": model_id, "messages": messages},
    )
    stubber.activate()
    return stubber


def deactivate_stubber(stubber: Stubber | None) -> None:
    if stubber is not None:
        stubber.deactivate()
