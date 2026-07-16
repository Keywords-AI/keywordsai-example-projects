"""Compatibility bridge for older Claude Agent SDK examples.

The examples used to import ``respan_exporter_anthropic_agents``. This bridge
keeps that shape while using ``respan-instrumentation-claude-agent-sdk`` and the
unified Respan OTEL exporter.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, AsyncIterator

import claude_agent_sdk
from claude_agent_sdk import ResultMessage
from dotenv import load_dotenv
from respan import Respan
from respan_instrumentation_claude_agent_sdk import ClaudeAgentSDKInstrumentor

load_dotenv(Path(__file__).resolve().parents[3] / ".env", override=False)


class RespanAnthropicAgentsExporter:
    """Legacy exporter facade backed by the active Claude Agent SDK instrumentor."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        *,
        app_name: str = "claude-agent-sdk-examples",
        capture_content: bool = True,
        **_: Any,
    ) -> None:
        self.api_key = api_key or os.getenv("RESPAN_API_KEY") or os.getenv("RESPAN_GATEWAY_API_KEY")
        self.base_url = (base_url or os.getenv("RESPAN_BASE_URL") or "https://api.respan.ai/api").rstrip("/")
        gateway_base_url = (os.getenv("RESPAN_GATEWAY_BASE_URL") or self.base_url).rstrip("/")
        gateway_api_key = os.getenv("RESPAN_GATEWAY_API_KEY") or self.api_key

        if gateway_api_key:
            os.environ["ANTHROPIC_API_KEY"] = gateway_api_key
            os.environ["ANTHROPIC_AUTH_TOKEN"] = gateway_api_key
        os.environ["ANTHROPIC_BASE_URL"] = f"{gateway_base_url}/anthropic"

        self._last_session_id: str | None = None
        self._respan = Respan(
            app_name=app_name,
            api_key=self.api_key,
            base_url=self.base_url,
            instrumentations=[ClaudeAgentSDKInstrumentor(capture_content=capture_content)],
        )

    async def query(self, *, prompt: str, options: Any) -> AsyncIterator[Any]:
        async for message in claude_agent_sdk.query(prompt=prompt, options=options):
            session_id = getattr(message, "session_id", None)
            if isinstance(session_id, str) and session_id:
                self._last_session_id = session_id
            if isinstance(message, ResultMessage):
                result_session_id = getattr(message, "session_id", None)
                if isinstance(result_session_id, str) and result_session_id:
                    self._last_session_id = result_session_id
            yield message

    def flush(self) -> None:
        self._respan.flush()

    def shutdown(self) -> None:
        self.flush()
