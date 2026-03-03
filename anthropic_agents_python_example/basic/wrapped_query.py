"""
Wrapped Query — the simplest integration pattern.

Uses exporter.query() which handles hooks + tracking automatically.
One line to instrument, zero boilerplate.

Setup:
    pip install claude-agent-sdk respan-exporter-anthropic-agents python-dotenv

Run:
    python basic/wrapped_query.py
"""

from dotenv import load_dotenv

load_dotenv(override=True)

import asyncio
import os
import sys

from claude_agent_sdk import ClaudeAgentOptions

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
    """Use exporter.query() for automatic tracing — simplest pattern."""

    message_types = []

    async for message in exporter.query(
        prompt="Name three primary colors. One word each, comma separated.",
        options=ClaudeAgentOptions(
            permission_mode="bypassPermissions",
            max_turns=1,
        ),
    ):
        msg_type = type(message).__name__
        message_types.append(msg_type)
        print(f"  {msg_type}")

    print(f"\nMessage flow: {' -> '.join(message_types)}")
    print("All traces exported automatically via exporter.query()")


asyncio.run(main())
