"""Shared helpers for MCP tracing examples."""

from __future__ import annotations

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from respan import Respan
from respan_instrumentation_mcp import MCPInstrumentor

EXAMPLE_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXAMPLE_DIR.parents[2]
SERVER_SCRIPT = EXAMPLE_DIR / "server.py"
RESPAN_BASE_URL = "https://api.respan.ai/api"


def load_example_env() -> None:
    load_dotenv(REPO_ROOT / ".env")
    if not os.getenv("RESPAN_API_KEY"):
        raise RuntimeError(f"RESPAN_API_KEY is required in {REPO_ROOT / '.env'}")
    os.environ.setdefault("RESPAN_BASE_URL", RESPAN_BASE_URL)


def create_respan() -> Respan:
    load_example_env()
    return Respan(
        api_key=os.environ["RESPAN_API_KEY"],
        base_url=os.getenv("RESPAN_BASE_URL", RESPAN_BASE_URL),
        instrumentations=[MCPInstrumentor()],
        is_batching_enabled=False,
    )


def workflow_attributes(workflow_name: str) -> dict[str, object]:
    return {
        "trace_group_identifier": workflow_name,
        "custom_identifier": f"{workflow_name}-{uuid4().hex[:8]}",
        "metadata": {
            "example": "mcp",
            "workflow_name": workflow_name,
        },
    }


@asynccontextmanager
async def with_session():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_SCRIPT)],
        cwd=str(EXAMPLE_DIR),
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session
