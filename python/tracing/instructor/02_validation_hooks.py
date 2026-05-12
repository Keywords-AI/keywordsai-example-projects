"""Use Instructor validation, retries, hooks, and Respan attributes."""

from __future__ import annotations

from typing import Literal
from typing import TypedDict

from instructor.core.hooks import HookName
from respan_tracing import workflow
from respan_tracing.exporters import propagate_attributes

from _respan_instructor import create_respan_instructor_client


class SupportEscalation(TypedDict):
    customer: str
    priority: Literal["low", "medium", "high"]
    sentiment: Literal["positive", "neutral", "negative"]
    follow_up_hours: int
    summary: str


@workflow(name="instructor_example_02_validation_hooks")
def classify_support_escalation(client) -> SupportEscalation:
    return client.create(
        response_model=SupportEscalation,
        max_retries=2,
        messages=[
            {
                "role": "user",
                "content": (
                    "ACME Analytics says production login is failing for "
                    "their security team before a customer audit. They are "
                    "frustrated and need a same-day response."
                ),
            }
        ],
    )


def run_validation_hooks_example() -> None:
    telemetry, client = create_respan_instructor_client(
        app_name="instructor-validation-hooks"
    )
    hook_counts = {"completion_kwargs": 0, "completion_response": 0}

    def on_completion_kwargs(**kwargs) -> None:
        hook_counts["completion_kwargs"] += 1
        print(
            {
                "hook": HookName.COMPLETION_KWARGS.value,
                "model": kwargs.get("model"),
                "tool_count": len(kwargs.get("tools", [])),
            }
        )

    def on_completion_response(_response) -> None:
        hook_counts["completion_response"] += 1

    client.on(HookName.COMPLETION_KWARGS, on_completion_kwargs)
    client.on(HookName.COMPLETION_RESPONSE, on_completion_response)

    try:
        with propagate_attributes(
            customer_identifier="customer_instructor_example",
            thread_identifier="instructor_example_02_validation_hooks",
            metadata={
                "example_script": "02_validation_hooks.py",
                "instructor_api": "create_hooks",
            },
        ):
            escalation = classify_support_escalation(client)
    finally:
        client.off(HookName.COMPLETION_KWARGS, on_completion_kwargs)
        client.off(HookName.COMPLETION_RESPONSE, on_completion_response)

    print(dict(escalation))
    print(hook_counts)
    telemetry.flush()


if __name__ == "__main__":
    run_validation_hooks_example()
