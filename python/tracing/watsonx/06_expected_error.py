from __future__ import annotations

from _shared import (
    close_provider,
    example_attributes,
    make_custom_identifier,
    make_model,
    make_respan,
    print_lookup,
    workflow_name,
)
from respan import workflow

EXAMPLE_NAME = "expected-error"
_MODEL = None


@workflow(name=workflow_name(EXAMPLE_NAME))
def _expected_error_workflow(scenario: str) -> None:
    _MODEL.generate_text(prompt=scenario)


def run_expected_error() -> None:
    global _MODEL
    model = make_model(force_offline=True)
    _MODEL = model
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    result = {}
    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            try:
                _expected_error_workflow("RESPAN_EXPECTED_WATSONX_ERROR")
            except RuntimeError as exc:
                result = {"expected_error": type(exc).__name__}
    finally:
        try:
            close_provider(model)
        finally:
            respan.shutdown()
    print_lookup(EXAMPLE_NAME, custom_identifier, result)


if __name__ == "__main__":
    run_expected_error()
