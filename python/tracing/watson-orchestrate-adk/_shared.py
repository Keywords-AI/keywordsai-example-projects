"""Shared helpers for Watson Orchestrate ADK Respan examples."""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from uuid import uuid4

from dotenv import load_dotenv
from ibm_watsonx_orchestrate.client.autodiscover.watsonx_ai.watsonx_ai_client import (
    WatsonxAIClient,
)
from ibm_watsonx_orchestrate_clients.chat.run_client import RunClient
from respan import Respan, propagate_attributes
from respan_instrumentation_watson_orchestrate_adk import (
    WatsonOrchestrateADKInstrumentor,
)

EXAMPLE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = EXAMPLE_DIR.parents[2]
DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai/api"
DEFAULT_MODEL = "watsonx/meta-llama/llama-3-3-70b-instruct"


class DeterministicWatsonError(Exception):
    status_code = 429


def load_repo_env() -> None:
    load_dotenv(PROJECT_ROOT / ".env", override=False)


def require_env(name: str) -> str:
    load_repo_env()
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} must be set")
    return value


def optional_env(name: str) -> str | None:
    load_repo_env()
    return os.getenv(name) or None


def marker_for(example_name: str) -> str:
    return os.getenv("RESPAN_EXAMPLE_RUN_ID") or (
        f"watson-orchestrate-{example_name}-{uuid4().hex[:8]}"
    )


def workflow_name(example_name: str) -> str:
    return f"watson_orchestrate_{example_name.replace('-', '_')}"


def create_respan(app_name: str, marker: str) -> Respan:
    return Respan(
        app_name="watson-orchestrate-adk-examples",
        api_key=require_env("RESPAN_API_KEY"),
        base_url=os.getenv("RESPAN_BASE_URL", DEFAULT_RESPAN_BASE_URL),
        instrumentations=[WatsonOrchestrateADKInstrumentor()],
        is_batching_enabled=False,
        metadata={
            "integration": "watson-orchestrate-adk",
            "example": app_name,
            "run_id": marker,
            "example_run_id": marker,
        },
        environment="examples",
    )


@contextmanager
def example_attributes(example_name: str, marker: str) -> Iterator[None]:
    name = workflow_name(example_name)
    with propagate_attributes(
        custom_identifier=marker,
        trace_group_identifier=name,
        customer_identifier="watson-orchestrate-example-user",
        thread_identifier=f"{marker}-{example_name}",
        metadata={
            "example": example_name,
            "example_set": "watson-orchestrate-adk",
            "run_id": marker,
            "example_run_id": marker,
            "workflow_name": name,
        },
    ):
        yield


def _create_run(
    self: Any,
    message: str,
    agent_id: str | None = None,
    thread_id: str | None = None,
    capture_logs: bool = False,
) -> dict[str, Any]:
    del self, capture_logs
    if "provider failure" in message.lower():
        raise DeterministicWatsonError("deterministic provider rate limit")
    return {
        "run_id": "watson-run-deterministic",
        "thread_id": thread_id or "watson-thread-deterministic",
        "agent_id": agent_id or "watson-agent-deterministic",
        "status": "queued",
        "message": message,
    }


async def _stream_run_with_websocket(
    self: Any,
    agent_id: str,
    thread_id: str,
    run_id: str,
    **kwargs: Any,
) -> dict[str, Any]:
    del self, kwargs
    return {
        "agent_id": agent_id,
        "thread_id": thread_id,
        "run_id": run_id,
        "status": "completed",
    }


def _generate_response(
    self: Any,
    input: str,
    model: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    del self, kwargs
    if "provider failure" in input.lower():
        raise DeterministicWatsonError("deterministic provider rate limit")
    return {
        "model": model or DEFAULT_MODEL,
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Watson Orchestrate tracing is deterministic.",
                }
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 6,
            "total_tokens": 16,
        },
    }


@contextmanager
def deterministic_watson_runtime() -> Iterator[None]:
    originals = {
        (RunClient, "create_run"): RunClient.create_run,
        (RunClient, "stream_run_with_websocket"): RunClient.stream_run_with_websocket,
        (WatsonxAIClient, "generate_response"): WatsonxAIClient.generate_response,
    }
    RunClient.create_run = _create_run
    RunClient.stream_run_with_websocket = _stream_run_with_websocket
    WatsonxAIClient.generate_response = _generate_response
    try:
        yield
    finally:
        for (cls, method_name), original in originals.items():
            current = getattr(cls, method_name)
            if current in {
                _create_run,
                _stream_run_with_websocket,
                _generate_response,
            }:
                setattr(cls, method_name, original)


def deterministic_run_client() -> RunClient:
    return object.__new__(RunClient)


def deterministic_chat_client() -> WatsonxAIClient:
    client = object.__new__(WatsonxAIClient)
    object.__setattr__(client, "model", DEFAULT_MODEL)
    return client
