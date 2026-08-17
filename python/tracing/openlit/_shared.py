"""Shared deterministic and optional-live setup for OpenLIT examples."""

from __future__ import annotations

import json
import os
import sys
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.metadata import distribution
from pathlib import Path
from typing import Any, NamedTuple
from urllib.parse import unquote, urlparse

from dotenv import load_dotenv

EXAMPLE_DIR = Path(__file__).resolve().parent
EXAMPLE_REPO_ROOT = EXAMPLE_DIR.parents[2]
WORKSPACE_ROOT = EXAMPLE_REPO_ROOT.parent
RESPAN_REPO_ROOT = WORKSPACE_ROOT / "respan"
LOCAL_PACKAGE_ROOT = (
    RESPAN_REPO_ROOT
    / "python-sdks"
    / "instrumentations"
    / "respan-instrumentation-openlit"
)
DEFAULT_MODEL = "gpt-4.1-mini"


def _add_local_paths() -> None:
    paths = (
        RESPAN_REPO_ROOT / "python-sdks" / "respan" / "src",
        RESPAN_REPO_ROOT / "python-sdks" / "respan-tracing" / "src",
        RESPAN_REPO_ROOT / "python-sdks" / "respan-sdk" / "src",
        LOCAL_PACKAGE_ROOT / "src",
    )
    for path in reversed(paths):
        path_text = str(path)
        if path.exists() and path_text not in sys.path:
            sys.path.insert(0, path_text)


def _load_env_file(path: Path) -> None:
    load_dotenv(path, override=False)


_load_env_file(EXAMPLE_REPO_ROOT / ".env")
_add_local_paths()

from openai import AsyncOpenAI, OpenAI
from respan import Respan
from respan_instrumentation_openlit import OpenLITInstrumentor


class ProviderConfig(NamedTuple):
    api_key: str
    base_url: str | None
    model: str
    embedding_model: str
    live: bool


def require_run_id() -> str:
    run_id = os.getenv("RESPAN_EXAMPLE_RUN_ID")
    if not run_id or run_id != run_id.strip() or any(char in run_id for char in "\r\n"):
        raise RuntimeError(
            "Set RESPAN_EXAMPLE_RUN_ID in the shell to the exact audit marker."
        )
    if len(run_id.encode("utf-8")) > 160:
        raise RuntimeError("RESPAN_EXAMPLE_RUN_ID must be at most 160 UTF-8 bytes.")
    return run_id


def assert_local_package_link() -> None:
    direct_url_text = distribution("respan-instrumentation-openlit").read_text(
        "direct_url.json"
    )
    if not direct_url_text:
        raise RuntimeError(
            "Install respan-instrumentation-openlit from the local Respan checkout."
        )
    direct_url = json.loads(direct_url_text).get("url", "")
    linked_path = Path(unquote(urlparse(direct_url).path)).resolve()
    if linked_path != LOCAL_PACKAGE_ROOT.resolve():
        raise RuntimeError(
            "respan-instrumentation-openlit is not linked to the local Respan package."
        )


def example_metadata(scenario: str) -> dict[str, str]:
    run_id = require_run_id()
    return {
        "example_set": "python/tracing/openlit",
        "scenario": scenario,
        "run_id": run_id,
        "example_run_id": run_id,
    }


def create_respan(scenario: str, *, capture_content: bool = True) -> Respan:
    assert_local_package_link()
    api_key = os.getenv("RESPAN_API_KEY") or os.getenv("RESPAN_GATEWAY_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Set RESPAN_API_KEY in respan-example-projects/.env for trace export."
        )
    return Respan(
        api_key=api_key,
        base_url=os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api"),
        app_name="openlit-python-examples",
        metadata=example_metadata(scenario),
        instrumentations=[
            OpenLITInstrumentor(
                capture_content=capture_content,
                max_content_length=4_096,
            )
        ],
        is_batching_enabled=False,
        log_level=os.getenv("RESPAN_LOG_LEVEL", "WARNING"),
    )


