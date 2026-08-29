from __future__ import annotations

from _shared import (
    DeterministicWatsonError,
    create_respan,
    deterministic_chat_client,
    deterministic_watson_runtime,
    example_attributes,
    marker_for,
    workflow_name,
)
from respan import workflow

EXAMPLE_NAME = "expected-error"


@workflow(name=workflow_name(EXAMPLE_NAME))
def expected_error(prompt: str) -> dict:
    return deterministic_chat_client().generate_response(input=prompt)


def main() -> None:
    marker = marker_for(EXAMPLE_NAME)
    result: dict[str, object] = {}
    with deterministic_watson_runtime():
        respan = create_respan(EXAMPLE_NAME, marker)
        try:
            with example_attributes(EXAMPLE_NAME, marker):
                try:
                    expected_error("Trigger deterministic provider failure.")
                except DeterministicWatsonError as exc:
                    result = {
                        "expected_error": type(exc).__name__,
                        "status_code": exc.status_code,
                    }
                else:
                    raise AssertionError(
                        "expected Watson provider error was not raised"
                    )
        finally:
            respan.shutdown()
    print({"example": EXAMPLE_NAME, "marker": marker, "result": result}, flush=True)


if __name__ == "__main__":
    main()
