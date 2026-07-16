"""Trace a direct DSPy Tool call."""

from __future__ import annotations

import dspy

from _shared import create_respan, print_result, traced_example


def lookup_order_status(order_id: str) -> str:
    statuses = {
        "ord-1001": "ord-1001 is shipped and arriving tomorrow.",
        "ord-1002": "ord-1002 is waiting for carrier pickup.",
        "ord-1003": "ord-1003 was delivered yesterday.",
    }
    return statuses.get(order_id, f"No status found for {order_id}.")


def run_tool_call_example() -> None:
    context = create_respan(
        app_name="dspy-04-tool-call",
        example_name="04_tool_call",
    )
    tool = dspy.Tool(
        lookup_order_status,
        name="lookup_order_status",
        desc="Look up the shipping status for an order id.",
    )
    order_id = "ord-1001"

    with traced_example(context, input_data={"order_id": order_id}) as span:
        status = tool(order_id=order_id)
        span.set_output({"status": status})

    print_result("Status", status)


if __name__ == "__main__":
    run_tool_call_example()