@contextmanager
def example_scope(scenario: str) -> Iterator[None]:
    run_id = require_run_id()
    with Respan.propagate_attributes(
        trace_group_identifier=f"openlit:{run_id}",
        custom_identifier=f"{run_id}:{scenario}",
        metadata=example_metadata(scenario),
    ):
        yield


def finish_respan(respan: Respan) -> None:
    try:
        respan.flush()
    finally:
        respan.shutdown()


def _chat_payload(request: dict[str, Any]) -> dict[str, Any]:
    model = str(request.get("model") or DEFAULT_MODEL)
    messages = request.get("messages") or []
    if request.get("tools") and request.get("tool_choice"):
        message: dict[str, Any] = {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "call_openlit_weather",
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "arguments": json.dumps({"city": "Tokyo"}),
                    },
                }
            ],
        }
        finish_reason = "tool_calls"
    elif any(
        isinstance(message, dict) and message.get("role") == "tool"
        for message in messages
    ):
        message = {"role": "assistant", "content": "Tokyo is sunny and 22 C."}
        finish_reason = "stop"
    else:
        message = {"role": "assistant", "content": "OpenLIT deterministic reply."}
        finish_reason = "stop"
    return {
        "id": f"chatcmpl-openlit-{time.time_ns()}",
        "object": "chat.completion",
        "created": 1_700_000_000,
        "model": model,
        "choices": [{"index": 0, "message": message, "finish_reason": finish_reason}],
        "usage": {
            "prompt_tokens": 12,
            "completion_tokens": 7,
            "total_tokens": 19,
        },
    }


def _response_payload(prompt: str, *, status: str = "completed") -> dict[str, Any]:
    text = "OpenLIT Responses deterministic reply."
    return {
        "id": f"resp-openlit-{time.time_ns()}",
        "object": "response",
        "created_at": 1_700_000_000.0,
        "model": DEFAULT_MODEL,
        "output": (
            [
                {
                    "id": "msg_openlit_response",
                    "type": "message",
                    "status": "completed",
                    "role": "assistant",
                    "content": [
                        {"type": "output_text", "text": text, "annotations": []}
                    ],
                }
            ]
            if status == "completed"
            else []
        ),
        "parallel_tool_calls": True,
        "tool_choice": "auto",
        "tools": [],
        "status": status,
        "usage": {
            "input_tokens": 6,
            "input_tokens_details": {
                "cached_tokens": 0,
                "cache_write_tokens": 0,
            },
            "output_tokens": 4,
            "output_tokens_details": {"reasoning_tokens": 0},
            "total_tokens": 10,
        },
        "metadata": {"bounded_prompt_length": str(len(prompt))},
    }


