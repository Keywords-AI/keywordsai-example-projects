"""Tool error."""

from langchain_core.tools import tool

from _shared import flush, init_telemetry, tracing_config


@tool
def failing_lookup(query: str) -> str:
    """Always fail to demonstrate tool error callbacks."""
    raise ValueError(f"no result for {query}")


def tool_error() -> None:
    telemetry = init_telemetry("langchain-tool-error")
    try:
        try:
            failing_lookup.invoke(
                {"query": "missing"},
                config=tracing_config("tool_error"),
            )
        except ValueError as exc:
            print(f"caught: {exc}")
    finally:
        flush(telemetry)


if __name__ == "__main__":
    tool_error()
