from __future__ import annotations

import json
import os
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

import httpx
import replicate
from dotenv import load_dotenv
from respan import Respan, propagate_attributes
from respan_instrumentation_replicate import ReplicateInstrumentor

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai/api"
DEFAULT_MODEL = "meta/meta-llama-3-8b-instruct"
MOCK_BASE_URL = "https://mock.replicate.local"


def load_root_env() -> None:
    load_dotenv(PROJECT_ROOT / ".env", override=True)


def require_respan_api_key() -> str:
    load_root_env()
    api_key = os.getenv("RESPAN_API_KEY")
    if not api_key:
        raise RuntimeError("RESPAN_API_KEY must be set in the repo root .env file")
    return api_key


def respan_base_url() -> str:
    return os.getenv("RESPAN_BASE_URL", DEFAULT_RESPAN_BASE_URL).rstrip("/")


def model_name() -> str:
    return os.getenv("RESPAN_REPLICATE_MODEL", DEFAULT_MODEL)


def use_mock_replicate() -> bool:
    explicit = os.getenv("RESPAN_REPLICATE_MOCK")
    if explicit is not None:
        return explicit.lower() not in {"0", "false", "no"}
    return not bool(os.getenv("REPLICATE_API_TOKEN"))


def make_respan(example_name: str) -> Respan:
    api_key = require_respan_api_key()
    return Respan(
        api_key=api_key,
        base_url=respan_base_url(),
        app_name="replicate-examples",
        instrumentations=[ReplicateInstrumentor()],
        environment=os.getenv("RESPAN_ENVIRONMENT", "example"),
        metadata={"integration": "replicate", "example": example_name},
    )


def _mock_prediction(prediction_id: str, *, prompt: str, stream: bool = False) -> dict:
    output = ["Mock Replicate response for: ", prompt]
    return {
        "id": prediction_id,
        "model": model_name(),
        "version": "mock-version",
        "status": "succeeded",
        "input": {"prompt": prompt},
        "output": output,
        "logs": "mock prediction completed",
        "error": None,
        "metrics": {"predict_time": 0.01},
        "created_at": "2026-06-14T00:00:00Z",
        "started_at": "2026-06-14T00:00:00Z",
        "completed_at": "2026-06-14T00:00:01Z",
        "urls": {
            key: value
            for key, value in {
                "get": f"{MOCK_BASE_URL}/v1/predictions/{prediction_id}",
                "cancel": f"{MOCK_BASE_URL}/v1/predictions/{prediction_id}/cancel",
                "stream": f"{MOCK_BASE_URL}/stream/{prediction_id}" if stream else None,
            }.items()
            if value is not None
        },
    }


def _mock_response(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    method = request.method.upper()
    if method == "POST" and (
        path == "/v1/predictions" or path.startswith("/v1/models/") and path.endswith("/predictions")
    ):
        body = json.loads(request.content.decode() or "{}")
        prompt = (body.get("input") or {}).get("prompt", "")
        prediction_id = f"mock-{uuid4().hex[:8]}"
        return httpx.Response(
            201,
            json=_mock_prediction(
                prediction_id,
                prompt=prompt,
                stream=bool(body.get("stream")),
            ),
        )
    if method == "GET" and path.startswith("/v1/predictions/"):
        prediction_id = path.rsplit("/", maxsplit=1)[-1]
        return httpx.Response(
            200,
            json=_mock_prediction(prediction_id, prompt="lookup prediction"),
        )
    if method == "GET" and path == "/v1/predictions":
        return httpx.Response(
            200,
            json={
                "next": None,
                "previous": None,
                "results": [
                    _mock_prediction("mock-listed", prompt="listed prediction")
                ],
            },
        )
    if method == "POST" and path.endswith("/cancel"):
        prediction_id = path.split("/")[-2]
        payload = _mock_prediction(prediction_id, prompt="canceled prediction")
        payload["status"] = "canceled"
        return httpx.Response(200, json=payload)
    if method == "GET" and path.startswith("/stream/"):
        content = "id: 1\nevent: output\ndata: streamed \n\nid: 2\nevent: output\ndata: response\n\nid: 3\nevent: done\ndata: \n\n"
        return httpx.Response(
            200,
            content=content.encode(),
            headers={"content-type": "text/event-stream"},
        )
    return httpx.Response(404, json={"detail": f"Unhandled mock path: {method} {path}"})


def make_client() -> replicate.Client:
    load_root_env()
    if use_mock_replicate():
        return replicate.Client(
            api_token="mock-replicate-token",
            base_url=MOCK_BASE_URL,
            transport=httpx.MockTransport(_mock_response),
        )
    return replicate.Client(api_token=os.environ["REPLICATE_API_TOKEN"])


def workflow_name(example_name: str) -> str:
    normalized_name = example_name.replace("-", "_")
    return f"replicate_{normalized_name}"


def make_custom_identifier(example_name: str) -> str:
    return f"replicate-{example_name}-{uuid4().hex[:8]}"


@contextmanager
def example_attributes(example_name: str, custom_identifier: str | None = None):
    custom_identifier = custom_identifier or make_custom_identifier(example_name)
    current_workflow_name = workflow_name(example_name)
    with propagate_attributes(
        custom_identifier=custom_identifier,
        trace_group_identifier=current_workflow_name,
        metadata={
            "example": example_name,
            "run_id": custom_identifier,
            "workflow_name": current_workflow_name,
            "replicate_client_mode": client_mode(),
        },
    ):
        yield custom_identifier


def client_mode() -> str:
    return "mock-replicate" if use_mock_replicate() else "direct-replicate"


def text_from_output(output) -> str:
    if isinstance(output, str):
        return output
    if isinstance(output, list):
        return "".join(str(item) for item in output)
    try:
        return "".join(str(item) for item in output)
    except TypeError:
        return str(output)


def print_result(example_name: str, custom_identifier: str, text: str) -> None:
    print(f"example={example_name}")
    print(f"custom_identifier={custom_identifier}")
    print(f"workflow_name={workflow_name(example_name)}")
    print(f"client_mode={client_mode()}")
    print(text.strip())
