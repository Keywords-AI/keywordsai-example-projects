from __future__ import annotations

import json
import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from uuid import uuid4

import httpx
from dotenv import load_dotenv
from respan import Respan, propagate_attributes
from respan_instrumentation_together import TogetherInstrumentor
from together import AsyncTogether, Together

EXAMPLE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = EXAMPLE_DIR.parents[2]
DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai/api"
DEFAULT_CHAT_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
DEFAULT_EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
DEFAULT_RERANK_MODEL = "Salesforce/Llama-Rank-v1"
DEFAULT_IMAGE_MODEL = "black-forest-labs/FLUX.1-schnell-Free"


def load_root_env() -> None:
    load_dotenv(PROJECT_ROOT / ".env", override=False)


def require_env(*names: str) -> str:
    load_root_env()
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    raise RuntimeError(f"One of {', '.join(names)} must be set")


def respan_api_key() -> str:
    return require_env("RESPAN_API_KEY", "RESPAN_GATEWAY_API_KEY")


def respan_base_url() -> str:
    load_root_env()
    return os.getenv("RESPAN_BASE_URL", DEFAULT_RESPAN_BASE_URL).rstrip("/")


def model_name() -> str:
    return os.getenv("RESPAN_TOGETHER_MODEL", DEFAULT_CHAT_MODEL)


def completion_model_name() -> str:
    return os.getenv("RESPAN_TOGETHER_COMPLETION_MODEL", DEFAULT_CHAT_MODEL)


def embedding_model_name() -> str:
    return os.getenv("RESPAN_TOGETHER_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)


def rerank_model_name() -> str:
    return os.getenv("RESPAN_TOGETHER_RERANK_MODEL", DEFAULT_RERANK_MODEL)


def image_model_name() -> str:
    return os.getenv("RESPAN_TOGETHER_IMAGE_MODEL", DEFAULT_IMAGE_MODEL)


def _request_json(request: httpx.Request) -> dict[str, Any]:
    try:
        value = json.loads(request.content.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _usage(prompt: int, completion: int) -> dict[str, int]:
    return {
        "prompt_tokens": prompt,
        "completion_tokens": completion,
        "total_tokens": prompt + completion,
    }


def _chat_response(payload: dict[str, Any]) -> dict[str, Any]:
    messages = payload.get("messages") or []
    tools = payload.get("tools") or []
    has_tool_result = any(
        isinstance(message, dict) and message.get("role") == "tool"
        for message in messages
    )
    if tools and not has_tool_result:
        message: dict[str, Any] = {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "together-weather-1",
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "arguments": '{"city":"Tokyo"}',
                    },
                }
            ],
        }
        finish_reason = "tool_calls"
        completion = 12
    elif has_tool_result:
        message = {
            "role": "assistant",
            "content": "Tokyo is sunny and 22 C.",
        }
        finish_reason = "stop"
        completion = 8
    else:
        message = {
            "role": "assistant",
            "content": "Together tracing keeps model calls observable.",
        }
        finish_reason = "stop"
        completion = 7
    return {
        "id": "together-chat-deterministic",
        "object": "chat.completion",
        "created": 1_787_000_000,
        "model": payload.get("model") or model_name(),
        "choices": [
            {
                "index": 0,
                "message": message,
                "finish_reason": finish_reason,
            }
        ],
        "usage": _usage(11, completion),
    }


def _stream_response(request: httpx.Request, payload: dict[str, Any]) -> httpx.Response:
    chunks = [
        {
            "id": "together-stream-deterministic",
            "object": "chat.completion.chunk",
            "created": 1_787_000_000,
            "model": payload.get("model") or model_name(),
            "choices": [
                {
                    "index": 0,
                    "delta": {"role": "assistant", "content": "Trace data "},
                    "finish_reason": None,
                }
            ],
        },
        {
            "id": "together-stream-deterministic",
            "object": "chat.completion.chunk",
            "created": 1_787_000_000,
            "model": payload.get("model") or model_name(),
            "choices": [
                {
                    "index": 0,
                    "delta": {"content": "flows clearly."},
                    "finish_reason": "stop",
                }
            ],
            "usage": _usage(9, 4),
        },
    ]
    body = "".join(f"data: {json.dumps(chunk)}\n\n" for chunk in chunks)
    body += "data: [DONE]\n\n"
    return httpx.Response(
        200,
        headers={"content-type": "text/event-stream"},
        text=body,
        request=request,
    )


