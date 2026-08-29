"""Shared utilities for Google ADK Respan examples."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable
from uuid import uuid4

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.base_llm import BaseLlm
from google.adk.models.lite_llm import LiteLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from respan import Respan, propagate_attributes
from respan_instrumentation_google_adk import GoogleADKInstrumentor

APP_USER_ID = "respan-google-adk-user"


def load_repo_env() -> None:
    """Load environment variables from respan-example-projects/.env."""
    repo_root = Path(__file__).resolve().parents[3]
    load_dotenv(repo_root / ".env", override=True)


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} must be set in respan-example-projects/.env")
    return value


def gateway_model_name() -> str:
    model = os.getenv("RESPAN_MODEL", "gpt-4o-mini")
    if "/" in model:
        return model
    return f"openai/{model}"


class DeterministicLlm(BaseLlm):
    """Small local model used by the repeatable full example run."""

    async def generate_content_async(
        self,
        llm_request: LlmRequest,
        stream: bool = False,
    ):
        has_function_response = any(
            getattr(part, "function_response", None) is not None
            for content in llm_request.contents
            for part in (content.parts or [])
        )
        if llm_request.tools_dict and not has_function_response:
            content = types.Content(
                role="model",
                parts=[
                    types.Part(
                        function_call=types.FunctionCall(
                            id="call-adk-weather-1",
                            name="get_weather",
                            args={"city": "San Francisco"},
                        )
                    )
                ],
            )
        elif has_function_response:
            content = types.Content(
                role="model",
                parts=[types.Part(text="San Francisco is sunny, 72F, with light wind.")],
            )
        else:
            content = types.Content(
                role="model",
                parts=[types.Part(text="This traced Google ADK agent is ready.")],
            )
        yield LlmResponse(
            model_version=self.model,
            content=content,
            partial=False,
            usage_metadata=types.GenerateContentResponseUsageMetadata(
                prompt_token_count=8,
                candidates_token_count=7,
                total_token_count=15,
            ),
        )


def create_gateway_model() -> BaseLlm:
    load_repo_env()
    if os.getenv("RESPAN_ADK_MODEL_MODE", "gateway") == "local":
        return DeterministicLlm(model="respan-adk-deterministic")
    gateway_api_key = os.getenv("RESPAN_GATEWAY_API_KEY") or require_env(
        "RESPAN_API_KEY"
    )
    gateway_base_url = os.getenv(
        "RESPAN_GATEWAY_BASE_URL",
        os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api"),
    )
    return LiteLlm(
        model=gateway_model_name(),
        api_key=gateway_api_key,
        api_base=gateway_base_url,
    )


def create_respan(app_name: str) -> Respan:
    load_repo_env()
    run_id = example_run_id()
    return Respan(
        app_name=app_name,
        api_key=require_env("RESPAN_API_KEY"),
        base_url=os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api"),
        instrumentations=[GoogleADKInstrumentor()],
        is_batching_enabled=False,
        metadata={
            "integration": "google-adk",
            "example": app_name,
            "run_id": run_id,
        },
    )


def example_run_id() -> str:
    return os.getenv("RESPAN_EXAMPLE_RUN_ID") or f"google-adk-{uuid4().hex[:10]}"


def example_attributes(app_name: str):
    run_id = example_run_id()
    return propagate_attributes(
        custom_identifier=f"{run_id}:{app_name}",
        trace_group_identifier=f"{run_id}:{app_name}",
        metadata={
            "integration": "google-adk",
            "example": app_name,
            "run_id": run_id,
        },
    )


def make_user_message(text: str) -> types.Content:
    return types.Content(role="user", parts=[types.Part(text=text)])


def final_response_text(events: Iterable[object]) -> str:
    output_parts: list[str] = []
    for event in events:
        is_final_response = getattr(event, "is_final_response", None)
        if not callable(is_final_response) or not is_final_response():
            continue
        content = getattr(event, "content", None)
        for part in getattr(content, "parts", []) or []:
            text = getattr(part, "text", None)
            if text:
                output_parts.append(text)
    return "\n".join(output_parts)


async def run_agent_once(*, agent: Agent, app_name: str, prompt: str) -> str:
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=app_name,
        user_id=APP_USER_ID,
    )
    runner = Runner(
        agent=agent,
        app_name=app_name,
        session_service=session_service,
    )
    events = []
    async for event in runner.run_async(
        user_id=APP_USER_ID,
        session_id=session.id,
        new_message=make_user_message(prompt),
    ):
        events.append(event)
    return final_response_text(events)
