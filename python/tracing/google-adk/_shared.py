"""Shared utilities for Google ADK Respan examples."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from respan import Respan
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


def create_gateway_model() -> LiteLlm:
    load_repo_env()
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
    return Respan(
        app_name=app_name,
        api_key=require_env("RESPAN_API_KEY"),
        base_url=os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api"),
        instrumentations=[GoogleADKInstrumentor()],
        is_batching_enabled=False,
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
