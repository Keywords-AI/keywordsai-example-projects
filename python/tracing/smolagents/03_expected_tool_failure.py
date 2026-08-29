"""Trace a deterministic failing smolagents tool call."""

from _shared import build_respan, example_attributes
from respan import workflow
from smolagents import tool

EXAMPLE_NAME = "expected-tool-failure"
WORKFLOW_NAME = "smolagents_expected_tool_failure_workflow"


@tool
def fail_city_lookup(city: str) -> str:
    """Raise the deterministic failure used by this tracing example.

    Args:
        city: City included in the bounded error message.
    """
    raise RuntimeError(f"No deterministic population fixture for {city}")


@workflow(name=WORKFLOW_NAME)
def execute_expected_failure(city: str) -> None:
    fail_city_lookup(city)


def main() -> None:
    respan = build_respan(EXAMPLE_NAME, WORKFLOW_NAME)
    try:
        with example_attributes(EXAMPLE_NAME, WORKFLOW_NAME):
            try:
                execute_expected_failure("Atlantis")
            except RuntimeError as exc:
                print(f"expected_error={type(exc).__name__}")
    finally:
        respan.shutdown()


if __name__ == "__main__":
    main()
