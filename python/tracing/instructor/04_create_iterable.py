"""Stream multiple complete objects with Instructor.create_iterable."""

from __future__ import annotations

from typing import Literal
from typing import TypedDict

from respan_tracing import workflow
from respan_tracing.exporters import propagate_attributes

from _respan_instructor import create_respan_instructor_client


class ActionItem(TypedDict):
    owner: str
    task: str
    due: str | None
    status: Literal["new", "blocked", "done"]


@workflow(name="instructor_example_04_create_iterable")
def extract_action_items(client) -> list[ActionItem]:
    return list(
        client.create_iterable(
            response_model=ActionItem,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Extract each action item as a separate object. "
                        "Maya will send the launch checklist by Friday. "
                        "Noah is blocked on legal approval for the DPA. "
                        "Priya already finished the latency dashboard."
                    ),
                }
            ],
        )
    )


def run_create_iterable_example() -> None:
    telemetry, client = create_respan_instructor_client(
        app_name="instructor-create-iterable"
    )

    with propagate_attributes(
        thread_identifier="instructor_example_04_create_iterable",
        metadata={
            "example_script": "04_create_iterable.py",
            "instructor_api": "create_iterable",
        },
    ):
        action_items = extract_action_items(client)

    print([dict(item) for item in action_items])


if __name__ == "__main__":
    run_create_iterable_example()
