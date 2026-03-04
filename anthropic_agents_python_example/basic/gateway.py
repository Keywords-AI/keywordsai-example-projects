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

Note:
    The Claude Agent SDK spawns Claude Code as a subprocess. If you have
    custom hooks configured in ~/.claude/settings.json, the subprocess may
    print noisy warnings to stderr. This example suppresses them — the
    query still completes successfully.
"""

from dotenv import load_dotenv

load_dotenv(override=True)

import asyncio
import os
import sys
from typing import Optional

from claude_agent_sdk import ClaudeAgentOptions, ResultMessage
import httpx

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
QUERY_TIMEOUT_SECONDS = int(os.getenv("RESPAN_GATEWAY_QUERY_TIMEOUT_SECONDS", "90"))


def _suppress_stderr():
    """Redirect fd 2 to /dev/null. Returns a restore function."""
    stderr_fd = sys.stderr.fileno()
    saved = os.dup(stderr_fd)
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, stderr_fd)
    os.close(devnull)

    def restore():
        os.dup2(saved, stderr_fd)
        os.close(saved)

    return restore


async def _probe_gateway(gateway_url: str) -> None:
    """Print a minimal diagnostic probe for common gateway failures."""
    probe_url = f"{gateway_url.rstrip('/')}/v1/messages"
    payload = {
        "model": "claude-sonnet-4-5",
        "max_tokens": 8,
        "messages": [{"role": "user", "content": "ping"}],
    }
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                probe_url,
                headers={"x-api-key": API_KEY},
                json=payload,
            )
        body_preview = response.text[:400].replace("\n", " ")
        print(
            f"Gateway probe -> {response.status_code} {response.reason_phrase}: {body_preview}"
        )
    except Exception as exc:
        print(f"Gateway probe failed: {type(exc).__name__}: {exc}")


async def _run_query_with_timeout(
    prompt: str,
    options: ClaudeAgentOptions,
    timeout_seconds: int,
) -> ResultMessage:
    result: Optional[ResultMessage] = None
    try:
        async with asyncio.timeout(timeout_seconds):
            async for message in exporter.query(prompt=prompt, options=options):
                msg_type = type(message).__name__
                print(f"  {msg_type}")
                if isinstance(message, ResultMessage):
                    result = message
    except TimeoutError:
        raise TimeoutError(
            f"Timed out after {timeout_seconds}s waiting for gateway result."
        )
    except Exception:
        # Claude Code subprocess can return non-zero after already delivering result.
        if result is None:
            raise
    if result is None:
        raise RuntimeError("Query completed without a ResultMessage from gateway.")
    return result


async def main():
    """Send a query through the Respan gateway and export traces."""

    print(f"Gateway: {BASE_URL}")
    print(f"API key: {API_KEY[:8]}...\n")

    # The Anthropic SDK appends /v1/messages to ANTHROPIC_BASE_URL,
    # so we point it at the gateway's /anthropic passthrough path.
    # Final URL: {BASE_URL}/anthropic/v1/messages
    gateway_url = f"{BASE_URL}/anthropic"

    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        max_turns=1,
        env={
            "ANTHROPIC_BASE_URL": gateway_url,
            "ANTHROPIC_AUTH_TOKEN": API_KEY,
            "ANTHROPIC_API_KEY": API_KEY,
        },
    )

    result: Optional[ResultMessage] = None

    # The Claude Code subprocess can emit noisy stderr (hook warnings,
    # minified source dumps) that have nothing to do with the query.
    # Suppress them so example output stays clean.
    restore_stderr = _suppress_stderr()

    try:
        result = await _run_query_with_timeout(
            prompt="Reply with exactly: gateway_ok",
            options=options,
            timeout_seconds=QUERY_TIMEOUT_SECONDS,
        )
    except Exception as exc:
        print(f"\nGateway query failed: {type(exc).__name__}: {exc}")
        await _probe_gateway(gateway_url)
        raise
    finally:
        # Let the subprocess finish writing its stderr before we restore,
        # so any remaining noise goes to /dev/null.
        await asyncio.sleep(0.5)
        restore_stderr()

    print(f"\nResult: subtype={result.subtype}, turns={result.num_turns}")
    if result.usage:
        print(f"Usage: {result.usage}")

    print(f"\nSession: {exporter._last_session_id}")
    print("View trace at: https://platform.keywordsai.co/platform/traces")


asyncio.run(main())
