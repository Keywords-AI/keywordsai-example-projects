from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from dotenv import load_dotenv
from livekit.agents import function_tool, llm
from livekit.agents.types import DEFAULT_API_CONNECT_OPTIONS, NOT_GIVEN
from respan import Respan, propagate_attributes
from respan_instrumentation_livekit import LiveKitInstrumentor

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai/api"


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


def workflow_name(example_name: str) -> str:
    return f"livekit_{example_name.replace('-', '_')}"


def make_custom_identifier(example_name: str) -> str:
    return f"livekit-{example_name}-{uuid4().hex[:8]}"


def make_respan(example_name: str) -> Respan:
    return Respan(
        api_key=require_respan_api_key(),
        base_url=respan_base_url(),
        app_name="livekit-examples",
        instrumentations=[LiveKitInstrumentor()],
        environment=os.getenv("RESPAN_ENVIRONMENT", "example"),
        metadata={"integration": "livekit", "example": example_name},
    )


def example_attributes(example_name: str, custom_identifier: str | None = None):
    custom_identifier = custom_identifier or make_custom_identifier(example_name)
    current_workflow_name = workflow_name(example_name)
    return propagate_attributes(
        custom_identifier=custom_identifier,
        trace_group_identifier=current_workflow_name,
        metadata={
            "example": example_name,
            "run_id": custom_identifier,
            "workflow_name": current_workflow_name,
            "client_mode": "mock-livekit",
        },
    )


def print_start(example_name: str, custom_identifier: str) -> None:
    print(f"example={example_name}", flush=True)
    print(f"custom_identifier={custom_identifier}", flush=True)
    print(f"workflow_name={workflow_name(example_name)}", flush=True)
    print("client_mode=mock-livekit", flush=True)


def print_result(label: str, value: Any) -> None:
    print(f"\n== {label} ==")
    if isinstance(value, str):
        print(value.strip())
        return
    print(json.dumps(value, default=str, indent=2, sort_keys=True))


def finish_respan(respan: Respan) -> None:
    shutdown = getattr(respan, "shutdown", None)
    if shutdown is not None:
        shutdown()


class MockLiveKitLLM(llm.LLM):
    def __init__(self, *, model: str = "gpt-4o-mini", provider: str = "openai") -> None:
        super().__init__()
        self._model = model
        self._provider = provider

    @property
    def model(self) -> str:
        return self._model

    @property
    def provider(self) -> str:
        return self._provider

    def chat(
        self,
        *,
        chat_ctx: llm.ChatContext,
        tools: list[llm.Tool] | None = None,
        conn_options=DEFAULT_API_CONNECT_OPTIONS,
        parallel_tool_calls=NOT_GIVEN,
        tool_choice=NOT_GIVEN,
        extra_kwargs=NOT_GIVEN,
    ) -> llm.LLMStream:
        scenario = "chat"
        if isinstance(extra_kwargs, dict):
            scenario = str(extra_kwargs.get("scenario", scenario))
        return MockLiveKitLLMStream(
            self,
            chat_ctx=chat_ctx,
            tools=tools or [],
            conn_options=conn_options,
            scenario=scenario,
        )

    async def aclose(self) -> None:
        return None


class MockLiveKitLLMStream(llm.LLMStream):
    def __init__(
        self,
        livekit_llm: MockLiveKitLLM,
        *,
        chat_ctx: llm.ChatContext,
        tools: list[llm.Tool],
        conn_options,
        scenario: str,
    ) -> None:
        self._scenario = scenario
        super().__init__(
            livekit_llm,
            chat_ctx=chat_ctx,
            tools=tools,
            conn_options=conn_options,
        )

    async def _run(self) -> None:
        await asyncio.sleep(0)
        if self._scenario == "stream":
            await self._send_text_chunks(
                request_id="mock-stream",
                chunks=["LiveKit ", "streaming ", "works."],
                prompt_tokens=11,
                completion_tokens=6,
            )
            return

        if self._scenario == "tool":
            await self._send_tool_call(
                name="lookup_room_status",
                arguments='{"room":"blue"}',
                call_id="call_livekit_blue_room",
                content="I will look up the room status.",
                prompt_tokens=14,
                completion_tokens=5,
            )
            return

        if self._scenario == "missing_tool":
            await self._send_tool_call(
                name="missing_tool",
                arguments='{"value":1}',
                call_id="call_missing_tool",
                content="I will call a missing tool to demonstrate error tracing.",
                prompt_tokens=12,
                completion_tokens=9,
            )
            return

        await self._send_text_chunks(
            request_id="mock-chat",
            chunks=["LiveKit mock response from a Respan traced LLM."],
            prompt_tokens=9,
            completion_tokens=8,
        )

    async def _send_text_chunks(
        self,
        *,
        request_id: str,
        chunks: list[str],
        prompt_tokens: int,
        completion_tokens: int,
    ) -> None:
        for content in chunks:
            self._event_ch.send_nowait(
                llm.ChatChunk(
                    id=request_id,
                    delta=llm.ChoiceDelta(role="assistant", content=content),
                )
            )
            await asyncio.sleep(0)
        self._event_ch.send_nowait(
            llm.ChatChunk(
                id=request_id,
                usage=llm.CompletionUsage(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens,
                    prompt_cached_tokens=2,
                ),
            )
        )

    async def _send_tool_call(
        self,
        *,
        name: str,
        arguments: str,
        call_id: str,
        content: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> None:
        tool_call = llm.FunctionToolCall(
            name=name,
            arguments=arguments,
            call_id=call_id,
        )
        self._event_ch.send_nowait(
            llm.ChatChunk(
                id="mock-tool",
                delta=llm.ChoiceDelta(
                    role="assistant",
                    content=content,
                    tool_calls=[tool_call],
                ),
            )
        )
        await asyncio.sleep(0)
        self._event_ch.send_nowait(
            llm.ChatChunk(
                id="mock-tool",
                usage=llm.CompletionUsage(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens,
                ),
            )
        )


@function_tool
async def lookup_room_status(room: str) -> str:
    """Return the occupancy status for a LiveKit room."""
    return f"Room {room} is online with two participants"


def chat_context(prompt: str) -> llm.ChatContext:
    ctx = llm.ChatContext.empty()
    ctx.add_message(
        role="system",
        content="You are a concise LiveKit assistant used for tracing examples.",
    )
    ctx.add_message(role="user", content=prompt)
    return ctx
