#!/usr/bin/env python3
"""
MCP Server — MCP stdio server integration with tracing.

Demonstrates connecting an OpenAI Agent to an MCP server via stdio,
with @workflow and @task decorators tracing the MCP operations.

Requires: npx installed and a filesystem MCP server available.
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from agents import Agent, Runner
from agents.mcp import MCPServerStdio
from respan_tracing import RespanTelemetry
from respan_tracing.decorators import workflow, task
from respan_tracing.instruments import Instruments

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

telemetry = RespanTelemetry(
    app_name="openai-agents-mcp-server",
    api_key=os.getenv("RESPAN_API_KEY"),
    is_batching_enabled=False,
    block_instruments={Instruments.REQUESTS, Instruments.URLLIB3},
)


@task(name="run_agent_with_mcp")
async def run_agent_with_mcp(agent, prompt):
    """Run the agent with a given prompt inside a traced task."""
    result = await Runner.run(agent, prompt)
    print(result.final_output)
    return result.final_output


@workflow(name="mcp_server_workflow")
async def main_workflow():
    async with MCPServerStdio(
        name="Filesystem Server",
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", os.getcwd()],
        },
    ) as server:
        agent = Agent(
            name="MCP Assistant",
            instructions="You are a helpful assistant with filesystem access. Use tools to list files.",
            mcp_servers=[server],
        )
        await run_agent_with_mcp(agent, "List the files in the current directory.")


async def main():
    try:
        await main_workflow()
    finally:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
