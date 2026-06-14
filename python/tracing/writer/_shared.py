from __future__ import annotations

import json
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from uuid import uuid4

import httpx
from dotenv import load_dotenv
from respan import Respan, propagate_attributes
from respan_instrumentation_writer import WriterInstrumentor
from writerai import AsyncWriter, Writer

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai/api"
DEFAULT_WRITER_MODEL = "palmyra-x5"
DEFAULT_WRITER_VISION_MODEL = "palmyra-vision"
DEFAULT_WRITER_TRANSLATION_MODEL = "palmyra-translate"
MOCK_BASE_URL = "https://writer.mock"


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
    return os.getenv("WRITER_MODEL", DEFAULT_WRITER_MODEL)


def vision_model_name() -> str:
    return os.getenv("WRITER_VISION_MODEL", DEFAULT_WRITER_VISION_MODEL)


def translation_model_name() -> str:
    return os.getenv("WRITER_TRANSLATION_MODEL", DEFAULT_WRITER_TRANSLATION_MODEL)


def writer_api_key() -> str | None:
    return os.getenv("WRITER_API_KEY")


def use_mock_writer() -> bool:
    mode = os.getenv("WRITER_EXAMPLE_MODE", "").strip().lower()
    if mode in {"mock", "offline"}:
        return True
    if mode in {"live", "real"}:
        return False
    return writer_api_key() is None


def client_mode() -> str:
    return "mock-writer" if use_mock_writer() else "live-writer"


def make_respan(example_name: str) -> Respan:
    api_key = require_respan_api_key()
    return Respan(
        api_key=api_key,
        base_url=respan_base_url(),
        app_name="writer-examples",
        instrumentations=[WriterInstrumentor()],
        environment=os.getenv("RESPAN_ENVIRONMENT", "example"),
        metadata={"integration": "writer", "example": example_name},
    )


def make_client() -> Writer:
    load_root_env()
    if use_mock_writer():
        return Writer(
            api_key="mock-writer-key",
            base_url=MOCK_BASE_URL,
            http_client=httpx.Client(transport=httpx.MockTransport(_mock_writer_response)),
        )

    api_key = writer_api_key()
    if not api_key:
        raise RuntimeError("WRITER_API_KEY must be set for live Writer examples")
    return Writer(api_key=api_key)


async def make_async_client() -> AsyncWriter:
    load_root_env()
    if use_mock_writer():
        return AsyncWriter(
            api_key="mock-writer-key",
            base_url=MOCK_BASE_URL,
            http_client=httpx.AsyncClient(
                transport=httpx.MockTransport(_mock_writer_response)
            ),
        )

    api_key = writer_api_key()
    if not api_key:
        raise RuntimeError("WRITER_API_KEY must be set for live Writer examples")
    return AsyncWriter(api_key=api_key)


def workflow_name(example_name: str) -> str:
    return f"writer_{example_name.replace('-', '_')}"


def make_custom_identifier(example_name: str) -> str:
    return f"writer-{example_name}-{uuid4().hex[:8]}"


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
            "client_mode": client_mode(),
        },
    ):
        yield custom_identifier


def graph_ids() -> list[str]:
    value = os.getenv("WRITER_GRAPH_IDS") or os.getenv("WRITER_GRAPH_ID")
    if value:
        return [item.strip() for item in value.split(",") if item.strip()]
    if use_mock_writer():
        return ["graph_mock"]
    raise RuntimeError("Set WRITER_GRAPH_ID or WRITER_GRAPH_IDS for live graph examples")


def application_id() -> str:
    value = os.getenv("WRITER_APPLICATION_ID")
    if value:
        return value
    if use_mock_writer():
        return "app_mock"
    raise RuntimeError("Set WRITER_APPLICATION_ID for live application examples")


def file_id() -> str:
    value = os.getenv("WRITER_FILE_ID") or os.getenv("WRITER_VISION_FILE_ID")
    if value:
        return value
    if use_mock_writer():
        return "file_mock"
    raise RuntimeError("Set WRITER_FILE_ID or WRITER_VISION_FILE_ID for live file examples")


def print_start(example_name: str, custom_identifier: str) -> None:
    print(f"example={example_name}", flush=True)
    print(f"custom_identifier={custom_identifier}", flush=True)
    print(f"workflow_name={workflow_name(example_name)}", flush=True)
    print(f"client_mode={client_mode()}", flush=True)


def print_result(label: str, value: Any) -> None:
    print(f"\n== {label} ==")
    if isinstance(value, str):
        print(value.strip())
        return
    print(json.dumps(value, default=str, indent=2, sort_keys=True))


def finish_respan(respan: Respan) -> None:
    respan.flush()
    shutdown = getattr(respan, "shutdown", None)
    if shutdown is not None:
        shutdown()


