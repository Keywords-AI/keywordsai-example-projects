"""Shared setup for Vertex AI OTel 2.x tracing examples."""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

from dotenv import load_dotenv
from respan import Respan, propagate_attributes
from respan_instrumentation_vertexai import VertexAIInstrumentor
from vertexai.generative_models import ChatSession, GenerativeModel

EXAMPLE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = EXAMPLE_DIR.parents[2]
DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai/api"
DEFAULT_MODEL = "gemini-2.5-flash"


class DeterministicVertexError(Exception):
    status_code = 503


def load_repo_env() -> None:
    load_dotenv(PROJECT_ROOT / ".env", override=False)


def require_env(*names: str) -> str:
    load_repo_env()
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    raise RuntimeError(f"One of {', '.join(names)} must be set")


def marker_for(example_name: str) -> str:
    return os.getenv("RESPAN_EXAMPLE_RUN_ID") or (
        f"vertexai-{example_name}-{uuid4().hex[:8]}"
    )


def model_name() -> str:
    return os.getenv("VERTEXAI_MODEL", DEFAULT_MODEL)


def _usage(prompt: int, completion: int) -> Any:
    return SimpleNamespace(
        prompt_token_count=prompt,
        candidates_token_count=completion,
        thoughts_token_count=0,
        total_token_count=prompt + completion,
    )


def _response(
    text: str,
    *,
    prompt_tokens: int,
    completion_tokens: int,
    function_call: Any = None,
) -> Any:
    parts = (
        [SimpleNamespace(function_call=function_call)]
        if function_call is not None
        else [SimpleNamespace(text=text)]
    )
    return SimpleNamespace(
        text=text,
        candidates=[
            SimpleNamespace(content=SimpleNamespace(role="model", parts=parts))
        ],
        usage_metadata=_usage(prompt_tokens, completion_tokens),
    )


def _generate_content(
    self: Any, contents: Any, *, stream: bool = False, **kwargs: Any
) -> Any:
    del self, kwargs
    text = contents if isinstance(contents, str) else ""
    if "provider failure" in text.lower():
        raise DeterministicVertexError("deterministic Vertex provider unavailable")
    if stream:
        return iter(
            [
                _response("Vertex ", prompt_tokens=0, completion_tokens=0),
                _response("streamed clearly.", prompt_tokens=10, completion_tokens=4),
            ]
        )
    if "weather" in text.lower() and "tool result" not in text.lower():
        return _response(
            "",
            prompt_tokens=12,
            completion_tokens=6,
            function_call=SimpleNamespace(
                id="vertex-weather-1",
                name="get_weather",
                args={"city": "Tokyo"},
            ),
        )
    if "tool result" in text.lower():
        return _response(
            "Tokyo is sunny and 22 C.",
            prompt_tokens=18,
            completion_tokens=7,
        )
    return _response(
        "Vertex tracing is deterministic.",
        prompt_tokens=9,
        completion_tokens=5,
    )


async def _generate_content_async(self: Any, contents: Any, **kwargs: Any) -> Any:
    return _generate_content(self, contents, **kwargs)


def _send_message(
    self: Any, content: Any, *, stream: bool = False, **kwargs: Any
) -> Any:
    return _generate_content(self, content, stream=stream, **kwargs)


async def _send_message_async(self: Any, content: Any, **kwargs: Any) -> Any:
    return _generate_content(self, content, **kwargs)


@contextmanager
def deterministic_vertex_runtime() -> Iterator[None]:
    originals = {
        (GenerativeModel, "generate_content"): GenerativeModel.generate_content,
        (
            GenerativeModel,
            "generate_content_async",
        ): GenerativeModel.generate_content_async,
        (ChatSession, "send_message"): ChatSession.send_message,
        (ChatSession, "send_message_async"): ChatSession.send_message_async,
    }
    GenerativeModel.generate_content = _generate_content
    GenerativeModel.generate_content_async = _generate_content_async
    ChatSession.send_message = _send_message
    ChatSession.send_message_async = _send_message_async
    try:
        yield
    finally:
        for (cls, method_name), original in originals.items():
            if getattr(cls, method_name) in {
                _generate_content,
                _generate_content_async,
                _send_message,
                _send_message_async,
            }:
                setattr(cls, method_name, original)


def deterministic_model(
    *,
    system_instruction: str | None = None,
    tools: list[Any] | None = None,
) -> GenerativeModel:
    model = object.__new__(GenerativeModel)
    object.__setattr__(model, "_model_name", model_name())
    object.__setattr__(model, "_system_instruction", system_instruction)
    object.__setattr__(model, "_tools", tools)
    return model


def deterministic_chat(model: GenerativeModel) -> ChatSession:
    chat = object.__new__(ChatSession)
    object.__setattr__(chat, "model", model)
    return chat


def make_respan(example_name: str, marker: str) -> Respan:
    return Respan(
        api_key=require_env("RESPAN_API_KEY", "RESPAN_GATEWAY_API_KEY"),
        base_url=os.getenv("RESPAN_BASE_URL", DEFAULT_RESPAN_BASE_URL).rstrip("/"),
        app_name="vertexai-examples",
        instrumentations=[VertexAIInstrumentor()],
        environment=os.getenv("RESPAN_ENVIRONMENT", "example"),
        metadata={
            "integration": "vertexai",
            "example": example_name,
            "run_id": marker,
            "example_run_id": marker,
        },
    )


def workflow_name(example_name: str) -> str:
    return f"vertexai_{example_name.replace('-', '_')}"


@contextmanager
def example_attributes(example_name: str, marker: str) -> Iterator[None]:
    name = workflow_name(example_name)
    with propagate_attributes(
        custom_identifier=marker,
        trace_group_identifier=name,
        customer_identifier="vertexai-example-user",
        thread_identifier=f"{marker}-{example_name}",
        metadata={
            "example": example_name,
            "example_set": "vertexai",
            "run_id": marker,
            "example_run_id": marker,
            "workflow_name": name,
        },
    ):
        yield
