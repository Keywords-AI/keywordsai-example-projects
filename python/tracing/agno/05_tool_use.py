"""Trace an Agno agent that calls a Python tool."""

from respan import workflow

from _shared import build_agent, create_respan, print_result


def lookup_shipping_status(order_id: str) -> str:
    """Look up the shipping status for an order id."""
    return f"Order {order_id} is packed and ready for pickup."


@workflow(name="agno_05_tool_use")
def run_tool_use() -> str:
    agent = build_agent(
        name="Support Agent",
        instructions="Use tools when order status is requested.",
        tools=[lookup_shipping_status],
    )
    result = agent.run("What is the shipping status for order A-100?")
    return str(result.content)


def tool_use() -> None:
    respan, _ = create_respan(app_name="agno-05-tool-use")
    output = run_tool_use()
    print_result("Agent output", output)


if __name__ == "__main__":
    tool_use()
