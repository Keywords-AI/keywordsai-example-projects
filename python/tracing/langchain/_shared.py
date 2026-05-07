"""Shared helpers for the numbered LangChain tracing examples."""

from __future__ import annotations

import os
from contextlib import suppress
from typing import Any

from dotenv import find_dotenv, load_dotenv
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage
from langchain_core.tools import tool
from respan_instrumentation_langchain import add_respan_callback
from respan_tracing import RespanTelemetry

load_dotenv(find_dotenv(), override=False)


class NoopTelemetry:
    def flush(self) -> None:
        return None


def init_telemetry(app_name: str) -> RespanTelemetry | NoopTelemetry:
    """Initialize Respan export without auto-patching; examples attach callbacks explicitly."""
    api_key = os.getenv("RESPAN_API_KEY")
    if not api_key:
        return NoopTelemetry()

    return RespanTelemetry(
        app_name=app_name,
        api_key=api_key,
        base_url=os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api"),
        is_auto_instrument=False,
        is_batching_enabled=False,
        is_enabled=True,
    )


def tracing_config(name: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    return add_respan_callback(
        {
            "run_name": name,
            "tags": ["respan-langchain-example", name],
            "metadata": {"example": name, **(metadata or {})},
        }
    )


def flush(telemetry: RespanTelemetry | NoopTelemetry) -> None:
    with suppress(Exception):
        telemetry.flush()


def message_text(message: Any) -> str:
    text = getattr(message, "text", None)
    if text:
        return str(text)
    content = getattr(message, "content", message)
    return str(content)


@tool
def get_weather(city: str) -> str:
    """Get deterministic weather for a city."""
    return f"It is sunny in {city}."


class ToolCallingFakeMessagesListChatModel(FakeMessagesListChatModel):
    """Fake chat model that supports tool binding for offline agent examples."""

    def bind_tools(
        self,
        tools: Any,
        **kwargs: Any,
    ) -> "ToolCallingFakeMessagesListChatModel":
        return self


def fake_tool_calling_model(
    *,
    tool_name: str = "get_weather",
    args: dict[str, Any] | None = None,
    final_text: str = "The tool result has been handled.",
) -> ToolCallingFakeMessagesListChatModel:
    call_id = f"call_{tool_name}"
    return ToolCallingFakeMessagesListChatModel(
        responses=[
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": tool_name,
                        "args": args or {"city": "San Francisco"},
                        "id": call_id,
                    }
                ],
            ),
            AIMessage(content=final_text),
        ]
    )


def make_openai_chat_model(model_name: str = "gpt-4o-mini") -> Any | None:
    """Return a provider-backed chat model for examples that need provider features."""
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("RESPAN_API_KEY")
    if not api_key:
        return None

    from langchain_openai import ChatOpenAI

    kwargs: dict[str, Any] = {
        "model": os.getenv("LANGCHAIN_OPENAI_MODEL", model_name),
        "api_key": api_key,
        "temperature": 0,
    }
    base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("RESPAN_OPENAI_BASE_URL")
    if base_url:
        kwargs["base_url"] = base_url
    return ChatOpenAI(**kwargs)