class _MockHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, format: str, *args: Any) -> None:
        del format, args

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("content-length", "0") or "0")
        return json.loads(self.rfile.read(length)) if length else {}

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_sse(self, events: list[dict[str, Any]], *, named: bool = False) -> None:
        body = ""
        for event in events:
            if named:
                body += f"event: {event['type']}\n"
            body += f"data: {json.dumps(event)}\n\n"
        body += "data: [DONE]\n\n"
        encoded = body.encode("utf-8")
        self.send_response(200)
        self.send_header("content-type", "text/event-stream")
        self.send_header("content-length", str(len(encoded)))
        self.end_headers()
        try:
            self.wfile.write(encoded)
        except BrokenPipeError:
            pass

    def do_POST(self) -> None:
        request = self._read_json()
        if self.path.endswith("/embeddings"):
            self._send_json(
                200,
                {
                    "object": "list",
                    "model": str(request.get("model") or "text-embedding-3-small"),
                    "data": [
                        {
                            "object": "embedding",
                            "index": 0,
                            "embedding": [0.1, 0.2, 0.3],
                        }
                    ],
                    "usage": {"prompt_tokens": 4, "total_tokens": 4},
                },
            )
            return
        if self.path.endswith("/responses"):
            prompt = str(request.get("input") or "")
            if request.get("stream"):
                completed = _response_payload(prompt)
                events = [
                    {
                        "type": "response.created",
                        "sequence_number": 0,
                        "response": {
                            **_response_payload(prompt, status="in_progress"),
                            "usage": None,
                        },
                    },
                    {
                        "type": "response.output_text.delta",
                        "sequence_number": 1,
                        "item_id": "msg_openlit_response",
                        "output_index": 0,
                        "content_index": 0,
                        "delta": "OpenLIT Responses deterministic reply.",
                        "logprobs": [],
                    },
                    {
                        "type": "response.completed",
                        "sequence_number": 2,
                        "response": completed,
                    },
                ]
                self._send_sse(events, named=True)
            else:
                self._send_json(200, _response_payload(prompt))
            return
        if not self.path.endswith("/chat/completions"):
            self._send_json(404, {"error": {"message": "not found"}})
            return
        messages = request.get("messages") or []
        prompt = str(messages[0].get("content") if messages else "")
        if prompt == "expected-rate-limit":
            self._send_json(
                429,
                {
                    "error": {
                        "message": "deterministic rate limit",
                        "type": "rate_limit_error",
                    }
                },
            )
            return
        if request.get("stream"):
            chunks = [
                {
                    "id": "chatcmpl-openlit-stream",
                    "object": "chat.completion.chunk",
                    "created": 1_700_000_000,
                    "model": str(request.get("model") or DEFAULT_MODEL),
                    "choices": [
                        {
                            "index": 0,
                            "delta": {"role": "assistant", "content": "OpenLIT "},
                            "finish_reason": None,
                        }
                    ],
                },
                {
                    "id": "chatcmpl-openlit-stream",
                    "object": "chat.completion.chunk",
                    "created": 1_700_000_000,
                    "model": str(request.get("model") or DEFAULT_MODEL),
                    "choices": [
                        {
                            "index": 0,
                            "delta": {"content": "stream reply."},
                            "finish_reason": "stop",
                        }
                    ],
                },
                {
                    "id": "chatcmpl-openlit-stream",
                    "object": "chat.completion.chunk",
                    "created": 1_700_000_000,
                    "model": str(request.get("model") or DEFAULT_MODEL),
                    "choices": [],
                    "usage": {
                        "prompt_tokens": 7,
                        "completion_tokens": 11,
                        "total_tokens": 18,
                    },
                },
            ]
            self._send_sse(chunks)
            return
        self._send_json(200, _chat_payload(request))


@contextmanager
def provider_config(*, force_mock: bool = False) -> Iterator[ProviderConfig]:
    live = not force_mock and os.getenv("RESPAN_OPENLIT_LIVE") == "1"
    if live:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("RESPAN_OPENLIT_LIVE=1 requires OPENAI_API_KEY.")
        yield ProviderConfig(
            api_key=api_key,
            base_url=os.getenv("OPENAI_BASE_URL"),
            model=os.getenv("RESPAN_OPENLIT_MODEL", DEFAULT_MODEL),
            embedding_model=os.getenv(
                "RESPAN_OPENLIT_EMBEDDING_MODEL", "text-embedding-3-small"
            ),
            live=True,
        )
        return

    server = ThreadingHTTPServer(("127.0.0.1", 0), _MockHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield ProviderConfig(
            api_key="local-openlit-key",
            base_url=f"http://127.0.0.1:{server.server_port}/v1",
            model=DEFAULT_MODEL,
            embedding_model="text-embedding-3-small",
            live=False,
        )
    finally:
        try:
            server.shutdown()
        finally:
            try:
                server.server_close()
            finally:
                thread.join(timeout=5)
                if thread.is_alive():
                    raise RuntimeError(
                        "OpenLIT mock server did not stop within 5 seconds."
                    )


def sync_client(config: ProviderConfig) -> OpenAI:
    kwargs: dict[str, Any] = {
        "api_key": config.api_key,
        "max_retries": 0,
        "timeout": 8,
    }
    if config.base_url:
        kwargs["base_url"] = config.base_url
    return OpenAI(**kwargs)


def async_client(config: ProviderConfig) -> AsyncOpenAI:
    kwargs: dict[str, Any] = {
        "api_key": config.api_key,
        "max_retries": 0,
        "timeout": 8,
    }
    if config.base_url:
        kwargs["base_url"] = config.base_url
    return AsyncOpenAI(**kwargs)
