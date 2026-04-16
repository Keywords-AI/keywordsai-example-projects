"""
Run all examples with a fake SDK query to verify instrumentation works.

Does NOT require ANTHROPIC_API_KEY — simulates SDK messages to exercise
each example's instrumentation code path end-to-end via Respan.
"""

import asyncio
import time
import uuid

from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env", override=True)

import claude_agent_sdk
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    SystemMessage,
)
from claude_agent_sdk.types import TextBlock, ToolUseBlock

from respan import Respan
from respan_instrumentation_anthropic_agents import AnthropicAgentsInstrumentor


# Mutable reference that the instrumentor's wrapper will call through
_current_fake = None


async def _dispatch_query(prompt, options=None, **kwargs):
    """Dispatch to the current fake query function."""
    async for msg in _current_fake(prompt, options=options, **kwargs):
        yield msg


def set_fake_query(session_id: str, prompt_text: str, with_tools: bool = False):
    """Set the current fake query that the instrumented wrapper calls through."""
    global _current_fake

    async def fake(prompt, options=None, **kwargs):
        yield SystemMessage(subtype="init", data={"session_id": session_id})

        content_blocks = [TextBlock(text=f"Response to: {prompt_text}")]
        if with_tools:
            content_blocks.append(
                ToolUseBlock(
                    id="tool-1",
                    name="Glob",
                    input={"pattern": "*.py"},
                )
            )

        msg = AssistantMessage(
            content=content_blocks,
            model="claude-sonnet-4-5-20250514",
        )
        msg.id = f"msg-{uuid.uuid4().hex[:8]}"
        yield msg

        yield ResultMessage(
            subtype="success",
            duration_ms=800,
            duration_api_ms=500,
            is_error=False,
            num_turns=1,
            session_id=session_id,
            total_cost_usd=0.003,
            usage={
                "input_tokens": 50,
                "output_tokens": 10,
                "cache_read_input_tokens": 5,
                "cache_creation_input_tokens": 0,
            },
            result=f"Response to: {prompt_text}",
        )

    _current_fake = fake


async def run_hello_world():
    """basic/hello_world_test.py"""
    session_id = str(uuid.uuid4())
    set_fake_query(session_id, "What is 2 + 2?")

    from basic._sdk_runtime import query_for_result

    result = await query_for_result(
        prompt="What is 2 + 2? Reply in one word.",
        options=ClaudeAgentOptions(),
    )
    print(f"  Result: {result.subtype}, Session: {result.session_id}")
    return session_id


async def run_wrapped_query():
    """basic/wrapped_query_test.py"""
    session_id = str(uuid.uuid4())
    set_fake_query(session_id, "Primary colors")

    from basic._sdk_runtime import query_for_result

    message_types = []

    def _on_message(message):
        message_types.append(type(message).__name__)

    result = await query_for_result(
        prompt="Name three primary colors.",
        options=ClaudeAgentOptions(),
        on_message=_on_message,
    )
    print(f"  Flow: {' -> '.join(message_types)}, Result: {result.subtype}")
    return session_id


async def run_multi_turn():
    """sessions/multi_turn_test.py"""
    prompts = ["My name is Alice.", "What is my name?"]
    session_ids = []

    for prompt in prompts:
        session_id = str(uuid.uuid4())
        session_ids.append(session_id)
        set_fake_query(session_id, prompt)

        result = None
        async for message in claude_agent_sdk.query(prompt=prompt, options=ClaudeAgentOptions()):
            if isinstance(message, ResultMessage):
                result = message

        if result:
            print(f"  Turn: {result.subtype}, Session: {result.session_id}")

    return session_ids[-1]


async def run_stream_messages():
    """streaming/stream_messages_test.py"""
    session_id = str(uuid.uuid4())
    set_fake_query(session_id, "Write a haiku")

    message_flow = []
    async for message in claude_agent_sdk.query(
        prompt="Write a haiku about programming.",
        options=ClaudeAgentOptions(),
    ):
        message_flow.append(type(message).__name__)

    print(f"  Flow: {' -> '.join(message_flow)}")
    return session_id


async def run_tool_use():
    """tools/tool_use_test.py"""
    session_id = str(uuid.uuid4())
    set_fake_query(session_id, "List Python files", with_tools=True)

    from basic._sdk_runtime import query_for_result

    result = await query_for_result(
        prompt="List the Python files in the current directory.",
        options=ClaudeAgentOptions(),
    )
    print(f"  Result: {result.subtype}, Session: {result.session_id}")
    return session_id


async def run_multi_tool():
    """tools/multi_tool_test.py"""
    session_id = str(uuid.uuid4())
    set_fake_query(session_id, "Find and read Python files", with_tools=True)

    from basic._sdk_runtime import query_for_result

    result = await query_for_result(
        prompt="Find all Python files, read the first one.",
        options=ClaudeAgentOptions(),
    )
    print(f"  Result: {result.subtype}, Session: {result.session_id}")
    return session_id


async def main():
    # Patch query to our dispatch function, then activate instrumentor
    # (which wraps _dispatch_query). We swap the underlying _current_fake
    # per example without needing to re-activate.
    claude_agent_sdk.query = _dispatch_query

    instrumentor = AnthropicAgentsInstrumentor()
    respan = Respan(instrumentations=[instrumentor])

    examples = [
        ("basic/hello_world_test.py", run_hello_world),
        ("basic/wrapped_query_test.py", run_wrapped_query),
        ("sessions/multi_turn_test.py", run_multi_turn),
        ("streaming/stream_messages_test.py", run_stream_messages),
        ("tools/tool_use_test.py", run_tool_use),
        ("tools/multi_tool_test.py", run_multi_tool),
    ]

    results = {}
    for name, fn in examples:
        print(f"\n[{name}]")
        with respan.propagate_attributes(
            customer_identifier="example-test-run",
            metadata={"example": name},
        ):
            session_id = await fn()
            results[name] = session_id

    respan.flush()
    time.sleep(1)

    print(f"\n{'='*60}")
    print(f"All {len(examples)} examples ran successfully!")
    print(f"customer_identifier = example-test-run")
    for name, sid in results.items():
        print(f"  {name}: session={sid}")


if __name__ == "__main__":
    asyncio.run(main())
