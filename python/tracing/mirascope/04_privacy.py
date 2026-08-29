"""Run a Mirascope call with content capture disabled."""

from __future__ import annotations

import json

from _shared import (
    close_model_provider,
    create_deterministic_model,
    create_respan,
    finish_respan,
    workflow_attributes,
)
from mirascope import llm
from respan import workflow

WORKFLOW_NAME = "mirascope-content-disabled"


def create_runner(model: llm.Model):
    @workflow(name=WORKFLOW_NAME)
    def run_private_call(scenario: str) -> dict[str, object]:
        response = model.call("private-example-content")
        return {
            "capture_content": False,
            "response_received": bool(response.text()),
            "scenario": scenario,
        }

    return run_private_call


def main() -> None:
    respan = create_respan(WORKFLOW_NAME, capture_content=False)
    model: llm.Model | None = None
    try:
        model = create_deterministic_model()
        runner = create_runner(model)
        with respan.propagate_attributes(
            **workflow_attributes(WORKFLOW_NAME, "04_privacy.py")
        ):
            result = runner("content-capture-disabled")
        print(json.dumps(result, sort_keys=True))
    finally:
        try:
            if model is not None:
                close_model_provider(model)
        finally:
            finish_respan(respan)


if __name__ == "__main__":
    main()
