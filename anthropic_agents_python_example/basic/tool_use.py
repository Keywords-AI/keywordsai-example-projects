"""
Tool Use — trace agent tool calls through Respan.

Runs a query that uses Claude Code's built-in tools (Read, Glob, Grep),
then exports the full trace including tool spans.

Setup:
    pip install claude-agent-sdk respan-exporter-anthropic-agents python-dotenv

Run:
    python basic/tool_use.py
"""

from dotenv import load_dotenv

load_dotenv(override=True)

import asyncio
import os
import sys

from claude_agent_sdk import ClaudeAgentOptions

from respan_exporter_anthropic_agents import RespanAnthropicAgentsExporter
from _sdk_runtime import query_for_result

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
    """Run a query that uses tools and see tool spans in traces."""

    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        max_turns=3,
        allowed_tools=["Read", "Glob", "Grep"],
    )

    def _on_message(message):
        msg_type = type(message).__name__
        print(f"  {msg_type}")
    result = await query_for_result(
        exporter=exporter,
        prompt="List the Python files in the current directory. Just show filenames.",
        options=options,
        on_message=_on_message,
    )

    print(f"\nResult: subtype={result.subtype}, turns={result.num_turns}")

    print(f"\nSession: {exporter._last_session_id}")
    print("Check Respan traces to see tool spans (Read, Glob, etc.)")


asyncio.run(main())
