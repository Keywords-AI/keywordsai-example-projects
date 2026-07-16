"""Compatibility bridge for older OpenAI Agents SDK examples.

The examples used to import ``respan_exporter_openai_agents.RespanTraceProcessor``.
This bridge keeps that import working while routing spans through the active
``respan-instrumentation-openai-agents`` package and the unified Respan OTEL
pipeline.
"""

from __future__ import annotations

import os
from typing import Any

from dotenv import find_dotenv, load_dotenv
from openai import AsyncOpenAI
from agents import set_default_openai_api, set_default_openai_client
from respan import Respan
from respan_instrumentation_openai_agents._instrumentation import _RespanTracingProcessor

load_dotenv(find_dotenv(), override=True)

_RESPAN: Respan | None = None
_GATEWAY_CLIENT_CONFIGURED = False


def _clean_url(value: str | None, default: str) -> str:
    return (value or default).rstrip("/")


def _configure_gateway_client(api_key: str | None) -> None:
    global _GATEWAY_CLIENT_CONFIGURED
    if _GATEWAY_CLIENT_CONFIGURED:
        return

    use_gateway = os.getenv("RESPAN_OPENAI_AGENTS_USE_OPENAI") != "1"
    gateway_base_url = _clean_url(
        os.getenv("RESPAN_GATEWAY_BASE_URL") or os.getenv("RESPAN_BASE_URL"),
        "https://api.respan.ai/api",
    )
    gateway_api_key = os.getenv("RESPAN_GATEWAY_API_KEY") or api_key
    respan_model = os.getenv("RESPAN_MODEL", "gpt-4o")
    os.environ.setdefault("OPENAI_DEFAULT_MODEL", respan_model)

    if use_gateway and gateway_api_key:
        # The gateway currently supports chat-compatible routes. Force the
        # OpenAI Agents SDK off the default Responses API for gateway runs.
        set_default_openai_api("chat_completions")
        os.environ["OPENAI_API_KEY"] = gateway_api_key
        os.environ["OPENAI_BASE_URL"] = gateway_base_url
        set_default_openai_client(
            AsyncOpenAI(api_key=gateway_api_key, base_url=os.environ["OPENAI_BASE_URL"])
        )
    _GATEWAY_CLIENT_CONFIGURED = True


def _ensure_respan(api_key: str | None, base_url: str | None) -> Respan | None:
    global _RESPAN
    if _RESPAN is not None:
        return _RESPAN

    resolved_api_key = api_key or os.getenv("RESPAN_API_KEY") or os.getenv("RESPAN_GATEWAY_API_KEY")
    if not resolved_api_key:
        return None

    _RESPAN = Respan(
        app_name=os.getenv("RESPAN_APP_NAME", "openai-agents-sdk-examples"),
        api_key=resolved_api_key,
        base_url=_clean_url(base_url or os.getenv("RESPAN_BASE_URL"), "https://api.respan.ai/api"),
    )
    return _RESPAN


class RespanTraceProcessor(_RespanTracingProcessor):
    """Legacy constructor, active OpenAI Agents processor implementation."""

    def __init__(
        self,
        api_key: str | None = None,
        endpoint: str | None = None,
        base_url: str | None = None,
        default_model: str | None = None,
        **_: Any,
    ) -> None:
        super().__init__()
        self.api_key = api_key or os.getenv("RESPAN_API_KEY")
        self.endpoint = endpoint
        self.base_url = base_url
        self.default_model = default_model or os.getenv("RESPAN_MODEL")
        self._respan = _ensure_respan(self.api_key, base_url)
        _configure_gateway_client(self.api_key)

    def shutdown(self) -> None:
        if self._respan is not None:
            self._respan.flush()

    def force_flush(self) -> None:
        if self._respan is not None:
            self._respan.flush()
