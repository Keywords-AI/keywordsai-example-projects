from __future__ import annotations

from _shared import (
    example_attributes,
    make_collections,
    make_custom_identifier,
    make_respan,
    workflow_name,
)
from respan import workflow

EXAMPLE_NAME = "expected-error"


@workflow(name=workflow_name(EXAMPLE_NAME))
def expected_error(collection_name: str) -> None:
    make_collections().delete(collection_name)


def run() -> dict[str, str]:
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    result = {}
    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            try:
                expected_error("missing-collection")
            except RuntimeError as exc:
                result = {"expected_error": type(exc).__name__, "message": str(exc)}
    finally:
        respan.shutdown()
    print(result)
    return result


if __name__ == "__main__":
    run()
