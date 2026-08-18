from __future__ import annotations

from _shared import (
    example_attributes,
    finish_respan,
    make_client,
    make_respan,
    model_name,
    print_result,
    workflow_name,
)
from respan import workflow

EXAMPLE_NAME = "expected-error"


@workflow(name=workflow_name(EXAMPLE_NAME))
def expected_error_workflow(prompt: str) -> None:
    make_client().run(model_name(), input={"prompt": prompt})


def main() -> None:
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = ""
    outcome = ""
    try:
        try:
            with example_attributes(EXAMPLE_NAME) as custom_identifier:
                expected_error_workflow("Expected provider error")
        except Exception as exc:  # noqa: BLE001 - expected real SDK error.
            outcome = f"expected {type(exc).__name__}"
    finally:
        finish_respan(respan)
    print_result(EXAMPLE_NAME, custom_identifier, outcome)


if __name__ == "__main__":
    main()
