from __future__ import annotations

from _shared import (
    close_client,
    example_attributes,
    finish_respan,
    make_client,
    make_custom_identifier,
    make_respan,
    model_name,
    print_result,
    print_start,
    workflow_name,
)
from respan import workflow

EXAMPLE_NAME = "expected-error"
_CLIENT = None


@workflow(name=workflow_name(EXAMPLE_NAME))
def _expected_error_workflow(prompt: str) -> None:
    _CLIENT.chat.chat(
        model=model_name(),
        messages=[{"role": "user", "content": prompt}],
        max_tokens=16,
    )


def run() -> dict[str, str]:
    global _CLIENT
    respan = make_respan(EXAMPLE_NAME)
    client = make_client()
    _CLIENT = client
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    result = {}
    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print_start(EXAMPLE_NAME, custom_identifier)
            try:
                _expected_error_workflow("RESPAN_EXPECTED_WRITER_ERROR")
            except BaseException as exc:  # noqa: BLE001
                result = {"expected_error": type(exc).__name__}
    finally:
        try:
            close_client(client)
        finally:
            finish_respan(respan)
    print_result("expected error", result)
    return result


if __name__ == "__main__":
    run()