def _deterministic_response(
    request: httpx.Request, *, error_status: int | None
) -> httpx.Response:
    if error_status is not None:
        return httpx.Response(
            error_status,
            json={"error": {"message": "deterministic provider limit"}},
            request=request,
        )
    payload = _request_json(request)
    path = request.url.path
    if path.endswith("/chat/completions"):
        if payload.get("stream") is True:
            return _stream_response(request, payload)
        body = _chat_response(payload)
    elif path.endswith("/completions"):
        body = {
            "id": "together-text-deterministic",
            "object": "text_completion",
            "created": 1_787_000_000,
            "model": payload.get("model") or completion_model_name(),
            "choices": [
                {
                    "index": 0,
                    "text": "Completion tracing is deterministic.",
                    "finish_reason": "stop",
                }
            ],
            "usage": _usage(6, 5),
        }
    elif path.endswith("/embeddings"):
        body = {
            "object": "list",
            "model": payload.get("model") or embedding_model_name(),
            "data": [
                {"object": "embedding", "index": 0, "embedding": [0.1, 0.2, 0.3]},
                {"object": "embedding", "index": 1, "embedding": [0.4, 0.5, 0.6]},
            ],
            "usage": _usage(4, 0),
        }
    elif path.endswith("/rerank"):
        body = {
            "id": "together-rerank-deterministic",
            "model": payload.get("model") or rerank_model_name(),
            "results": [
                {
                    "index": 1,
                    "relevance_score": 0.98,
                    "document": {"text": "Washington, D.C. is the capital."},
                }
            ],
            "usage": _usage(7, 0),
        }
    elif path.endswith("/images/generations"):
        body = {
            "id": "together-image-deterministic",
            "model": payload.get("model") or image_model_name(),
            "data": [
                {
                    "index": 0,
                    "type": "url",
                    "url": "https://example.invalid/deterministic-image.png",
                }
            ],
        }
    else:
        body = {"error": {"message": f"unhandled deterministic path {path}"}}
        return httpx.Response(404, json=body, request=request)
    return httpx.Response(200, json=body, request=request)


def _live_mode() -> bool:
    return os.getenv("RESPAN_TOGETHER_LIVE") == "1"


def make_client(*, error_status: int | None = None) -> Together:
    load_root_env()
    if _live_mode() and error_status is None:
        api_key = require_env("TOGETHER_API_KEY")
        base_url = os.getenv("TOGETHER_BASE_URL")
        return Together(api_key=api_key, base_url=base_url)
    transport = httpx.MockTransport(
        lambda request: _deterministic_response(request, error_status=error_status)
    )
    return Together(
        api_key="deterministic-together-key",
        base_url="https://together.invalid/v1",
        http_client=httpx.Client(transport=transport),
    )


def make_async_client(*, error_status: int | None = None) -> AsyncTogether:
    transport = httpx.MockTransport(
        lambda request: _deterministic_response(request, error_status=error_status)
    )
    return AsyncTogether(
        api_key="deterministic-together-key",
        base_url="https://together.invalid/v1",
        http_client=httpx.AsyncClient(transport=transport),
    )


def make_respan(example_name: str, marker: str) -> Respan:
    return Respan(
        api_key=respan_api_key(),
        base_url=respan_base_url(),
        app_name="together-examples",
        instrumentations=[TogetherInstrumentor()],
        environment=os.getenv("RESPAN_ENVIRONMENT", "example"),
        metadata={
            "integration": "together",
            "example": example_name,
            "run_id": marker,
            "example_run_id": marker,
        },
    )


def workflow_name(example_name: str) -> str:
    return f"together_{example_name.replace('-', '_')}"


def make_custom_identifier(example_name: str) -> str:
    return (
        os.getenv("RESPAN_EXAMPLE_RUN_ID")
        or f"together-{example_name}-{uuid4().hex[:8]}"
    )


@contextmanager
def example_attributes(
    example_name: str, custom_identifier: str | None = None
) -> Iterator[str]:
    marker = custom_identifier or make_custom_identifier(example_name)
    current_workflow_name = workflow_name(example_name)
    with propagate_attributes(
        custom_identifier=marker,
        trace_group_identifier=current_workflow_name,
        customer_identifier="together-example-user",
        thread_identifier=f"{marker}-{example_name}",
        metadata={
            "example": example_name,
            "run_id": marker,
            "example_run_id": marker,
            "workflow_name": current_workflow_name,
            "example_set": "together",
            "client_mode": "live" if _live_mode() else "deterministic",
        },
    ):
        yield marker


def first_message_text(response: Any) -> str:
    choices = getattr(response, "choices", None) or []
    message = getattr(choices[0], "message", None) if choices else None
    content = getattr(message, "content", None)
    return content if isinstance(content, str) else ""


def first_text_completion(response: Any) -> str:
    choices = getattr(response, "choices", None) or []
    text = getattr(choices[0], "text", None) if choices else None
    return text if isinstance(text, str) else ""


def print_start(example_name: str, marker: str) -> None:
    print(f"example={example_name} marker={marker}", flush=True)


def print_result(example_name: str, marker: str, result: Any) -> None:
    print(
        json.dumps(
            {"example": example_name, "marker": marker, "result": result},
            ensure_ascii=False,
            sort_keys=True,
        ),
        flush=True,
    )