def _json_body(request: httpx.Request) -> dict[str, Any]:
    if not request.content:
        return {}
    try:
        body = json.loads(request.content.decode("utf-8"))
    except Exception:
        return {}
    return body if isinstance(body, dict) else {}


def _response(request: httpx.Request, payload: dict[str, Any]) -> httpx.Response:
    return httpx.Response(200, json=payload, request=request)


def _sse_response(request: httpx.Request, events: list[dict[str, Any]]) -> httpx.Response:
    content = "".join(f"data: {json.dumps(event)}\n\n" for event in events)
    content += "data: [DONE]\n\n"
    return httpx.Response(
        200,
        content=content.encode("utf-8"),
        headers={"content-type": "text/event-stream"},
        request=request,
    )


def _chat_payload(body: dict[str, Any]) -> dict[str, Any]:
    messages = body.get("messages") or []
    user_content = ""
    if messages and isinstance(messages[-1], dict):
        user_content = str(messages[-1].get("content") or "")

    content = f"Writer mock response for: {user_content[:80]}"
    tool_calls = None
    finish_reason = "stop"
    if body.get("tools"):
        content = ""
        finish_reason = "tool_calls"
        tool_calls = [
            {
                "id": "call_mock_weather",
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "arguments": json.dumps({"city": "Tokyo"}),
                },
            }
        ]
    elif body.get("response_format"):
        content = json.dumps({"summary": "mock structured output", "sentiment": "positive"})

    message: dict[str, Any] = {"role": "assistant", "content": content}
    if tool_calls:
        message["tool_calls"] = tool_calls

    return {
        "id": "chatcmpl_mock",
        "object": "chat.completion",
        "created": 1,
        "model": body.get("model") or DEFAULT_WRITER_MODEL,
        "choices": [{"index": 0, "finish_reason": finish_reason, "message": message}],
        "usage": {"prompt_tokens": 12, "completion_tokens": 8, "total_tokens": 20},
    }


def _chat_stream_response(request: httpx.Request, body: dict[str, Any]) -> httpx.Response:
    model = body.get("model") or DEFAULT_WRITER_MODEL
    events = [
        {
            "id": "chatcmpl_mock_stream",
            "object": "chat.completion.chunk",
            "created": 1,
            "model": model,
            "choices": [{"index": 0, "delta": {"role": "assistant", "content": "Writer "}}],
        },
        {
            "id": "chatcmpl_mock_stream",
            "object": "chat.completion.chunk",
            "created": 1,
            "model": model,
            "choices": [{"index": 0, "delta": {"content": "streaming response."}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 7, "completion_tokens": 4, "total_tokens": 11},
        },
    ]
    return _sse_response(request, events)


def _completion_stream_response(request: httpx.Request) -> httpx.Response:
    return _sse_response(request, [{"value": "Mock "}, {"value": "completion."}])


def _application_stream_response(request: httpx.Request) -> httpx.Response:
    return _sse_response(
        request,
        [
            {"delta": {"content": "Mock application "}},
            {"delta": {"content": "stream."}},
        ],
    )


def _mock_writer_response(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    body = _json_body(request)

    if path == "/v1/chat":
        if body.get("stream") is True:
            return _chat_stream_response(request, body)
        return _response(request, _chat_payload(body))

    if path == "/v1/completions":
        if body.get("stream") is True:
            return _completion_stream_response(request)
        return _response(
            request,
            {
                "model": body.get("model") or DEFAULT_WRITER_MODEL,
                "choices": [{"text": "Mock Writer text completion."}],
            },
        )

    if path == "/v1/graphs/question":
        return _response(
            request,
            {
                "answer": "Mock graph answer grounded in the example graph.",
                "question": body.get("question") or "",
                "sources": [],
            },
        )

    if path.startswith("/v1/applications/"):
        if body.get("stream") is True:
            return _application_stream_response(request)
        return _response(
            request,
            {
                "title": "mock output",
                "suggestion": "Mock application generation.",
            },
        )

    if path == "/v1/vision":
        return _response(request, {"data": "Mock vision analysis for the provided file."})

    if path == "/v1/translation":
        return _response(request, {"data": "Bonjour depuis Writer."})

    if path == "/v1/tools/web-search":
        return _response(
            request,
            {
                "query": body.get("query") or "",
                "answer": "Mock web search answer.",
                "sources": [
                    {"url": "https://www.respan.ai", "raw_content": "Respan tracing"}
                ],
            },
        )

    if path.startswith("/v1/tools/pdf-parser/"):
        return _response(request, {"content": "# Mock PDF\nParsed Writer PDF content."})

    return httpx.Response(404, json={"error": f"Unhandled mock path: {path}"}, request=request)
