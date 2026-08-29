from __future__ import annotations

from _shared import (
    example_attributes,
    finish_respan,
    make_custom_identifier,
    make_mock_sync_client,
    make_respan,
    print_result,
    print_start,
    root_request,
    workflow_name,
)
from respan import workflow

EXAMPLE_NAME = "expected-application-failure"
PROMPT = "Exercise a deterministic Mistral application transport failure."


def _response(_request):
    raise RuntimeError("deterministic Mistral transport failure")


def _build_application_failure_workflow(client):
    @workflow(name=workflow_name(EXAMPLE_NAME))
    def run(request: dict[str, str]) -> None:
        client.chat.complete(
            model=request["model"],
            messages=[{"role": "user", "content": request["prompt"]}],
        )
        raise AssertionError("application failure fixture unexpectedly succeeded")

    return run


def run_expected_application_failure() -> None:
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    result: dict[str, object] = {}

    try:
        with (
            make_mock_sync_client(_response) as client,
            example_attributes(EXAMPLE_NAME, custom_identifier),
        ):
            print_start(EXAMPLE_NAME, custom_identifier, "deterministic-application")
            try:
                _build_application_failure_workflow(client)(
                    root_request(EXAMPLE_NAME, PROMPT, expected_status=500)
                )
            except RuntimeError as exc:
                result = {
                    "expected": True,
                    "error_type": type(exc).__name__,
                    "message": str(exc),
                    "status_code": 500,
                }
    finally:
        finish_respan(respan)

    print_result(
        EXAMPLE_NAME,
        custom_identifier,
        result,
        "deterministic-application",
    )


if __name__ == "__main__":
    run_expected_application_failure()
