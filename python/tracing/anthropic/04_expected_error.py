"""Trace an expected Anthropic provider 404 without losing its status."""

from anthropic import NotFoundError
from respan import workflow

from _shared import (
    example_attributes,
    make_client,
    make_respan,
    print_result,
    workflow_name,
)

CASE_ID = "expected_error"
INVALID_MODEL = "respan-intentional-python-anthropic-error-model"


@workflow(name=workflow_name(CASE_ID))
def run_expected_error() -> str:
    try:
        make_client().messages.create(
            model=INVALID_MODEL,
            max_tokens=16,
            messages=[{"role": "user", "content": "This request should fail."}],
        )
    except NotFoundError as exc:
        if exc.status_code != 404:
            raise
        return f"expected provider status={exc.status_code}"
    raise AssertionError("The intentionally invalid model unexpectedly succeeded")


def main() -> None:
    respan = make_respan()
    try:
        with example_attributes(respan, CASE_ID):
            output = run_expected_error()
    finally:
        respan.shutdown()
    print_result(CASE_ID, output)


if __name__ == "__main__":
    main()
