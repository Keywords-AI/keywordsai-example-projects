from __future__ import annotations

import io
import json
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from uuid import uuid4

import boto3
from botocore.response import StreamingBody
from botocore.stub import Stubber
from dotenv import load_dotenv
from respan import Respan, propagate_attributes
from respan_instrumentation_sagemaker import SageMakerInstrumentor

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai/api"
DEFAULT_REGION = "us-east-1"
DEFAULT_MODEL = "gpt-4o-mini"
STUB_ENDPOINT_NAME = "respan-sagemaker-stub-endpoint"


def load_root_env() -> None:
    load_dotenv(PROJECT_ROOT / ".env", override=False)


def example_run_id() -> str:
    load_root_env()
    return os.getenv("RESPAN_EXAMPLE_RUN_ID") or f"sagemaker-local-{uuid4().hex[:12]}"


def respan_api_key() -> str | None:
    load_root_env()
    return os.getenv("RESPAN_API_KEY") or os.getenv("RESPAN_GATEWAY_API_KEY")


def respan_base_url() -> str:
    load_root_env()
    return (
        os.getenv("RESPAN_BASE_URL")
        or os.getenv("RESPAN_GATEWAY_BASE_URL")
        or DEFAULT_RESPAN_BASE_URL
    ).rstrip("/")


def make_respan(example_name: str) -> Respan:
    run_id = example_run_id()
    return Respan(
        api_key=respan_api_key(),
        base_url=respan_base_url(),
        app_name="sagemaker-examples",
        instrumentations=[SageMakerInstrumentor()],
        environment=os.getenv("RESPAN_ENVIRONMENT", "example"),
        metadata={
            "integration": "sagemaker",
            "example_set": "sagemaker",
            "example": example_name,
            "run_id": run_id,
            "example_run_id": run_id,
        },
        is_batching_enabled=False,
        log_level=os.getenv("RESPAN_LOG_LEVEL", "WARNING"),
    )


def sagemaker_mode() -> str:
    load_root_env()
    mode = os.getenv("SAGEMAKER_EXAMPLE_MODE", "auto").lower()
    if mode in {"live", "stub"}:
        return mode
    return "live" if os.getenv("SAGEMAKER_ENDPOINT_NAME") else "stub"


def use_live_sagemaker() -> bool:
    return sagemaker_mode() == "live"


def endpoint_name() -> str:
    load_root_env()
    endpoint = os.getenv("SAGEMAKER_ENDPOINT_NAME")
    if use_live_sagemaker():
        if not endpoint:
            raise RuntimeError(
                "SAGEMAKER_ENDPOINT_NAME is required when SAGEMAKER_EXAMPLE_MODE=live."
            )
        return endpoint
    return endpoint or STUB_ENDPOINT_NAME


def aws_region() -> str:
    load_root_env()
    return (
        os.getenv("AWS_REGION")
        or os.getenv("AWS_DEFAULT_REGION")
        or os.getenv("SAGEMAKER_REGION")
        or DEFAULT_REGION
    )


def model_name() -> str:
    load_root_env()
    return os.getenv("SAGEMAKER_MODEL_ID") or os.getenv("RESPAN_MODEL") or DEFAULT_MODEL


def custom_attributes() -> str:
    return f"respan_model={model_name()}"


def make_client():
    kwargs: dict[str, Any] = {"region_name": aws_region()}
    if not use_live_sagemaker():
        kwargs.update(
            aws_access_key_id="stub",
            aws_secret_access_key="stub",
            aws_session_token="stub",
        )
    return boto3.client("sagemaker-runtime", **kwargs)


def workflow_name(example_name: str) -> str:
    normalized_name = example_name.replace("-", "_")
    return f"sagemaker_{normalized_name}"


def make_custom_identifier(example_name: str) -> str:
    return f"sagemaker-{example_name}-{uuid4().hex[:8]}"


@contextmanager
def example_attributes(example_name: str, custom_identifier: str | None = None):
    custom_identifier = custom_identifier or make_custom_identifier(example_name)
    current_workflow_name = workflow_name(example_name)
    run_id = example_run_id()
    with propagate_attributes(
        custom_identifier=custom_identifier,
        trace_group_identifier=current_workflow_name,
        metadata={
            "example": example_name,
            "example_set": "sagemaker",
            "run_id": run_id,
            "example_run_id": run_id,
            "execution_id": custom_identifier,
            "workflow_name": current_workflow_name,
            "sagemaker_mode": sagemaker_mode(),
        },
    ):
        yield custom_identifier


def json_bytes(payload: Any) -> bytes:
    return json.dumps(payload).encode("utf-8")


def streaming_body(payload: Any) -> StreamingBody:
    data = json_bytes(payload)
    return StreamingBody(io.BytesIO(data), len(data))


@contextmanager
def stubbed_response(
    client: Any,
    method_name: str,
    response: dict[str, Any],
    expected_params: dict[str, Any],
):
    if use_live_sagemaker():
        yield
        return

    stubber = Stubber(client)
    stubber.add_response(method_name, response, expected_params)
    with stubber:
        yield


def read_json_body(response: dict[str, Any]) -> Any:
    body = response["Body"].read()
    if isinstance(body, str):
        body = body.encode("utf-8")
    return json.loads(body.decode("utf-8"))


def collect_stream_text(response: dict[str, Any]) -> str:
    parts: list[str] = []
    for event in response["Body"]:
        payload_part = event.get("PayloadPart") if isinstance(event, dict) else None
        payload_bytes = (
            payload_part.get("Bytes") if isinstance(payload_part, dict) else None
        )
        if payload_bytes is None:
            continue
        payload = json.loads(payload_bytes.decode("utf-8"))
        token = payload.get("token") if isinstance(payload, dict) else None
        if isinstance(token, dict) and isinstance(token.get("text"), str):
            parts.append(token["text"])
        elif isinstance(payload, dict) and isinstance(
            payload.get("generated_text"), str
        ):
            parts.append(payload["generated_text"])
    return "".join(parts)


def print_run_header(example_name: str, custom_identifier: str) -> None:
    print(f"example_run_id={example_run_id()}", flush=True)
    print(f"custom_identifier={custom_identifier}", flush=True)
    print(f"workflow_name={workflow_name(example_name)}", flush=True)
    print(f"sagemaker_mode={sagemaker_mode()}", flush=True)
    print(f"model={model_name()}", flush=True)


def print_result(example_name: str, custom_identifier: str, result: Any) -> None:
    print(f"example={example_name}")
    print(f"custom_identifier={custom_identifier}")
    print(f"workflow_name={workflow_name(example_name)}")
    print(f"sagemaker_mode={sagemaker_mode()}")
    print(f"model={model_name()}")
    print(json.dumps(result, indent=2, sort_keys=True))
