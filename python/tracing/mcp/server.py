"""Local MCP stdio server used by the Respan MCP examples."""

import sys

if "--exit-immediately" in sys.argv:
    raise SystemExit(3)

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.server import Settings

# MCP 1.x with current Pydantic otherwise warns while resolving the generic
# lifespan annotation. Rebuild before FastMCP constructs its Settings instance.
Settings.model_rebuild(force=True)

mcp = FastMCP("respan-mcp-example-server")


@mcp.tool()
def summarize_city(city: str) -> str:
    return (
        f"{city} is ready for a concise travel brief: include weather, "
        "transport, local highlights, and one practical next step."
    )


@mcp.tool()
def calculate_delivery_total(subtotal: float, tax_rate: float = 0.0875) -> str:
    total = subtotal * (1 + tax_rate)
    return f"{total:.2f}"


@mcp.resource("profile://city/paris")
def paris_profile() -> str:
    return (
        "Paris profile: strong public transit, dense museum coverage, "
        "and reliable cafe options near major rail hubs."
    )


@mcp.prompt(name="city_research_prompt")
def city_research_prompt(city: str) -> str:
    return (
        f"Create a compact research brief for {city}. Include current travel "
        "constraints, local context, and three source questions to verify."
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
