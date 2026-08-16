"""Deterministic Claude Agent SDK examples using its real query protocol."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Any
import uuid

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[3]
load_dotenv(ROOT_DIR / ".env", override=True)

MODEL = os.getenv("CLAUDE_AGENT_SDK_MODEL", "claude-sonnet-4-5-20250514")


@dataclass(frozen=True)
class ToolSpec:
    name: str
    arguments: dict[str, Any]
    result: Any


class FakeClaudeTransport:
    """Fake CLI transport that exercises real SDK hooks and message parsing."""

    def __init__(
        self,
        *,
        session_id: str,
        prompt_text: str,
        tools: Sequence[ToolSpec],
    ) -> None:
        self._session_id = session_id
        self._prompt_text = prompt_text
        self._tools = list(tools)
        self._queue: asyncio.Queue[dict[str, Any] | None] = asyncio.Queue()
        self._hook_ids: dict[str, str] = {}
        self._tool_index = 0
        self._closed = False

    async def connect(self) -> None:
        return None

    async def write(self, data: str) -> None:
        message = json.loads(data)
        message_type = message.get("type")
        if message_type == "control_request":
            self._capture_hook_ids(message.get("request", {}).get("hooks"))
            await self._queue.put(
                {
                    "type": "control_response",
                    "response": {
                        "subtype": "success",
                        "request_id": message["request_id"],
                        "response": {"ok": True},
                    },
                }
            )
            return

        if message_type == "user":
            await self._queue.put(
                {
                    "type": "system",
                    "subtype": "init",
                    "session_id": self._session_id,
                    "data": {"session_id": self._session_id},
                }
            )
            if self._tools:
                await self._enqueue_tool_hook("PreToolUse")
            else:
                await self._enqueue_final_response()
            return

        if message_type != "control_response":
            return

        request_id = message.get("response", {}).get("request_id", "")
        if request_id.startswith("pre-"):
            await self._enqueue_tool_assistant_message()
            await self._enqueue_tool_hook("PostToolUse")
        elif request_id.startswith("post-"):
            self._tool_index += 1
            if self._tool_index < len(self._tools):
                await self._enqueue_tool_hook("PreToolUse")
            else:
                await self._enqueue_final_response()

    def _capture_hook_ids(self, hooks: Any) -> None:
        if not isinstance(hooks, dict):
            return
        for event_name, matchers in hooks.items():
            if not isinstance(matchers, list) or not matchers:
                continue
            callback_ids = matchers[0].get("hookCallbackIds", [])
            if callback_ids:
                self._hook_ids[event_name] = callback_ids[0]

    async def _enqueue_tool_hook(self, event_name: str) -> None:
        callback_id = self._hook_ids.get(event_name)
        if callback_id is None:
            raise RuntimeError(f"Instrumentation did not register {event_name}")
        tool = self._tools[self._tool_index]
        tool_use_id = f"tool-{self._tool_index + 1}"
        phase = "pre" if event_name == "PreToolUse" else "post"
        hook_input: dict[str, Any] = {
            "hook_event_name": event_name,
            "session_id": self._session_id,
            "transcript_path": "/tmp/respan-claude-agent-sdk.jsonl",
            "cwd": str(Path.cwd()),
            "permission_mode": "default",
            "tool_name": tool.name,
            "tool_input": tool.arguments,
            "tool_use_id": tool_use_id,
        }
        if event_name == "PostToolUse":
            hook_input["tool_response"] = tool.result
        await self._queue.put(
            {
                "type": "control_request",
                "request_id": f"{phase}-{tool_use_id}",
                "request": {
                    "subtype": "hook_callback",
                    "callback_id": callback_id,
                    "input": hook_input,
                    "tool_use_id": tool_use_id,
                },
            }
        )

    async def _enqueue_tool_assistant_message(self) -> None:
        tool = self._tools[self._tool_index]
        tool_use_id = f"tool-{self._tool_index + 1}"
        await self._queue.put(
            {
                "type": "assistant",
                "session_id": self._session_id,
                "message": {
                    "id": f"msg-{uuid.uuid4().hex[:8]}",
                    "model": MODEL,
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_use",
                            "id": tool_use_id,
                            "name": tool.name,
                            "input": tool.arguments,
                        }
                    ],
                    "usage": {"input_tokens": 30, "output_tokens": 5},
                },
            }
        )

    async def _enqueue_final_response(self) -> None:
        response_text = f"Completed: {self._prompt_text}"
        await self._queue.put(
            {
                "type": "assistant",
                "session_id": self._session_id,
                "message": {
                    "id": f"msg-{uuid.uuid4().hex[:8]}",
                    "model": MODEL,
                    "role": "assistant",
                    "content": [{"type": "text", "text": response_text}],
                    "usage": {"input_tokens": 4, "output_tokens": 10},
                },
            }
        )
        await self._queue.put(
            {
                "type": "result",
                "subtype": "success",
                "duration_ms": 800,
                "duration_api_ms": 500,
                "is_error": False,
                "num_turns": 1,
                "session_id": self._session_id,
                "total_cost_usd": 0.003,
                "usage": {
                    "input_tokens": 4,
                    "output_tokens": 10,
                    "cache_read_input_tokens": 5,
                    "cache_creation_input_tokens": 2,
                },
                "result": response_text,
            }
        )
        await self._queue.put(None)

    async def close(self) -> None:
        if not self._closed:
            self._closed = True
            await self._queue.put(None)

    async def end_input(self) -> None:
        return None

    def is_ready(self) -> bool:
        return True

    async def read_messages(self) -> AsyncIterator[dict[str, Any]]:
        while True:
            item = await self._queue.get()
            if item is None:
                break
            yield item


async def run_example(
    *,
    example_name: str,
    prompts: Sequence[str],
    tools: Sequence[ToolSpec] = (),
    resume: bool = False,
) -> None:
    import claude_agent_sdk
    from claude_agent_sdk import ClaudeAgentOptions, ResultMessage
    from respan import Respan
    from respan_instrumentation_claude_agent_sdk import ClaudeAgentSDKInstrumentor

    run_id = os.environ["RESPAN_EXAMPLE_RUN_ID"]
    session_id = str(uuid.uuid4())
    respan = Respan(
        api_key=os.environ["RESPAN_API_KEY"],
        base_url=os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api"),
        app_name=f"claude-agent-sdk-{example_name}",
        instrumentations=[
            ClaudeAgentSDKInstrumentor(
                agent_name=example_name,
                capture_content=True,
            )
        ],
        is_batching_enabled=False,
        environment=os.getenv("RESPAN_ENVIRONMENT", "examples"),
        metadata={
            "example_set": "claude-agent-sdk",
            "example_name": example_name,
            "example_run_id": run_id,
        },
    )
    instrumented_query = claude_agent_sdk.query
    current_transport: FakeClaudeTransport | None = None

    async def dispatch_query(*, prompt, options=None, transport=None):
        selected_transport = transport or current_transport
        if selected_transport is None:
            raise RuntimeError("Fake Claude transport was not configured")
        async for message in instrumented_query(
            prompt=prompt,
            options=options,
            transport=selected_transport,
        ):
            yield message

    claude_agent_sdk.query = dispatch_query
    try:
        with respan.propagate_attributes(
            customer_identifier="claude-agent-sdk-example-user",
            trace_group_identifier=f"claude-agent-sdk:{example_name}:{run_id}",
            custom_identifier=f"{example_name}:{run_id}",
            metadata={
                "example_set": "claude-agent-sdk",
                "example_name": example_name,
                "example_run_id": run_id,
            },
        ):
            for turn_index, prompt in enumerate(prompts):
                current_transport = FakeClaudeTransport(
                    session_id=session_id,
                    prompt_text=prompt,
                    tools=tools if turn_index == 0 else (),
                )
                options = ClaudeAgentOptions(
                    model=MODEL,
                    tools=[tool.name for tool in tools] or None,
                    system_prompt="Return concise deterministic example output.",
                    resume=session_id if resume and turn_index else None,
                )
                result = None
                async for message in claude_agent_sdk.query(
                    prompt=prompt,
                    options=options,
                ):
                    if isinstance(message, ResultMessage):
                        result = message
                if result is None:
                    raise RuntimeError("Claude Agent SDK example returned no result")
                if result.session_id != session_id:
                    raise RuntimeError("Resumed turn changed the Claude session id")
                print(
                    f"{example_name} turn={turn_index + 1} "
                    f"session={result.session_id} result={result.subtype}"
                )
    finally:
        claude_agent_sdk.query = instrumented_query
        respan.shutdown()
