from __future__ import annotations

import json
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from uuid import uuid4

import httpx2
from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI
from respan import Respan, propagate_attributes
from respan_instrumentation_openai import OpenAIInstrumentor

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai/api"
DEFAULT_MODEL = "gpt-4.1-nano"
FAILURE_SENTINEL = "RESPAN_EXPECTED_401"


def load_root_env() -> None:
    # A shell-supplied group marker must win over values in the repository file.
    load_dotenv(PROJECT_ROOT / ".env", override=False)


def require_respan_api_key() -> str:
    load_root_env()
    api_key = os.getenv("RESPAN_API_KEY")
    if not api_key:
        raise RuntimeError("RESPAN_API_KEY must be set in the repository .env")
    return api_key


def respan_base_url() -> str:
    return os.getenv("RESPAN_BASE_URL", DEFAULT_RESPAN_BASE_URL).rstrip("/")


def model_name() -> str:
    return os.getenv("RESPAN_OPENAI_MODEL", DEFAULT_MODEL)


def run_id() -> str:
    marker = os.getenv("RESPAN_EXAMPLE_RUN_ID")
    if marker:
        return marker
    marker = f"openai-sdk-{uuid4().hex[:12]}"
    os.environ["RESPAN_EXAMPLE_RUN_ID"] = marker
    return marker


def workflow_name(example_name: str) -> str:
    return f"openai_{example_name.replace('-', '_')}"


def make_respan(example_name: str) -> Respan:
    marker = run_id()
    return Respan(
        api_key=require_respan_api_key(),
        base_url=respan_base_url(),
        app_name="openai-sdk-examples",
        environment=os.getenv("RESPAN_ENVIRONMENT", "example"),
        instrumentations=[OpenAIInstrumentor()],
        metadata={
            "integration": "openai",
            "example": example_name,
            "example_run_id": marker,
        },
    )


@contextmanager
def example_attributes(example_name: str):
    marker = run_id()
    current_workflow = workflow_name(example_name)
    with propagate_attributes(
        custom_identifier=f"{marker}:{example_name}",
        trace_group_identifier=current_workflow,
        metadata={
            "integration": "openai",
            "example": example_name,
            "example_run_id": marker,
            "workflow_name": current_workflow,
        },
    ):
        yield marker


def live_enabled() -> bool:
    return os.getenv("RESPAN_OPENAI_LIVE", "").lower() in {"1", "true", "yes"}


def client_mode() -> str:
    return "live-openai" if live_enabled() else "deterministic-openai-transport"


def _live_client_kwargs() -> dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("RESPAN_OPENAI_LIVE=1 requires OPENAI_API_KEY")
    kwargs: dict[str, Any] = {"api_key": api_key, "max_retries": 0}
    base_url = os.getenv("OPENAI_BASE_URL")
    if base_url:
        kwargs["base_url"] = base_url
    return kwargs


def make_sync_client() -> OpenAI:
    load_root_env()
    if live_enabled():
        return OpenAI(**_live_client_kwargs())
    return OpenAI(
        api_key="deterministic-test-key",
        base_url="https://openai.example.invalid/v1",
        max_retries=0,
        http_client=httpx2.Client(transport=httpx2.MockTransport(_sync_handler)),
    )


def make_async_client() -> AsyncOpenAI:
    load_root_env()
    if live_enabled():
        return AsyncOpenAI(**_live_client_kwargs())
    return AsyncOpenAI(
        api_key="deterministic-test-key",
        base_url="https://openai.example.invalid/v1",
        max_retries=0,
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(_async_handler)),
    )


def finish_respan(respan: Respan) -> None:
    try:
        respan.flush()
    finally:
        respan.shutdown()


def print_result(example_name: str, text: str) -> None:
    print(f"example={example_name}")
    print(f"example_run_id={run_id()}")
    print(f"workflow_name={workflow_name(example_name)}")
    print(f"client_mode={client_mode()}")
    print(text.strip())


def _request_body(request: httpx2.Request) -> dict[str, Any]:
    return json.loads(request.content or b"{}")


def _contains_failure(value: Any) -> bool:
    return FAILURE_SENTINEL in json.dumps(value, default=str)


def _chat_response(body: dict[str, Any]) -> dict[str, Any]:
    messages = body.get("messages") or []
    structured = bool(body.get("response_format"))
    if structured:
        content = json.dumps(
            {
                "title": "The Matrix",
                "rating": 9,
                "summary": "A deterministic science-fiction classic.",
                "pros": ["visuals", "ideas"],
                "cons": ["dense exposition"],
            }
        )
        finish_reason = "stop"
        message: dict[str, Any] = {"role": "assistant", "content": content}
    elif body.get("tools") and not any(
        message.get("role") == "tool"
        for message in messages
        if isinstance(message, dict)
    ):
        finish_reason = "tool_calls"
        message = {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "call_weather",
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "arguments": '{"city":"Paris"}',
                    },
                }
            ],
        }
    elif body.get("tools"):
        finish_reason = "stop"
        message = {
            "role": "assistant",
            "content": "The deterministic tool reports sunny weather in Paris.",
        }
    elif not messages:
        finish_reason = "stop"
        message = {
            "role": "assistant",
            "content": "Milestone plan: design, implement, validate.",
        }
    else:
        finish_reason = "stop"
        message = {
            "role": "assistant",
            "content": "Deterministic OpenAI chat response.",
        }
    return {
        "id": "chat_deterministic",
        "object": "chat.completion",
        "created": 1_786_972_800,
        "model": body.get("model") or model_name(),
        "choices": [
            {
                "index": 0,
                "message": message,
                "finish_reason": finish_reason,
            }
        ],
        "usage": {"prompt_tokens": 13, "completion_tokens": 7, "total_tokens": 20},
    }


