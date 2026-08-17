"""Raise a deterministic Mirascope provider error across the workflow boundary."""

from __future__ import annotations

from _shared import (
    close_model_provider,
    create_deterministic_model,
    create_respan,
    finish_respan,
    workflow_attributes,
)
from mirascope import llm
from respan import workflow

WORKFLOW_NAME = "mirascope-expected-provider-error"


def create_runner(model: llm.Model):
    @workflow(name=WORKFLOW_NAME)
    def run_expected_error(prompt: str) -> None:
        model.call(prompt)

    return run_expected_error


def main() -> None:
    respan = create_respan(WORKFLOW_NAME)
    model: llm.Model | None = None
    try:
        model = create_deterministic_model(fail_status=503)
        runner = create_runner(model)
        try:
            with respan.propagate_attributes(
                **workflow_attributes(WORKFLOW_NAME, "03_expected_error.py")
            ):
                runner("Raise the deterministic provider error.")
        except llm.ServerError as exc:
            if exc.status_code != 503:
                raise AssertionError(f"unexpected status: {exc.status_code}") from exc
            print(f"expected failure ({exc.status_code}): {exc}")
        else:
            raise AssertionError("expected deterministic Mirascope failure")
    finally:
        try:
            if model is not None:
                close_model_provider(model)
        finally:
            finish_respan(respan)


if __name__ == "__main__":
    main()
