"""
Hello World — Anthropic Agent SDK + Respan tracing.

The simplest possible example: ask Claude a question, see the trace in Respan.

Setup:
    pip install claude-agent-sdk respan-exporter-anthropic-agents python-dotenv

Run:
    python basic/hello_world.py
"""

from dotenv import load_dotenv

load_dotenv(override=True)

import asyncio
import os
import sys

from claude_agent_sdk import ClaudeAgentOptions, ResultMessage

from respan_exporter_anthropic_agents import RespanAnthropicAgentsExporter

API_KEY = os.getenv("RESPAN_API_KEY") or os.getenv("KEYWORDSAI_API_KEY")
BASE_URL = os.getenv("RESPAN_BASE_URL") or os.getenv("KEYWORDSAI_BASE_URL")

if not API_KEY:
    print("Set RESPAN_API_KEY to run this example")
    sys.exit(1)

exporter = RespanAnthropicAgentsExporter(
    api_key=API_KEY,
    base_url=BASE_URL,
)


async def main():
    """Ask Claude a simple question and export the trace."""

    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        max_turns=1,
    )

    result_message = None

    async for message in exporter.query(
        prompt="What is 2 + 2? Reply in one word.",
        options=options,
    ):
        if isinstance(message, ResultMessage):
            result_message = message

    print(f"Result: {result_message.subtype if result_message else 'none'}")
    print(f"Session: {exporter._last_session_id}")
    print("View trace at: https://platform.keywordsai.co/traces")


asyncio.run(main())
