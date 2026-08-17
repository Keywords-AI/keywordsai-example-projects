"""Compatibility bridge for older OpenAI Agents SDK examples.

The examples used to import ``respan_exporter_openai_agents.RespanTraceProcessor``.
This bridge keeps that import working while routing spans through the active
``respan-instrumentation-openai-agents`` package and the unified Respan OTEL
pipeline.
"""

from __future__ import annotations

import asyncio
import os
from typing import Any

from agents import set_default_openai_api, set_default_openai_client
from dotenv import find_dotenv, load_dotenv
from openai import AsyncOpenAI
from respan import Respan
from respan_instrumentation_openai_agents._instrumentation import (
    _install_stream_patches,
    _RespanTracingProcessor,
)

load_dotenv(find_dotenv(), override=False)

_RESPAN: Respan | None = None
_GATEWAY_CLIENT_CONFIGURED = False
_GATEWAY_CLIENT: AsyncOpenAI | None = None
_GATEWAY_CLIENT_OWNER_LOOP: asyncio.AbstractEventLoop | None = None


def _clean_url(value: str | None, default: str) -> str:
    return (value or default).rstrip("/")


def _configure_gateway_client(api_key: str | None) -> None:
    global _GATEWAY_CLIENT, _GATEWAY_CLIENT_CONFIGURED
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
        _GATEWAY_CLIENT = AsyncOpenAI(
            api_key=gateway_api_key, base_url=os.environ["OPENAI_BASE_URL"]
        )
        set_default_openai_client(_GATEWAY_CLIENT)
    _GATEWAY_CLIENT_CONFIGURED = True


def _claim_gateway_client_loop() -> None:
    """Bind the retained async client to the loop that first uses an Agent trace."""
    global _GATEWAY_CLIENT_OWNER_LOOP
    if _GATEWAY_CLIENT is None:
        return
    try:
        current_loop = asyncio.get_running_loop()
    except RuntimeError:
        return
    if _GATEWAY_CLIENT_OWNER_LOOP is None:
        _GATEWAY_CLIENT_OWNER_LOOP = current_loop
    elif _GATEWAY_CLIENT_OWNER_LOOP is not current_loop:
        raise RuntimeError(
            "The shared OpenAI Agents client must stay on its owning event loop"
        )


def has_direct_responses_credentials() -> bool:
    """Return whether hosted Responses tools can run without gateway coercion."""
    return os.getenv("RESPAN_OPENAI_AGENTS_USE_OPENAI") == "1" and bool(
        os.getenv("OPENAI_API_KEY")
    )


def _ensure_respan(api_key: str | None, base_url: str | None) -> Respan | None:
    global _RESPAN
    if _RESPAN is not None:
        return _RESPAN

    resolved_api_key = (
        api_key or os.getenv("RESPAN_API_KEY") or os.getenv("RESPAN_GATEWAY_API_KEY")
    )
    if not resolved_api_key:
        return None

    _RESPAN = Respan(
        app_name=os.getenv("RESPAN_APP_NAME", "openai-agents-sdk-examples"),
        api_key=resolved_api_key,
        base_url=_clean_url(
            base_url or os.getenv("RESPAN_BASE_URL"), "https://api.respan.ai/api"
        ),
        # The explicit Agents trace processor owns provider-call coverage.
        # Direct OpenAI auto-instrumentation would duplicate its chat spans.
        is_auto_instrument=False,
        log_level=os.getenv("RESPAN_LOG_LEVEL", "WARNING"),
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
        marker = os.getenv("RESPAN_EXAMPLE_RUN_ID")
        super().__init__(
            metadata={"example_run_id": marker} if marker else None,
        )
        self.api_key = api_key or os.getenv("RESPAN_API_KEY")
        self.endpoint = endpoint
        self.base_url = base_url
        self.default_model = default_model or os.getenv("RESPAN_MODEL")
        self._respan = _ensure_respan(self.api_key, base_url)
        _install_stream_patches()
        _configure_gateway_client(self.api_key)

    def on_trace_start(self, trace) -> None:
        _claim_gateway_client_loop()
        return super().on_trace_start(trace)

    def shutdown(self) -> None:
        if self._respan is not None:
            self._respan.flush()

    def force_flush(self) -> None:
        if self._respan is not None:
            self._respan.flush()


def flush_respan() -> None:
    """Flush all example spans without closing the shared test-session client."""
    if _RESPAN is not None:
        _RESPAN.flush()


async def shutdown_respan_async() -> None:
    """Close the exporter and retained gateway client on its owning event loop."""
    global _GATEWAY_CLIENT, _GATEWAY_CLIENT_CONFIGURED
    global _GATEWAY_CLIENT_OWNER_LOOP, _RESPAN

    try:
        if _RESPAN is not None:
            _RESPAN.shutdown()
            _RESPAN = None
    finally:
        client = _GATEWAY_CLIENT
        if client is None:
            _GATEWAY_CLIENT_CONFIGURED = False
        else:
            current_loop = asyncio.get_running_loop()
            if (
                _GATEWAY_CLIENT_OWNER_LOOP is not None
                and _GATEWAY_CLIENT_OWNER_LOOP is not current_loop
            ):
                raise RuntimeError(
                    "The shared OpenAI Agents client must close on its owning event loop"
                )
            await client.close()
            _GATEWAY_CLIENT = None
            _GATEWAY_CLIENT_OWNER_LOOP = None
            _GATEWAY_CLIENT_CONFIGURED = False
