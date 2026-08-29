from __future__ import annotations

from _shared import (
    example_attributes,
    flush_and_shutdown,
    make_client,
    make_custom_identifier,
    make_respan,
    model_name,
    print_result,
    workflow_name,
)
from ollama import ResponseError
from respan import workflow

EXAMPLE_NAME = "expected-error"


@workflow(name=workflow_name(EXAMPLE_NAME))
def _expected_error_workflow(prompt: str) -> str:
    client = make_client(force_compat_server=True)
    try:
        response = client.chat(
            model=model_name(),
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )
        return str(response)
    finally:
        client.close()


def run_expected_error() -> None:
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    text = ""

    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print(f"custom_identifier={custom_identifier}", flush=True)
            print(f"workflow_name={workflow_name(EXAMPLE_NAME)}", flush=True)
            try:
                _expected_error_workflow("force expected provider error")
            except ResponseError as exc:
                if exc.status_code != 503:
                    raise
                text = f"expected_status={exc.status_code} error={exc.error}"
            else:
                raise AssertionError("The compatibility server should return HTTP 503")
    finally:
        flush_and_shutdown(respan)

    print_result(EXAMPLE_NAME, custom_identifier, text)


if __name__ == "__main__":
    run_expected_error()
