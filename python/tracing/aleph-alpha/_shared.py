from __future__ import annotations

import json
import os
import sys
import threading
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Iterator
from uuid import uuid4

PROJECT_ROOT = Path(__file__).resolve().parents[3]
WORKSPACE_ROOT = PROJECT_ROOT.parent
LOCAL_RESPAN_REPO = WORKSPACE_ROOT / "respan"
for local_path in (
    LOCAL_RESPAN_REPO / "python-sdks/respan-sdk/src",
    LOCAL_RESPAN_REPO / "python-sdks/respan-tracing/src",
    LOCAL_RESPAN_REPO / "python-sdks/respan/src",
    LOCAL_RESPAN_REPO
    / "python-sdks/instrumentations/respan-instrumentation-aleph-alpha/src",
):
    if local_path.exists():
        sys.path.insert(0, str(local_path))

from aleph_alpha_client import AsyncClient, Client
from dotenv import load_dotenv
from respan import Respan, propagate_attributes, workflow
from respan_instrumentation_aleph_alpha import AlephAlphaInstrumentor

DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai/api"
DEFAULT_ALEPH_ALPHA_HOST = "https://api.aleph-alpha.com/"
DEFAULT_MODEL = "pharia-1-chat"


def load_root_env() -> None:
    load_dotenv(PROJECT_ROOT / ".env", override=True)


def require_respan_api_key() -> str:
    load_root_env()
    api_key = os.getenv("RESPAN_API_KEY") or os.getenv("RESPAN_GATEWAY_API_KEY")
    if not api_key:
        raise RuntimeError("RESPAN_API_KEY must be set in the repo root .env file")
    return api_key


def respan_base_url() -> str:
    return os.getenv("RESPAN_BASE_URL", DEFAULT_RESPAN_BASE_URL).rstrip("/")


def model_name() -> str:
    return os.getenv("ALEPH_ALPHA_MODEL", DEFAULT_MODEL)


def workflow_name(example_name: str) -> str:
    return f"aleph_alpha_{example_name.replace('-', '_')}"


def make_custom_identifier(example_name: str) -> str:
    return f"aleph-alpha-{example_name}-{uuid4().hex[:8]}"


def make_respan(example_name: str) -> Respan:
    return Respan(
        api_key=require_respan_api_key(),
        base_url=respan_base_url(),
        app_name="aleph-alpha-examples",
        instrumentations=[AlephAlphaInstrumentor()],
        environment=os.getenv("RESPAN_ENVIRONMENT", "example"),
        metadata={"integration": "aleph-alpha", "example": example_name},
    )


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
        },
    ):
        yield custom_identifier


def _prompt_text(payload: dict[str, Any]) -> str:
    prompt = payload.get("prompt") or payload.get("input") or []
    if isinstance(prompt, list):
        parts = [item.get("data", "") for item in prompt if isinstance(item, dict)]
        return " ".join(part for part in parts if part)
    if isinstance(prompt, str):
        return prompt
    return "mock prompt"