def _responses_response(body: dict[str, Any]) -> dict[str, Any]:
    structured = bool(body.get("text", {}).get("format"))
    input_value = body.get("input")
    has_tool_result = False
    if isinstance(input_value, list):
        has_tool_result = any(
            isinstance(item, dict) and item.get("type") == "function_call_output"
            for item in input_value
        )
    if structured:
        text = json.dumps(
            {
                "title": "The Matrix",
                "rating": 9,
                "summary": "A deterministic science-fiction classic.",
                "pros": ["visuals", "ideas"],
                "cons": ["dense exposition"],
            }
        )
        output = [_response_message(text)]
    elif body.get("tools") and not has_tool_result:
        output = [
            {
                "id": "fc_weather",
                "type": "function_call",
                "call_id": "call_weather",
                "name": "get_weather",
                "arguments": '{"city":"Paris"}',
                "status": "completed",
            }
        ]
    else:
        text = (
            "The deterministic tool reports sunny weather in Paris."
            if has_tool_result
            else "Deterministic OpenAI Responses output."
        )
        output = [_response_message(text)]
    return {
        "id": "resp_deterministic",
        "object": "response",
        "created_at": 1_786_972_800,
        "status": "completed",
        "model": body.get("model") or model_name(),
        "output": output,
        "parallel_tool_calls": True,
        "tool_choice": "auto",
        "tools": [],
        "temperature": 1,
        "top_p": 1,
        "usage": {"input_tokens": 11, "output_tokens": 6, "total_tokens": 17},
        "error": None,
        "incomplete_details": None,
        "instructions": body.get("instructions"),
        "metadata": {},
    }


def _response_message(text: str) -> dict[str, Any]:
    return {
        "id": "msg_deterministic",
        "type": "message",
        "status": "completed",
        "role": "assistant",
        "content": [{"type": "output_text", "text": text, "annotations": []}],
    }


def _sync_handler(request: httpx2.Request) -> httpx2.Response:
    body = _request_body(request)
    if _contains_failure(body):
        return httpx2.Response(
            401,
            json={
                "error": {
                    "message": "deterministic OpenAI credential rejected",
                    "type": "authentication_error",
                }
            },
        )
    if request.url.path.endswith("/chat/completions"):
        if body.get("stream"):
            return _chat_stream_response(body)
        return httpx2.Response(200, json=_chat_response(body))
    if request.url.path.endswith("/responses"):
        if body.get("stream"):
            return _responses_stream_response(body)
        return httpx2.Response(200, json=_responses_response(body))
    if request.url.path.endswith("/embeddings"):
        return httpx2.Response(
            200,
            json={
                "object": "list",
                "model": body.get("model") or "text-embedding-3-small",
                "data": [
                    {"object": "embedding", "index": 0, "embedding": [0.1, 0.2, 0.3]}
                ],
                "usage": {"prompt_tokens": 4, "total_tokens": 4},
            },
        )
    raise AssertionError(f"unhandled deterministic endpoint: {request.url.path}")


async def _async_handler(request: httpx2.Request) -> httpx2.Response:
    return _sync_handler(request)


def _chat_stream_response(body: dict[str, Any]) -> httpx2.Response:
    chunks = [
        {
            "id": "chat_stream",
            "object": "chat.completion.chunk",
            "created": 1_786_972_800,
            "model": body.get("model") or model_name(),
            "choices": [
                {
                    "index": 0,
                    "delta": {"role": "assistant", "content": "Streaming "},
                    "finish_reason": None,
                }
            ],
        },
        {
            "id": "chat_stream",
            "object": "chat.completion.chunk",
            "created": 1_786_972_800,
            "model": body.get("model") or model_name(),
            "choices": [
                {
                    "index": 0,
                    "delta": {"content": "OpenAI response."},
                    "finish_reason": "stop",
                }
            ],
        },
        {
            "id": "chat_stream",
            "object": "chat.completion.chunk",
            "created": 1_786_972_800,
            "model": body.get("model") or model_name(),
            "choices": [],
            "usage": {"prompt_tokens": 9, "completion_tokens": 4, "total_tokens": 13},
        },
    ]
    payload = "".join(f"data: {json.dumps(chunk)}\n\n" for chunk in chunks)
    payload += "data: [DONE]\n\n"
    return httpx2.Response(
        200,
        headers={"content-type": "text/event-stream"},
        content=payload.encode(),
    )


def _responses_stream_response(body: dict[str, Any]) -> httpx2.Response:
    final_response = _responses_response(body)
    final_response["output"] = [_response_message("Streaming Responses output.")]
    events = [
        {
            "type": "response.output_text.delta",
            "sequence_number": 0,
            "item_id": "msg_deterministic",
            "output_index": 0,
            "content_index": 0,
            "delta": "Streaming ",
        },
        {
            "type": "response.output_text.delta",
            "sequence_number": 1,
            "item_id": "msg_deterministic",
            "output_index": 0,
            "content_index": 0,
            "delta": "Responses output.",
        },
        {
            "type": "response.completed",
            "sequence_number": 2,
            "response": final_response,
        },
    ]
    payload = "".join(
        f"event: {event['type']}\ndata: {json.dumps(event)}\n\n" for event in events
    )
    payload += "data: [DONE]\n\n"
    return httpx2.Response(
        200,
        headers={"content-type": "text/event-stream"},
        content=payload.encode(),
    )
