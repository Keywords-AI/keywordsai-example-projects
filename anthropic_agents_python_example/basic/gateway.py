"""
Gateway Integration — route through Respan, no Anthropic key needed.

The Respan gateway proxies Claude API calls, so you only need a single
Respan API key for both the LLM call and trace export.

Setup:
    pip install claude-agent-sdk respan-exporter-anthropic-agents python-dotenv

Environment:
    RESPAN_API_KEY=your_key    # only key needed

Run:
    python basic/gateway.py
"""

from dotenv import load_dotenv

load_dotenv(override=True)

import asyncio
import os
import sys

from claude_agent_sdk import ClaudeAgentOptions, ResultMessage

from respan_exporter_anthropic_agents import RespanAnthropicAgentsExporter

API_KEY = os.getenv("RESPAN_API_KEY") or os.getenv("KEYWORDSAI_API_KEY")
BASE_URL = (
    os.getenv("RESPAN_GATEWAY_BASE_URL")
    or os.getenv("RESPAN_BASE_URL")
    or os.getenv("KEYWORDSAI_BASE_URL")
    or "https://api.keywordsai.co/api"
).rstrip("/")

if not API_KEY:
    print("Set RESPAN_API_KEY to run this example")
    sys.exit(1)

exporter = RespanAnthropicAgentsExporter(
    api_key=API_KEY,
    base_url=BASE_URL,
)


async def main():
    """Send a query through the Respan gateway and export traces."""

    print(f"Gateway: {BASE_URL}")
    print(f"API key: {API_KEY[:8]}...\n")

    # Route Claude SDK through the Respan gateway — same key for auth + tracing
    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        max_turns=1,
        env={
            "ANTHROPIC_BASE_URL": BASE_URL,
            "ANTHROPIC_AUTH_TOKEN": API_KEY,
            "ANTHROPIC_API_KEY": API_KEY,
        },
    )

    result = None

    async for message in exporter.query(
        prompt="Reply with exactly: gateway_ok",
        options=options,
    ):
        msg_type = type(message).__name__
        print(f"  {msg_type}")
        if isinstance(message, ResultMessage):
            result = message

    if result:
        print(f"\nResult: subtype={result.subtype}, turns={result.num_turns}")
        if result.usage:
            print(f"Usage: {result.usage}")

    print(f"\nSession: {exporter._last_session_id}")
    print("View trace at: https://platform.keywordsai.co/traces")


asyncio.run(main())
