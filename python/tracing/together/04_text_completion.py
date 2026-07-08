from __future__ import annotations

from respan import workflow

from _shared import (
    completion_model_name,
    example_attributes,
    first_text_completion,
    make_client,
    make_custom_identifier,
    make_respan,
    print_result,
    print_start,
    SDK_UNAVAILABLE_ERRORS,
    unavailable_text,
    workflow_name,
)

EXAMPLE_NAME = "text-completion"


@workflow(name=workflow_name(EXAMPLE_NAME))
def _text_completion_workflow(client) -> str:
    try:
        response = client.completions.create(
            model=completion_model_name(),
            prompt="Complete this sentence in under ten words: Tracing AI calls helps",
            max_tokens=40,
            temperature=0,
        )
        return first_text_completion(response)
    except SDK_UNAVAILABLE_ERRORS as exc:
        return unavailable_text("text completions", exc)


def run_text_completion() -> None:
    respan = make_respan(EXAMPLE_NAME)
    client = make_client()
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    text = ""

    try:
        with example_attributes(EXAMPLE_NAME, custom_identifier):
            print_start(EXAMPLE_NAME, custom_identifier)
            text = _text_completion_workflow(client)
    finally:
        respan.flush()
        respan.shutdown()

    print_result(EXAMPLE_NAME, custom_identifier, text)


if __name__ == "__main__":
    run_text_completion()