class _MockAlephHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, format: str, *args: Any) -> None:
        return

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0].strip("/")
        if path == "version":
            self._send_text("mock-aleph-alpha")
            return
        if path == "models_available":
            self._send_json([{"name": model_name()}])
            return
        self.send_error(404)

    def do_POST(self) -> None:
        path = self.path.split("?", 1)[0].strip("/")
        body = self._read_json_body()
        if body.get("stream"):
            self._send_sse(self._stream_events(path, body))
            return
        self._send_json(self._response_for(path, body))

    def _read_json_body(self) -> dict[str, Any]:
        length = int(self.headers.get("content-length", "0"))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _send_text(self, text: str) -> None:
        encoded = text.encode("utf-8")
        self.send_response(200)
        self.send_header("content-type", "text/plain")
        self.send_header("content-length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_json(self, payload: Any) -> None:
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_sse(self, events: list[dict[str, Any]]) -> None:
        self.send_response(200)
        self.send_header("content-type", "text/event-stream")
        self.send_header("cache-control", "no-cache")
        self.send_header("connection", "close")
        self.end_headers()
        for event in events:
            self.wfile.write(f"data: {json.dumps(event)}\n\n".encode("utf-8"))
        self.wfile.write(b"data: [DONE]\n\n")
        self.wfile.flush()
        self.close_connection = True

    def _response_for(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        model = body.get("model") or model_name()
        if path == "complete":
            return {
                "model_version": f"{model}-mock",
                "completions": [
                    {
                        "completion": f"Mock completion for: {_prompt_text(body)}",
                        "finish_reason": "stop",
                    }
                ],
                "num_tokens_prompt_total": 9,
                "num_tokens_generated": 7,
            }
        if path == "chat/completions":
            has_tools = bool(body.get("tools"))
            message: dict[str, Any] = {
                "role": "assistant",
                "content": "Mock Aleph Alpha chat response.",
            }
            finish_reason = "stop"
            if has_tools:
                finish_reason = "tool_calls"
                message["tool_calls"] = [
                    {
                        "id": "call_mock_lookup",
                        "type": "function",
                        "function": {
                            "name": "lookup_policy",
                            "arguments": "{\"topic\":\"observability\"}",
                        },
                    }
                ]
            return {"choices": [{"finish_reason": finish_reason, "message": message}]}
        if path == "embed":
            return {
                "model_version": f"{model}-mock",
                "embeddings": {"-1": {"mean": [0.1, 0.2, 0.3]}},
                "tokens": ["mock", "embedding"],
                "num_tokens_prompt_total": 5,
            }
        if path == "embeddings":
            items = body.get("input")
            count = len(items) if isinstance(items, list) and items and isinstance(items[0], str) else 1
            return {
                "object": "list",
                "data": [
                    {"object": "embedding", "embedding": [0.1, 0.2, 0.3], "index": index}
                    for index in range(count)
                ],
                "model": model,
                "usage": {"prompt_tokens": 6, "total_tokens": 6},
            }
        if path in {"semantic_embed", "instructable_embed"}:
            return {
                "model_version": f"{model}-mock",
                "embedding": [0.4, 0.5, 0.6],
                "num_tokens_prompt_total": 6,
            }
        if path == "batch_semantic_embed":
            prompts = body.get("prompts") or []
            return {
                "model_version": f"{model}-mock",
                "embeddings": [[0.7, 0.8, 0.9] for _ in prompts],
                "num_tokens_prompt_total": max(1, len(prompts)) * 4,
            }
        if path == "evaluate":
            return {
                "model_version": f"{model}-mock",
                "message": None,
                "result": {"log_probability": -1.25},
                "num_tokens_prompt_total": 8,
            }
        if path == "explain":
            return {
                "model_version": f"{model}-mock",
                "explanations": [
                    {
                        "target": body.get("target", "mock target"),
                        "items": [
                            {
                                "type": "text",
                                "scores": [{"start": 0, "length": 4, "score": 0.72}],
                            },
                            {
                                "type": "target",
                                "scores": [{"start": 0, "length": 4, "score": 0.28}],
                            },
                        ],
                    }
                ],
            }
        return {"ok": True, "model_version": f"{model}-mock"}

    def _stream_events(self, path: str, body: dict[str, Any]) -> list[dict[str, Any]]:
        model = body.get("model") or model_name()
        if path == "complete":
            return [
                {"type": "stream_chunk", "index": 0, "completion": "Mock stream "},
                {"type": "stream_chunk", "index": 0, "completion": "completion."},
                {"type": "stream_summary", "index": 0, "model_version": f"{model}-mock", "finish_reason": "stop"},
                {"type": "completion_summary", "num_tokens_prompt_total": 10, "num_tokens_generated": 4},
            ]
        if path == "chat/completions":
            return [
                {"choices": [{"delta": {"role": "assistant", "content": ""}}]},
                {"choices": [{"delta": {"content": "Mock streaming "}}]},
                {"choices": [{"delta": {"content": "chat."}}]},
                {"usage": {"prompt_tokens": 9, "completion_tokens": 3, "total_tokens": 12}},
                {"choices": [{"finish_reason": "stop"}]},
            ]
        return []


@contextmanager
def mock_aleph_server() -> Iterator[str]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), _MockAlephHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


@contextmanager
def sync_client_context() -> Iterator[tuple[Client, str]]:
    load_root_env()
    api_key = os.getenv("ALEPH_ALPHA_API_KEY")
    if api_key:
        host = os.getenv("ALEPH_ALPHA_HOST", DEFAULT_ALEPH_ALPHA_HOST)
        yield Client(token=api_key, host=host), "direct-aleph-alpha"
        return
    with mock_aleph_server() as host:
        yield Client(token="mock-token", host=host, total_retries=0), "local-mock"


@contextmanager
def async_client_context() -> Iterator[tuple[AsyncClient, str]]:
    load_root_env()
    api_key = os.getenv("ALEPH_ALPHA_API_KEY")
    if api_key:
        host = os.getenv("ALEPH_ALPHA_HOST", DEFAULT_ALEPH_ALPHA_HOST)
        yield AsyncClient(token=api_key, host=host), "direct-aleph-alpha"
        return
    with mock_aleph_server() as host:
        yield AsyncClient(token="mock-token", host=host, total_retries=0), "local-mock"


def print_result(example_name: str, custom_identifier: str, mode: str, text: str) -> None:
    print(f"example={example_name}")
    print(f"custom_identifier={custom_identifier}")
    print(f"workflow_name={workflow_name(example_name)}")
    print(f"client_mode={mode}")
    print(text.strip())
