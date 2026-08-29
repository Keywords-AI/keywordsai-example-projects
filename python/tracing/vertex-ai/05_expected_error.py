from __future__ import annotations

from _shared import (
    DeterministicVertexError,
    deterministic_model,
    deterministic_vertex_runtime,
    example_attributes,
    make_respan,
    marker_for,
    workflow_name,
)
from respan import workflow

EXAMPLE_NAME = "expected-error"


@workflow(name=workflow_name(EXAMPLE_NAME))
def expected_error(prompt: str) -> str:
    return deterministic_model().generate_content(prompt).text


def main() -> None:
    marker = marker_for(EXAMPLE_NAME)
    result: dict[str, object] = {}
    with deterministic_vertex_runtime():
        respan = make_respan(EXAMPLE_NAME, marker)
        try:
            with example_attributes(EXAMPLE_NAME, marker):
                try:
                    expected_error("Trigger deterministic provider failure.")
                except DeterministicVertexError as exc:
                    result = {
                        "expected_error": type(exc).__name__,
                        "status_code": exc.status_code,
                    }
                else:
                    raise AssertionError("expected provider error was not raised")
        finally:
            respan.shutdown()
    print({"example": EXAMPLE_NAME, "marker": marker, "result": result}, flush=True)


if __name__ == "__main__":
    main()
